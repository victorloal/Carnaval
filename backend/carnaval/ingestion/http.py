"""The HTTP layer: robots, rate limiting, User-Agent and retry.

Every request carries an identifiable User-Agent with contact information
(FR-B-14), waits the source's minimum interval (FR-B-13), and is classified so
only transport-level failures are retried. `robots.txt` is checked before any
content request and never worked around.
"""

from __future__ import annotations

import hashlib
import random
import time
from collections.abc import Callable
from dataclasses import dataclass

import httpx
from django.conf import settings

from carnaval.ingestion import robots
from carnaval.ingestion.exceptions import (
    FetchError,
    PermanentFetchError,
    RobotsDisallowed,
    TransientFetchError,
)
from carnaval.ingestion.models import ScrapeSource


@dataclass(frozen=True)
class FetchedPayload:
    """Exactly what the source said, plus the hash the raw store gates on."""

    url: str
    http_status: int
    content_type: str
    body: bytes
    sha256: str


def default_user_agent() -> str:
    return f"CarnavalPastoSync/1.0 (+contact: {settings.INGESTION_CONTACT_EMAIL})"


def _default_jitter(delay: float) -> float:
    # Jitter spreads retries; it is not a cryptographic use of randomness.
    return random.uniform(0, delay * 0.1)  # noqa: S311


class Fetcher:
    def __init__(
        self,
        source: ScrapeSource,
        *,
        client: httpx.Client,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
        jitter: Callable[[float], float] | None = None,
    ) -> None:
        self.source = source
        self.client = client
        self._sleep: Callable[[float], None] = sleep
        self._monotonic: Callable[[], float] = monotonic
        self._jitter: Callable[[float], float] = jitter or _default_jitter
        self._last_request_at: float | None = None
        self.user_agent = source.user_agent or default_user_agent()

    def _robots_get(self, url: str, user_agent: str) -> tuple[int, str]:
        response = self.client.get(url, headers={"User-Agent": user_agent})
        return response.status_code, response.text

    def _respect_rate_limit(self) -> None:
        if self._last_request_at is not None:
            elapsed = self._monotonic() - self._last_request_at
            wait = self.source.rate_limit_seconds - elapsed
            if wait > 0:
                self._sleep(wait)
        self._last_request_at = self._monotonic()

    def _backoff(self, attempt: int) -> float:
        base = float(settings.INGESTION_RETRY_BASE)
        cap = float(settings.INGESTION_RETRY_CAP)
        delay: float = min(base * (2.0 ** (attempt - 1)), cap)
        return float(delay + self._jitter(delay))

    def fetch(self, url: str | None = None) -> FetchedPayload:
        target = url or self.source.url
        if not robots.is_allowed(
            target,
            self.user_agent,
            get=self._robots_get,
            now=self._monotonic,
        ):
            raise RobotsDisallowed(f"robots.txt disallows {target}")

        attempts = settings.INGESTION_RETRY_ATTEMPTS
        last_error: FetchError | None = None
        for attempt in range(1, attempts + 1):
            self._respect_rate_limit()
            try:
                response = self.client.get(
                    target, headers={"User-Agent": self.user_agent}
                )
            except httpx.HTTPError as exc:  # timeout, connect, DNS, TLS
                last_error = TransientFetchError(str(exc))
            else:
                status = response.status_code
                if 200 <= status < 300:
                    body = response.content
                    return FetchedPayload(
                        url=str(response.url),
                        http_status=status,
                        content_type=response.headers.get("content-type", ""),
                        body=body,
                        sha256=hashlib.sha256(body).hexdigest(),
                    )
                if status == 429:
                    last_error = TransientFetchError(f"HTTP 429 for {target}")
                    retry_after = response.headers.get("Retry-After", "")
                    if retry_after.isdigit():
                        self._sleep(float(retry_after))
                elif 500 <= status < 600:
                    last_error = TransientFetchError(f"HTTP {status} for {target}")
                else:
                    # 4xx other than 429 is permanent: retrying a 404 wastes
                    # requests against a rate-limited source.
                    raise PermanentFetchError(f"HTTP {status} for {target}")

            if attempt < attempts:
                self._sleep(self._backoff(attempt))

        raise last_error or FetchError(f"failed to fetch {target}")
