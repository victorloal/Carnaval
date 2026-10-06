from __future__ import annotations

from django.conf import settings
from django.db import models


class ModerationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PUBLISHED = "published", "Published"
    REJECTED = "rejected", "Rejected"


class ModerationOrigin(models.TextChoices):
    SCRAPED = "scraped", "Scraped"
    MANUAL = "manual", "Manual"
    COMMUNITY = "community", "Community"


class ModeratedModel(models.Model):
    """Abstract base for every table whose content passes through review.

    This is the moderation mixin of ``docs/02-diseno/modelo-datos.md`` §2 and
    ``estados.md`` §1: nothing reaches ``published`` without a human decision,
    and every record keeps its ``origin``.

    Two pieces are deliberately not here yet. ``ingestion_run`` (FK to
    ``ingestion_runs``) cannot exist before that table does, and the
    "``scraped`` requires a run / ``manual`` requires an author" constraints
    arrive with the moderation service rather than as a half-enforced rule now.
    """

    status = models.CharField(
        max_length=16,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
        db_index=True,
    )
    origin = models.CharField(
        max_length=16,
        choices=ModerationOrigin.choices,
        default=ModerationOrigin.MANUAL,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        abstract = True

    @property
    def is_published(self) -> bool:
        """Derived from ``status``; there is no independently settable flag."""
        return self.status == ModerationStatus.PUBLISHED


def rejection_reason_constraint() -> models.CheckConstraint:
    """A rejection is always explained (modelo-datos.md §2 / §9).

    ``Meta.constraints`` is not inherited from an abstract base, so every
    moderated model composes this into its own ``Meta.constraints``.
    """
    return models.CheckConstraint(
        condition=~models.Q(status=ModerationStatus.REJECTED)
        | ~models.Q(rejection_reason=""),
        name="%(app_label)s_%(class)s_rejection_reason_required",
    )
