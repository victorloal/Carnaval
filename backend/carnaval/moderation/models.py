"""The append-only decision log (`modelo-datos.md` §6.5, FR-C-07).

Separate from `audit_logs` because it is the evidence trail for a rights or
takedown dispute. Append-only is enforced the same way: no update, no delete,
and no add/change/delete permission exists.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ModerationVerb(models.TextChoices):
    SUBMIT = "submit", "Submit"
    APPROVE = "approve", "Approve"
    REJECT = "reject", "Reject"
    REQUEST_CHANGES = "request_changes", "Request changes"
    WITHDRAW = "withdraw", "Withdraw"


class ModerationActionQuerySet(models.QuerySet["ModerationAction"]):
    def update(self, **kwargs: Any) -> int:
        raise ValidationError("moderation_actions is append-only")

    def delete(self) -> tuple[int, dict[str, int]]:
        raise ValidationError("moderation_actions is append-only")


class ModerationAction(models.Model):
    subject_type = models.CharField(max_length=100)
    subject_id = models.UUIDField()
    action = models.CharField(max_length=32, choices=ModerationVerb.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    reason = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = ModerationActionQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        default_permissions = ("view",)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk is not None:
            raise ValidationError("moderation_actions is append-only")
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("moderation_actions is append-only")

    def __str__(self) -> str:  # noqa: DJ012
        return f"{self.action} {self.subject_type}:{self.subject_id}"
