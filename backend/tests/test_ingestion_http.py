"""HTTP layer: robots, rate limit, User-Agent, retry (FR-B-13/14, SEC-41/42)."""

from __future__ import annotations

import hashlib
from collections.abc import Callable

import httpx
import pytest
from carnaval.ingestion.exceptions import PermanentFetchError, RobotsDisallowed
from carnaval.ingestion.http import Fetcher
from carnaval.ingestion.models import ScrapeSource
from django.conf import settings

from tests import fixture_data
from tests.factories import ScrapeSourceFactory

pytestmark = pytest.mark.django_db

Handler = Callable[[httpx.Request], httpx.Response]

ROBOTS_OK = "User-agent: *\nAllow: /\n"


class Clock:
    def __init__(self, start: float = 1000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now


def _no_sleep(_seconds: float) -> None:
    return None


def _no_jitter(_delay: float) -> float:
    return 0.0


def _client(handler: Handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def _fetcher(
    source: ScrapeSource,
    handler: Handler,
    *,
    clock: Callable[[], float] | None = None,
    sleep: Callable[[float], None] | None = None,
) -> Fetcher:
    return Fetcher(
        source,
        client=_client(handler),
        sleep=sleep or _no_sleep,
        monotonic=clock or Clock(),
        jitter=_no_jitter,
    )


def _robots_ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, text=ROBOTS_OK, request=request)


def test_user_agent_carries_contact() -> None:
    """SEC-42: the outbound User-Agent identifies us and carries contact info."""
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers["User-Agent"])
        if request.url.path == "/robots.txt":
            return _robots_ok(request)
        return httpx.Response(200, content=b"x", request=request)

    _fetcher(ScrapeSourceFactory(user_agent=""), handler).fetch()

    assert settings.INGESTION_CONTACT_EMAIL in seen[-1]  # noqa: S101


def test_rate_limit_interval_is_observed() -> None:
    """SEC-41: the configured minimum interval is respected between requests."""
    clock = Clock()
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return _robots_ok(request)
        return httpx.Response(200, content=b"x", request=request)

    source = ScrapeSourceFactory(rate_limit_seconds=10, user_agent="t")
    fetcher = _fetcher(source, handler, clock=clock, sleep=sleeps.append)

    fetcher.fetch()
    clock.now += 4.0
    fetcher.fetch()

    assert sleeps == [6.0]  # noqa: S101


def test_transient_failure_is_retried_then_succeeds() -> None:
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return _robots_ok(request)
        calls.append(1)
        if len(calls) < 3:
            return httpx.Response(503, request=request)
        return httpx.Response(200, content=b"ok", request=request)

    payload = _fetcher(ScrapeSourceFactory(user_agent="t"), handler).fetch()

    assert payload.body == b"ok"  # noqa: S101
    assert len(calls) == 3  # noqa: S101


def test_permanent_failure_is_not_retried() -> None:
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return _robots_ok(request)
        calls.append(1)
        return httpx.Response(404, request=request)

    with pytest.raises(PermanentFetchError):
        _fetcher(ScrapeSourceFactory(user_agent="t"), handler).fetch()

    assert len(calls) == 1  # noqa: S101


def test_robots_disallow_stops_before_the_content_request() -> None:
    content_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            text = "User-agent: *\nDisallow: /private\n"
            return httpx.Response(200, text=text, request=request)
        content_paths.append(request.url.path)
        return httpx.Response(200, content=b"x", request=request)

    source = ScrapeSourceFactory(url="https://example.org/private", user_agent="t")
    with pytest.raises(RobotsDisallowed):
        _fetcher(source, handler).fetch()

    assert content_paths == []  # noqa: S101


def test_payload_hash_is_the_sha256_of_the_body() -> None:
    body = b"payload bytes"

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return _robots_ok(request)
        return httpx.Response(200, content=body, request=request)

    payload = _fetcher(ScrapeSourceFactory(user_agent="t"), handler).fetch()

    assert payload.sha256 == hashlib.sha256(body).hexdigest()  # noqa: S101


def test_committed_fixture_hash_matches_its_body() -> None:
    """The fixture's recorded hash is what the pipeline should compute."""
    body, meta = fixture_data.load("carnavaldepasto", "wp_index")

    assert meta["content_hash"] == hashlib.sha256(body).hexdigest()  # noqa: S101
    assert str(meta["url"]).startswith("https://carnavaldepasto.org")  # noqa: S101
