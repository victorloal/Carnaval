from __future__ import annotations

import uuid

from django.db import models


class SourceType(models.TextChoices):
    WP_API = "wp_api", "WordPress REST API"
    HTML = "html", "HTML"
    PDF = "pdf", "PDF"


class IngestionTrigger(models.TextChoices):
    CRON = "cron", "Scheduled"
    MANUAL = "manual", "Manual"
    ADMIN = "admin", "Admin"


class IngestionStatus(models.TextChoices):
    RUNNING = "running", "Running"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    SKIPPED = "skipped", "Skipped"


class ScrapeSource(models.Model):
    """A configured ingestion target and its circuit-breaker state.

    ``modelo-datos.md`` §3.5. Editable from Django admin in v1; the extractor
    (Sprint 03) is the only writer of the failure counters.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=2000)
    source_type = models.CharField(max_length=16, choices=SourceType.choices)
    wp_object_type = models.CharField(max_length=100, blank=True, default="")
    wp_object_id = models.CharField(max_length=100, blank=True, default="")
    # Per-section CSS selectors for html sources; ``{}`` for wp_api/pdf.
    selectors = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    # Minimum seconds between requests (FR-B-13), raised to the source's
    # Crawl-delay where one exists.
    rate_limit_seconds = models.PositiveIntegerField(default=60)
    schedule_cron = models.CharField(max_length=100, blank=True, default="")
    consecutive_failures = models.PositiveIntegerField(default=0)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default="")
    # FR-B-14: must be identifiable and carry contact information.
    user_agent = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class RawDocument(models.Model):
    """The RAW STORE — one row per successfully fetched payload.

    ``content_hash`` unique is what makes re-running a source idempotent
    (FR-B-03): a fetch whose hash already exists is a no-op, never reprocessed.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scrape_source = models.ForeignKey(
        ScrapeSource, on_delete=models.PROTECT, related_name="raw_documents"
    )
    url = models.URLField(max_length=2000)
    http_status = models.PositiveSmallIntegerField()
    content_type = models.CharField(max_length=200, blank=True, default="")
    # SHA-256 of the raw bytes. Unique is the idempotency gate.
    content_hash = models.CharField(max_length=64, unique=True)
    byte_size = models.PositiveBigIntegerField()
    # Object-storage key; the payload itself is never committed (FR-B-19).
    storage_key = models.CharField(max_length=1000)
    fetched_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fetched_at"]

    def __str__(self) -> str:
        return self.content_hash


class IngestionRun(models.Model):
    """One execution of the pipeline (``modelo-datos.md`` §3.7, FR-B-08)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Null for a manual run that is not bound to a single source.
    scrape_source = models.ForeignKey(
        ScrapeSource,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="runs",
    )
    trigger = models.CharField(max_length=16, choices=IngestionTrigger.choices)
    status = models.CharField(
        max_length=16, choices=IngestionStatus.choices, default=IngestionStatus.RUNNING
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    # {extracted, inserted, updated, skipped, rejected}
    stats = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.trigger} {self.status} @ {self.started_at:%Y-%m-%d %H:%M}"
