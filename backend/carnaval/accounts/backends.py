"""The authentication backend, with login throttling in front of it (SEC-06)."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest

from carnaval.accounts import privacy, throttle


class ThrottledModelBackend(ModelBackend):
    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> Any:
        ip_hash = privacy.hash_ip(request.META.get("REMOTE_ADDR") if request else None)

        if username and throttle.is_locked(username, ip_hash):
            # Do not even hash the password while locked: it bounds the work an
            # attacker can force and gives the same answer as a wrong password.
            return None

        user = super().authenticate(
            request, username=username, password=password, **kwargs
        )

        if username:
            if user is None:
                throttle.record_failure(username, ip_hash)
            else:
                throttle.reset(username, ip_hash)
        return user
