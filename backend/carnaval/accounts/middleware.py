"""Middleware: request context, the absolute session cap, TOTP for admins, and
`noindex` on the console.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone, translation

from carnaval.accounts import privacy

_OTP_EXEMPT_PREFIXES = (
    "/admin/login/",
    "/admin/logout/",
    "/admin/password_change/",
    "/accounts/step-up/",
    "/static/",
)


class RequestContextMiddleware:
    """Attach a correlation id and a salted IP hash to every request."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.request_id = uuid.uuid4().hex  # type: ignore[attr-defined]
        request.ip_hash = privacy.hash_ip(  # type: ignore[attr-defined]
            request.META.get("REMOTE_ADDR")
        )
        return self.get_response(request)


class AbsoluteSessionMiddleware:
    """End a session 72 h after authentication, however active it has been."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            started = request.session.get("auth_time")
            if (
                started
                and timezone.now().timestamp() - started > settings.SESSION_ABSOLUTE_AGE
            ):
                logout(request)
        return self.get_response(request)


class AdminTOTPRequiredMiddleware:
    """An `admin`-group user must complete a second factor to use the console."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        if (
            user is not None
            and user.is_authenticated
            and request.path.startswith("/admin/")
            and not request.path.startswith(_OTP_EXEMPT_PREFIXES)
            and user.groups.filter(name="admin").exists()
            and not _is_verified(request)
        ):
            return redirect("/accounts/step-up/")
        return self.get_response(request)


class NoIndexAdminMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if request.path.startswith("/admin/"):
            response["X-Robots-Tag"] = "noindex, nofollow"
        return response


class AdminLocaleMiddleware:
    """The admin is Spanish only (FR-H-08) while the API surface stays English."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.path.startswith(("/admin/", "/accounts/")):
            translation.activate("es")
        return self.get_response(request)


def _is_verified(request: HttpRequest) -> bool:
    user = request.user
    is_verified = getattr(user, "is_verified", None)
    return bool(is_verified()) if callable(is_verified) else False
