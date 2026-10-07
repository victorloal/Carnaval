"""The moderation verbs (FR-C-03/04/05, `estados.md`).

Every transition writes **three** things in one transaction: the field update, a
`moderation_actions` row, and an `audit_logs` row. Nothing reaches `published`
without passing through here, and the permission is checked on the server.

Approving an `edition` or a `day` publishes its pending children too: an edition
is the aggregate root and is published or withheld as a unit (`modelo-datos.md`
§3.1).
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from carnaval.audit import services as audit
from carnaval.audit.models import ActorKind
from carnaval.core.models import ModerationStatus
from carnaval.moderation.models import ModerationAction, ModerationVerb


def _label(obj: Any) -> str:
    return f"{obj._meta.app_label}.{obj._meta.model_name}"


def _require(actor: Any, perm: str) -> None:
    if not actor.has_perm(perm):
        raise PermissionDenied(f"missing permission {perm}")


def _record(
    obj: Any, verb: str, *, actor: Any, request: Any, reason: str = ""
) -> ModerationAction:
    action = ModerationAction.objects.create(
        subject_type=_label(obj),
        subject_id=obj.pk,
        action=verb,
        actor=actor if getattr(actor, "pk", None) else None,
        reason=reason,
    )
    audit.record(
        action=verb,
        actor=actor if getattr(actor, "pk", None) else None,
        actor_kind=ActorKind.HUMAN if getattr(actor, "pk", None) else ActorKind.SYSTEM,
        object_type=_label(obj),
        object_id=obj.pk,
        changes={"reason": reason} if reason else {},
        request=request,
    )
    return action


def _pending_children(obj: Any) -> list[Any]:
    from carnaval.programme.models import Day, Edition

    if isinstance(obj, Edition):
        days = list(obj.days.filter(status=ModerationStatus.PENDING))
        events = [
            event
            for day in days
            for event in day.events.filter(status=ModerationStatus.PENDING)
        ]
        return [*days, *events]
    if isinstance(obj, Day):
        return list(obj.events.filter(status=ModerationStatus.PENDING))
    return []


@transaction.atomic
def approve(obj: Any, *, actor: Any, request: Any = None) -> list[Any]:
    _require(actor, f"{obj._meta.app_label}.publish_{obj._meta.model_name}")
    targets = [obj, *_pending_children(obj)]
    now = timezone.now()
    for target in targets:
        target.status = ModerationStatus.PUBLISHED
        target.reviewed_by = actor
        target.reviewed_at = now
        target.rejection_reason = ""
        target.staged_changes = None
        target.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "rejection_reason",
                "staged_changes",
            ]
        )
        _record(target, ModerationVerb.APPROVE, actor=actor, request=request)
    return targets


@transaction.atomic
def reject(
    obj: Any, *, actor: Any, reason: str, request: Any = None
) -> ModerationAction:
    _require(actor, f"{obj._meta.app_label}.reject_{obj._meta.model_name}")
    if not reason.strip():
        raise ValueError("a rejection requires a reason")
    obj.status = ModerationStatus.REJECTED
    obj.rejection_reason = reason.strip()
    obj.reviewed_by = actor
    obj.reviewed_at = timezone.now()
    obj.staged_changes = None
    obj.save(
        update_fields=[
            "status",
            "rejection_reason",
            "reviewed_by",
            "reviewed_at",
            "staged_changes",
        ]
    )
    return _record(
        obj, ModerationVerb.REJECT, actor=actor, request=request, reason=reason
    )


@transaction.atomic
def unpublish(obj: Any, *, actor: Any, request: Any = None) -> ModerationAction:
    _require(actor, f"{obj._meta.app_label}.unpublish_{obj._meta.model_name}")
    obj.status = ModerationStatus.PENDING
    obj.save(update_fields=["status"])
    return _record(obj, ModerationVerb.WITHDRAW, actor=actor, request=request)


@transaction.atomic
def request_changes(
    obj: Any, *, actor: Any, reason: str = "", request: Any = None
) -> ModerationAction:
    _require(actor, f"{obj._meta.app_label}.request_changes_{obj._meta.model_name}")
    return _record(
        obj, ModerationVerb.REQUEST_CHANGES, actor=actor, request=request, reason=reason
    )


@transaction.atomic
def apply_proposal(obj: Any, *, actor: Any, request: Any = None) -> bool:
    """Apply a `staged_changes` proposal to a published row (§5.1).

    This is the only path that writes a published row, and it writes a
    moderation action and an audit row for it.
    """
    _require(actor, f"{obj._meta.app_label}.publish_{obj._meta.model_name}")
    proposed = obj.staged_changes
    if not proposed:
        return False
    field_names = [name for name in proposed if name != "ingestion_run"]
    for name in field_names:
        setattr(obj, name, proposed[name])
    obj.staged_changes = None
    obj.reviewed_by = actor
    obj.reviewed_at = timezone.now()
    obj.save(
        update_fields=[*field_names, "staged_changes", "reviewed_by", "reviewed_at"]
    )
    _record(
        obj,
        ModerationVerb.APPROVE,
        actor=actor,
        request=request,
        reason="staged change",
    )
    return True
