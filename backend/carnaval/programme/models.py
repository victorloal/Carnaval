from __future__ import annotations

import uuid

from django.db import models

from carnaval.core.models import (
    ModeratedModel,
    moderation_permissions,
    rejection_reason_constraint,
)


class Edition(ModeratedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.PositiveIntegerField(unique=True)
    slug = models.SlugField(unique=True, max_length=200)
    title_es = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True, default="")
    starts_on = models.DateField(blank=True, null=True)
    ends_on = models.DateField(blank=True, null=True)
    summary_es = models.TextField(blank=True, default="")
    summary_en = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["year"]
        constraints = [rejection_reason_constraint()]
        permissions = moderation_permissions("edition")

    def __str__(self) -> str:
        return f"{self.year} - {self.title_es}"


class Day(ModeratedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="days")
    date = models.DateField()
    slug = models.SlugField(max_length=200)
    label_es = models.CharField(max_length=200)
    label_en = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(
                fields=["edition", "slug"], name="day_edition_slug_unique"
            ),
            rejection_reason_constraint(),
        ]
        permissions = moderation_permissions("day")

    def __str__(self) -> str:
        return f"{self.edition.year} - {self.label_es}"


class Venue(ModeratedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_es = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200, blank=True, default="")
    address = models.TextField(blank=True, default="")
    city = models.CharField(max_length=200, blank=True, default="")
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    capacity = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name_es"]
        constraints = [rejection_reason_constraint()]
        permissions = moderation_permissions("venue")

    def __str__(self) -> str:
        return self.name_es


class Event(ModeratedModel):
    """A programme entry inside a day (FR-A-03, FR-A-04).

    Descriptions are our own words only — never copied prose from the source
    (brief §11). ``sort_order`` preserves the order the source gave.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="events")
    venue = models.ForeignKey(
        Venue,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    title_es = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True, default="")
    description_es = models.TextField(blank=True, default="")
    description_en = models.TextField(blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)
    # FR-A-12 for the MVP: a plain link. The v2 ``sources`` registry replaces it.
    source_url = models.URLField(max_length=2000, blank=True, default="")
    # Upstream identity, so re-staging is an upsert and not a second row.
    source_record_key = models.CharField(
        max_length=200, blank=True, default="", db_index=True
    )

    class Meta:
        ordering = ["day__date", "sort_order"]
        constraints = [
            rejection_reason_constraint(),
            models.UniqueConstraint(
                fields=["day", "source_record_key"],
                condition=~models.Q(source_record_key=""),
                name="event_day_source_key_unique",
            ),
        ]
        permissions = moderation_permissions("event")
        indexes = [models.Index(fields=["day", "sort_order"])]

    def __str__(self) -> str:
        return f"{self.day.date} - {self.title_es}"
