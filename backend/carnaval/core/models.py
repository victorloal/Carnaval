from __future__ import annotations

from django.db import models


class ModerationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PUBLISHED = "published", "Published"
    REJECTED = "rejected", "Rejected"


class ModerationOrigin(models.TextChoices):
    SCRAPED = "scraped", "Scraped"
    MANUAL = "manual", "Manual"
    COMMUNITY = "community", "Community"
