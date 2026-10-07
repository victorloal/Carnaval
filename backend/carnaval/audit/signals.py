"""Successful and failed logins are both written to `audit_logs` (FR-D-10)."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

from carnaval.audit import services
from carnaval.audit.models import ActorKind


@receiver(user_logged_in)
def on_login(sender: Any, request: Any, user: Any, **kwargs: Any) -> None:
    services.record(
        action="login",
        actor=user,
        actor_kind=ActorKind.HUMAN,
        object_type="user",
        object_id=getattr(user, "pk", None),
        request=request,
    )


@receiver(user_login_failed)
def on_login_failed(
    sender: Any, credentials: dict[str, Any], request: Any = None, **kwargs: Any
) -> None:
    services.record(
        action="login_failed",
        actor_kind=ActorKind.SYSTEM,
        object_type="user",
        changes={"username": credentials.get("username", "")},
        request=request,
    )
