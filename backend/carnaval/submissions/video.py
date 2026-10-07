"""Video links: an allowlist of providers, normalised to provider + id.

A video is never uploaded, and the submitted URL is never used as an embed
`src` (ADR 0007, FR-F-19).
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

from carnaval.submissions.models import VideoProvider

_YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
_VIMEO_HOSTS = {"vimeo.com", "www.vimeo.com"}
_YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
_VIMEO_ID = re.compile(r"^\d+$")


def normalise_video(url: str) -> tuple[str, str] | None:
    """Return ``(provider, video_id)`` or ``None`` if the host is not allowed."""
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    if not path:
        return None

    if host in _YOUTUBE_HOSTS:
        if host == "youtu.be":
            candidate = path.split("/")[0]
        else:
            parts = path.split("/")
            if parts[0] == "watch":
                candidate = parse_qs(parsed.query).get("v", [""])[0]
            elif parts[0] in {"embed", "shorts", "live"} and len(parts) > 1:
                candidate = parts[1]
            else:
                candidate = parts[0]
        if _YOUTUBE_ID.match(candidate):
            return VideoProvider.YOUTUBE, candidate
        return None

    if host in _VIMEO_HOSTS:
        candidate = path.split("/")[0]
        if _VIMEO_ID.match(candidate):
            return VideoProvider.VIMEO, candidate
        return None

    return None
