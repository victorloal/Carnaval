from __future__ import annotations

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
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

    One piece is still deliberately absent: the "``scraped`` requires a run /
    ``manual`` requires an author" constraints arrive with the moderation
    service rather than as a half-enforced rule now.
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
    # Set when origin = scraped (modelo-datos.md §2, FR-B-06). String reference
    # so core does not import the ingestion app at module load.
    ingestion_run = models.ForeignKey(
        "ingestion.IngestionRun",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    # A proposed change to an already-published row (`flujo-datos.md` §5.1). The
    # pipeline writes it; a reviewer applies or discards it. The published
    # fields themselves are never touched by the pipeline.
    staged_changes = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)

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


_MODERATION_VERBS = (
    ("publish", "Can publish {name}"),
    ("reject", "Can reject {name}"),
    ("unpublish", "Can unpublish {name}"),
    ("request_changes", "Can request changes to {name}"),
)


def moderation_permissions(model_name: str) -> tuple[tuple[str, str], ...]:
    """The custom permissions of `roles-permisos.md` §3, rows 4–7.

    ``Meta.permissions`` is not inherited from an abstract base either, so each
    moderated model composes this into its own ``Meta.permissions``. A tuple is
    returned because ``tuple`` is covariant and ``list`` is not.
    """
    return tuple(
        (f"{verb}_{model_name}", label.format(name=model_name))
        for verb, label in _MODERATION_VERBS
    )
