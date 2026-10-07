"""Public submissions: images and video links, always `pending`, always private.

An upload is validated by **content** (magic bytes via Pillow), fully decoded and
re-encoded, and stripped of metadata; a video is a normalised provider + id, never
a raw URL used as an embed `src` (ADR 0007). Nothing here is public until a
reviewer approves it in `carnaval.moderation`.
"""

from __future__ import annotations

import secrets
import uuid
from typing import Any

from django.conf import settings
from django.db import models

from carnaval.core.models import (
    ModeratedModel,
    ModerationOrigin,
    moderation_permissions,
    rejection_reason_constraint,
)


def generate_public_token() -> str:
    return secrets.token_hex(16)


class SubmissionKind(models.TextChoices):
    IMAGE = "image", "Image"
    VIDEO_LINK = "video_link", "Video link"


class VideoProvider(models.TextChoices):
    YOUTUBE = "youtube", "YouTube"
    VIMEO = "vimeo", "Vimeo"


class Submission(ModeratedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    public_token = models.CharField(
        max_length=32, unique=True, default=generate_public_token, editable=False
    )
    kind = models.CharField(max_length=16, choices=SubmissionKind.choices)
    declared_author = models.CharField(max_length=300, blank=True, default="")
    declared_year = models.PositiveIntegerField(null=True, blank=True)
    declared_place = models.CharField(max_length=300, blank=True, default="")
    description_es = models.TextField(blank=True, default="")
    description_en = models.TextField(blank=True, default="")
    video_provider = models.CharField(
        max_length=16, choices=VideoProvider.choices, blank=True, default=""
    )
    video_id = models.CharField(max_length=64, blank=True, default="")
    contact_email = models.EmailField(blank=True, default="")

    class Meta:
        ordering = ["-id"]
        constraints = [rejection_reason_constraint()]
        permissions = moderation_permissions("submission")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.origin = ModerationOrigin.COMMUNITY
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.kind} {self.public_token[:8]}"


class SubmissionFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="files"
    )
    quarantine_key = models.CharField(max_length=1000)
    mime_detected = models.CharField(max_length=100)
    declared_mime = models.CharField(max_length=100, blank=True, default="")
    content_hash = models.CharField(max_length=64, db_index=True)
    byte_size = models.PositiveIntegerField()
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    exif_stripped = models.BooleanField(default=False)
    duplicate_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="duplicates",
    )

    def __str__(self) -> str:
        return self.quarantine_key


class ConsentRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="consents"
    )
    legal_document = models.ForeignKey(
        "legal.LegalDocument",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="consents",
    )
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_hash = models.CharField(max_length=64, blank=True, default="")
    user_agent_hash = models.CharField(max_length=64, blank=True, default="")
    declaration_minor_subject = models.BooleanField(default=False)
    declaration_rights = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"consent {self.submission_id}"


# Kept so the settings module can advertise the cap the form must respect.
MAX_UPLOAD_BYTES = getattr(settings, "SUBMISSION_MAX_UPLOAD_BYTES", 5_000_000)
