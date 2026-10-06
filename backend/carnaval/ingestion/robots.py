"""robots.txt, cached per host and honoured before any content request.

A 403 on ``robots.txt`` means disallow-all; any other 4xx means allow-all (a
missing robots.txt is not a restriction). A refusal is never worked around: the
caller disables the source and flags it for human review.
"""

from __future__ import annotations

import time
import urllib.robotparser
from collections.abc import Callable
from urllib.parse import urlparse

from django.conf import settings

_Get = Callable[[str, str], tuple[int, str]]

# origin -> (fetched_at, parser). Process-local; a fresh run re-reads at most
# once per host per TTL.
_CACHE: dict[str, tuple[float, urllib.robotparser.RobotFileParser]] = {}


def clear_cache() -> None:
    """Drop the cache. Used by tests and by a long-lived process on demand."""
    _CACHE.clear()


def _origin(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _parser_for(
    url: str,
    user_agent: str,
    get: _Get,
    now: Callable[[], float],
    ttl: int,
) -> urllib.robotparser.RobotFileParser:
    origin = _origin(url)
    cached = _CACHE.get(origin)
    if cached is not None and now() - cached[0] < ttl:
        return cached[1]

    status, text = get(f"{origin}/robots.txt", user_agent)
    parser = urllib.robotparser.RobotFileParser()
    if status == 403:
        # A 403 on robots.txt means disallow-all.
        parser.parse(["User-agent: *", "Disallow: /"])
    elif status >= 400:
        # Any other 4xx means the file is missing: no restriction.
        parser.parse(["User-agent: *", "Disallow:"])
    else:
        parser.parse(text.splitlines())

    _CACHE[origin] = (now(), parser)
    return parser


def is_allowed(
    url: str,
    user_agent: str,
    *,
    get: _Get,
    now: Callable[[], float] = time.monotonic,
    ttl: int | None = None,
) -> bool:
    ttl = settings.INGESTION_ROBOTS_CACHE_SECONDS if ttl is None else ttl
    parser = _parser_for(url, user_agent, get, now, ttl)
    return parser.can_fetch(user_agent, url)
