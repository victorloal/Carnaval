"""The WordPress REST API handler — preferred over HTML scraping (FR-B-15).

A post is mapped to an `EventCandidate` by combining two independent signals:

- the **day** comes from the post's day **category name** (`5 de enero`), never
  from the post slug: the spike found slugs and dates that disagree;
- the **year** comes from the post's **date**, never from the category name:
  day labels are reused every edition, so the label carries no year.

The `6 de enero` trap: that category is a root category, not a child of `DIAS`,
so days are collected by **name pattern**, never by hierarchy.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from datetime import date, datetime
from typing import Any

from django.utils.text import slugify

from carnaval.ingestion.exceptions import TransformError
from carnaval.ingestion.http import FetchedPayload
from carnaval.ingestion.models import ScrapeSource
from carnaval.ingestion.transforms import EventCandidate, TransformReport

REQUIRED_FIELDS = ("id", "date", "title", "link")

_MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}
_DAY_CATEGORY = re.compile(r"^(\d{1,2})\s+de\s+([a-záéíóú]+)$", re.IGNORECASE)


def _present(value: Any) -> bool:
    return value not in (None, "", [])


def _terms(post: dict[str, Any]) -> Iterator[dict[str, Any]]:
    embedded = post.get("_embedded")
    if not isinstance(embedded, dict):
        return
    groups = embedded.get("wp:term")
    if not isinstance(groups, list):
        return
    for group in groups:
        if not isinstance(group, list):
            continue
        for term in group:
            if isinstance(term, dict) and term.get("taxonomy") == "category":
                yield term


def _day_from_category(post: dict[str, Any]) -> tuple[int, int, str, str] | None:
    for term in _terms(post):
        name = str(term.get("name", "")).strip()
        match = _DAY_CATEGORY.match(name)
        if match is None:
            continue
        month = _MONTHS.get(match.group(2).lower())
        day = int(match.group(1))
        if month is None or not 1 <= day <= 31:
            continue
        slug = str(term.get("slug") or slugify(name))
        return month, day, name, slug
    return None


def _parse_date(value: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def transform(payload: FetchedPayload, source: ScrapeSource) -> TransformReport:
    try:
        posts = json.loads(payload.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TransformError(f"wp_api payload is not JSON: {exc}") from exc
    if not isinstance(posts, list):
        raise TransformError("wp_api payload is not a list of posts")

    field_hits = {field: 0 for field in REQUIRED_FIELDS}
    candidates: list[EventCandidate] = []
    errors: list[str] = []
    rejected = 0

    for post in posts:
        if not isinstance(post, dict):
            rejected += 1
            errors.append("post is not an object")
            continue

        title = post.get("title")
        values = {
            "id": post.get("id"),
            "date": post.get("date"),
            "title": title.get("rendered") if isinstance(title, dict) else None,
            "link": post.get("link"),
        }
        for field, value in values.items():
            if _present(value):
                field_hits[field] += 1
        missing = [field for field, value in values.items() if not _present(value)]
        if missing:
            rejected += 1
            errors.append(f"post {values['id']} missing {', '.join(missing)}")
            continue

        parsed = _parse_date(values["date"])
        if parsed is None:
            rejected += 1
            errors.append(f"post {values['id']} has an unparseable date")
            continue

        month_day = _day_from_category(post)
        if month_day is not None:
            month, day, label, day_slug = month_day
        else:
            month, day = parsed.month, parsed.day
            label = f"{day:02d} de {parsed.strftime('%B')}".lower()
            day_slug = f"{month:02d}-{day:02d}"

        try:
            day_date = date(parsed.year, month, day)
        except ValueError:
            rejected += 1
            errors.append(
                f"post {values['id']} has an invalid day {month:02d}-{day:02d}"
            )
            continue

        candidates.append(
            EventCandidate(
                source_record_key=str(values["id"]),
                year=parsed.year,
                day_date=day_date,
                day_slug=day_slug,
                day_label_es=label,
                day_label_en="",
                title_es=str(values["title"]).strip(),
                title_en="",
                source_url=str(values["link"]),
            )
        )

    return TransformReport(
        candidates=candidates,
        posts_seen=len(posts),
        rejected=rejected,
        field_hits=field_hits,
        errors=errors,
    )
