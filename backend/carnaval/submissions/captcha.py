"""CAPTCHA verification (FR-F-17, SEC-14).

Cloudflare Turnstile. It is **off by default** so development and the tests need
no keys; production must set `SUBMISSION_CAPTCHA_ENABLED=true` and provide the
secret. The honeypot and the quotas are always active, so the submission path is
never unprotected even when the CAPTCHA is disabled.
"""

from __future__ import annotations

import httpx
from django.conf import settings

_SITEVERIFY = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify(token: str, remote_ip: str | None) -> bool:
    if not settings.SUBMISSION_CAPTCHA_ENABLED:
        return True
    if not token:
        return False
    try:
        response = httpx.post(
            _SITEVERIFY,
            data={
                "secret": settings.SUBMISSION_CAPTCHA_SECRET,
                "response": token,
                "remoteip": remote_ip or "",
            },
            timeout=10,
        )
        return bool(response.json().get("success"))
    except (httpx.HTTPError, ValueError):
        return False
