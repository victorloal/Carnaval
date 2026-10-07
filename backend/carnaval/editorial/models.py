"""v2 editorial content: the citation registry, news, media and settings.

`media_assets` is the highest-risk table in the schema; every column that makes
an image lawfully publishable is a `CHECK` constraint, and `publish_blockers()`
is the single source of truth the moderation service consults before publishing.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from carnaval.core.models import (
    ModeratedModel,
    moderation_permissions,
    rejection_reason_constraint,
)


class SourceKind(models.TextChoices):
    OFFICIAL_SITE = "official_site", "Official site"
    NEWS_OUTLET = "news_outlet", "News outlet"
    ARCHIVE = "archive", "Archive"
    PDF = "pdf", "PDF"
    OTHER = "other", "Other"


class RightsStatus(models.TextChoices):
    UNKNOWN = "unknown", "Unknown"
    PERMITTED = "permitted", "Permitted"
    LICENSED = "licensed", "Licensed"
    PUBLIC_DOMAIN = "public_domain", "Public domain"
    PERMISSION_ON_FILE = "permission_on_file", "Permission on file"


class SettingValueType(models.TextChoices):
    STRING = "string", "String"
    INT = "int", "Int"
    BOOL = "bool", "Bool"
    JSON = "json", "JSON"


class Source(models.Model):
    """The citation registry — not a fetch target (`modelo-datos.md` §4.3)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    kind = models.CharField(max_length=32, choices=SourceKind.choices)
    url = models.URLField(max_length=2000, blank=True, default="")
    is_official = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class NewsItem(ModeratedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        Source,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="news_items",
    )
    headline = models.CharField(max_length=300)
    url = models.URLField(max_length=2000, unique=True)
    outlet = models.CharField(max_length=200, blank=True, default="")
    published_on = models.DateField(null=True, blank=True)
    # A short **original** summary, never the article body (FR-E-02, LEG-04).
    summary_es = models.TextField(blank=True, default="")
    summary_en = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-published_on", "headline"]
        constraints = [rejection_reason_constraint()]
        permissions = moderation_permissions("newsitem")

    def __str__(self) -> str:
        return self.headline


class MediaAsset(ModeratedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edition = models.ForeignKey(
        "programme.Edition",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="media_assets",
    )
    file = models.CharField(max_length=1000, blank=True, default="")
    quarantine_file = models.CharField(max_length=1000, blank=True, default="")
    content_hash = models.CharField(
        max_length=64, blank=True, default="", db_index=True
    )
    year_approx = models.PositiveIntegerField(null=True, blank=True)
    title_es = models.CharField(max_length=300)
    title_en = models.CharField(max_length=300, blank=True, default="")
    description_es = models.TextField(blank=True, default="")
    description_en = models.TextField(blank=True, default="")
    author = models.CharField(max_length=300, blank=True, default="")
    source_ref = models.CharField(max_length=300, blank=True, default="")
    license = models.CharField(max_length=200, blank=True, default="")
    citation_text = models.TextField(blank=True, default="")
    rights_status = models.CharField(
        max_length=32, choices=RightsStatus.choices, default=RightsStatus.UNKNOWN
    )
    exif_stripped = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    minor_subject = models.BooleanField(default=False)
    guardian_consent_on_file = models.BooleanField(default=False)

    class Meta:
        ordering = ["-year_approx", "title_es"]
        constraints = [
            rejection_reason_constraint(),
            # An unknown-rights or uncited image cannot be published (LEG-02).
            models.CheckConstraint(
                condition=~models.Q(status="published")
                | (
                    ~models.Q(rights_status="unknown")
                    & ~models.Q(author="")
                    & ~models.Q(source_ref="")
                    & ~models.Q(citation_text="")
                    & models.Q(exif_stripped=True)
                ),
                name="media_publishable_requires_rights",
            ),
            # A minor cannot be published without guardian consent (LEG-09).
            models.CheckConstraint(
                condition=~models.Q(status="published")
                | ~models.Q(minor_subject=True)
                | models.Q(guardian_consent_on_file=True),
                name="media_minor_requires_consent",
            ),
        ]
        permissions = moderation_permissions("mediaasset")

    def publish_blockers(self) -> list[str]:
        reasons: list[str] = []
        if self.rights_status == RightsStatus.UNKNOWN:
            reasons.append("rights_status is unknown")
        if not self.author:
            reasons.append("author is missing")
        if not self.source_ref:
            reasons.append("source is missing")
        if not self.citation_text:
            reasons.append("citation text is missing")
        if not self.exif_stripped:
            reasons.append("EXIF has not been stripped")
        if self.minor_subject and not self.guardian_consent_on_file:
            reasons.append("guardian consent is missing for a minor subject")
        return reasons

    def __str__(self) -> str:
        return self.title_es


class SiteSetting(models.Model):
    key = models.CharField(max_length=200, primary_key=True)
    value = models.JSONField(default=dict, blank=True)
    value_type = models.CharField(
        max_length=16, choices=SettingValueType.choices, default=SettingValueType.STRING
    )
    description = models.CharField(max_length=300, blank=True, default="")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def clean(self) -> None:
        lowered = self.key.lower()
        if any(
            word in lowered
            for word in ("secret", "password", "token", "credential", "api_key")
        ):
            from django.core.exceptions import ValidationError

            raise ValidationError(
                "Secrets belong in environment variables, not site_settings (FR-E-11)."
            )

    def __str__(self) -> str:  # noqa: DJ012
        return self.key
