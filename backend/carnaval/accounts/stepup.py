"""Step-up re-authentication (FR-D-16, ADR 0013).

Before publishing, changing roles, editing site settings or a legal action, the
session must re-enter the password **and** a TOTP token, even if it is already
active. The state is a timestamp in the session, valid for
`STEPUP_AGE_SECONDS`.
"""

from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone

SESSION_KEY = "stepup_at"


def mark(request: HttpRequest) -> None:
    request.session[SESSION_KEY] = timezone.now().timestamp()


def seconds_remaining(request: HttpRequest) -> float:
    started = request.session.get(SESSION_KEY)
    if not started:
        return 0.0
    age = timezone.now().timestamp() - float(started)
    return max(0.0, float(settings.STEPUP_AGE_SECONDS) - age)


def is_stepped_up(request: HttpRequest) -> bool:
    return seconds_remaining(request) > 0
