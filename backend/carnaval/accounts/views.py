"""The step-up page: password plus a TOTP token, then back to where you were."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from carnaval.accounts import stepup

_SAFE_NEXT_PREFIXES = ("/admin/", "/accounts/")


def _safe_next(value: str | None) -> str:
    if value and value.startswith(_SAFE_NEXT_PREFIXES):
        return value
    return "/admin/"


def step_up(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("/admin/login/")

    next_url = _safe_next(request.GET.get("next"))
    error = ""

    if request.method == "POST":
        next_url = _safe_next(request.POST.get("next"))
        password = request.POST.get("password", "")
        token = request.POST.get("token", "")
        user = authenticate(
            request, username=request.user.get_username(), password=password
        )
        if user is not None and _token_is_valid(user, token):
            stepup.mark(request)
            return redirect(next_url)
        error = "Password or token is not correct."

    return render(request, "accounts/step_up.html", {"next": next_url, "error": error})


def _token_is_valid(user: Any, token: str) -> bool:
    if not token:
        return False
    from django_otp import match_token

    return match_token(user, token) is not None
