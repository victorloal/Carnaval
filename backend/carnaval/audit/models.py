"""The project-wide audit trail (`modelo-datos.md` §5.1, FR-D-08).

Append-only is enforced in the application here: no update, no delete, and no
`add`/`change`/`delete` permission is even created (`default_permissions`).
The PostgreSQL trigger that makes it true at the database level is deliberately
**not** written until a PostgreSQL service exists in CI — an unrun trigger is
not a guarantee, and this is recorded rather than pretended.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ActorKind(models.TextChoices):
    HUMAN = "human", "Human"
    PIPELINE = "pipeline", "Pipeline"
    SYSTEM = "system", "System"


class AuditLogQuerySet(models.QuerySet["AuditLog"]):
    def update(self, **kwargs: Any) -> int:
        raise ValidationError("audit_logs is append-only")

    def delete(self) -> tuple[int, dict[str, int]]:
        raise ValidationError("audit_logs is append-only")


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    actor_kind = models.CharField(
        max_length=16, choices=ActorKind.choices, default=ActorKind.SYSTEM
    )
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100, blank=True, default="")
    object_id = models.UUIDField(null=True, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_hash = models.CharField(max_length=64, blank=True, default="")
    request_id = models.CharField(max_length=36, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = AuditLogQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        # No add/change/delete permission is created at all (FR-D-09).
        default_permissions = ("view",)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk is not None:
            raise ValidationError("audit_logs is append-only")
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("audit_logs is append-only")

    def __str__(self) -> str:  # noqa: DJ012
        return f"{self.action} @ {self.created_at:%Y-%m-%d %H:%M}"
