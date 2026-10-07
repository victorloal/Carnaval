"""Versioned legal documents and the takedown register (FR-G-01…07).

A current legal version is **never edited in place**; a change is a new version,
so an old `ConsentRecord` remains interpretable (FR-G-02, PRV-05).
"""

from __future__ import annotations

import uuid
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class LegalDocType(models.TextChoices):
    TERMS = "terms", "Terms"
    PRIVACY = "privacy", "Privacy"
    CONTENT_POLICY = "content_policy", "Content policy"
    TAKEDOWN = "takedown", "Takedown"


class ClaimType(models.TextChoices):
    COPYRIGHT = "copyright", "Copyright"
    PRIVACY = "privacy", "Privacy"
    ILLEGAL_CONTENT = "illegal_content", "Illegal content"
    OTHER = "other", "Other"


class TakedownStatus(models.TextChoices):
    RECEIVED = "received", "Received"
    IN_REVIEW = "in_review", "In review"
    ACTIONED = "actioned", "Actioned"
    REJECTED = "rejected", "Rejected"
    ESCALATED = "escalated", "Escalated"


class LegalDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doc_type = models.CharField(max_length=32, choices=LegalDocType.choices)
    version = models.CharField(max_length=16)
    locale = models.CharField(max_length=2)
    body = models.TextField(blank=True, default="")
    effective_from = models.DateTimeField(default=timezone.now)
    is_current = models.BooleanField(default=True)

    class Meta:
        ordering = ["doc_type", "-effective_from"]
        constraints = [
            models.UniqueConstraint(
                fields=["doc_type", "locale"],
                condition=models.Q(is_current=True),
                name="legal_one_current_per_type_locale",
            )
        ]

    @classmethod
    def current(cls, doc_type: str, locale: str) -> LegalDocument | None:
        return cls.objects.filter(
            doc_type=doc_type, locale=locale, is_current=True
        ).first()

    def save(self, *args: Any, **kwargs: Any) -> None:  # noqa: DJ012
        if not self._state.adding:
            previous = LegalDocument.objects.filter(pk=self.pk).first()
            if previous is not None and previous.is_current:
                raise ValidationError(
                    "a current legal version is never edited in place; make a new one"
                )
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # noqa: DJ012
        return f"{self.doc_type} {self.version} ({self.locale})"


class TakedownRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject_type = models.CharField(max_length=100, blank=True, default="")
    subject_id = models.UUIDField(null=True, blank=True)
    requester_name = models.CharField(max_length=300, blank=True, default="")
    requester_email = models.EmailField()
    claim_type = models.CharField(max_length=32, choices=ClaimType.choices)
    evidence_url = models.URLField(max_length=2000, blank=True, default="")
    received_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=16, choices=TakedownStatus.choices, default=TakedownStatus.RECEIVED
    )
    action_taken = models.TextField(blank=True, default="")
    responded_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-received_at"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        # An illegal-content claim is escalated and never closed by a note alone.
        if self.claim_type == ClaimType.ILLEGAL_CONTENT and self.status in {
            TakedownStatus.RECEIVED,
            TakedownStatus.IN_REVIEW,
        }:
            self.status = TakedownStatus.ESCALATED
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # noqa: DJ012
        return f"{self.claim_type} {self.status}"
