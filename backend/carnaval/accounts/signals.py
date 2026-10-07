"""Stamp the authentication time so the absolute session cap can be enforced."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone


@receiver(user_logged_in)
def stamp_auth_time(sender: Any, request: Any, user: Any, **kwargs: Any) -> None:
    if request is not None and hasattr(request, "session"):
        request.session["auth_time"] = timezone.now().timestamp()
