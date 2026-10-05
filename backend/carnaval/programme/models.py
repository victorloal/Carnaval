from __future__ import annotations

import uuid

from django.db import models


class Edition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.PositiveIntegerField(unique=True)
    slug = models.SlugField(unique=True, max_length=200)
    title_es = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True, default="")
    starts_on = models.DateField(blank=True, null=True)
    ends_on = models.DateField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    summary_es = models.TextField(blank=True, default="")
    summary_en = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["year"]

    def __str__(self) -> str:
        return f"{self.year} - {self.title_es}"


class Day(models.Model):
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
            )
        ]

    def __str__(self) -> str:
        return f"{self.edition.year} - {self.label_es}"


class Venue(models.Model):
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

    def __str__(self) -> str:
        return self.name_es
