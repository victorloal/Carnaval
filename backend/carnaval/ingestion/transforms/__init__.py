"""Transform: a stored payload becomes candidate records.

The interface is a dataclass, not a shared global: `transform(payload, source)`
returns a `TransformReport` with the candidates plus the field-level counts the
sanity gate needs.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime

from carnaval.ingestion.http import FetchedPayload
from carnaval.ingestion.models import ScrapeSource


@dataclass(frozen=True)
class EventCandidate:
    """One programme entry, before it is staged as a `pending` row."""

    source_record_key: str
    year: int
    day_date: date
    day_slug: str
    day_label_es: str
    day_label_en: str
    title_es: str
    title_en: str
    source_url: str
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    description_es: str = ""
    description_en: str = ""


@dataclass
class TransformReport:
    candidates: list[EventCandidate]
    posts_seen: int
    rejected: int
    # Required field -> how many posts carried it. The sanity gate reads this.
    field_hits: dict[str, int]
    errors: list[str] = field(default_factory=list)


Transform = Callable[[FetchedPayload, ScrapeSource], TransformReport]
