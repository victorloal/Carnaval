"""How the rest of the project writes an audit row."""

from __future__ import annotations

from typing import Any

from carnaval.audit.models import ActorKind, AuditLog


def record(
    *,
    action: str,
    actor: Any = None,
    actor_kind: str = ActorKind.SYSTEM,
    object_type: str = "",
    object_id: Any = None,
    changes: dict[str, Any] | None = None,
    request: Any = None,
) -> AuditLog:
    return AuditLog.objects.create(
        actor=actor,
        actor_kind=actor_kind,
        action=action,
        object_type=object_type,
        object_id=object_id,
        changes=changes or {},
        ip_hash=getattr(request, "ip_hash", "") or "",
        request_id=getattr(request, "request_id", "") or "",
    )
