"""The public API exposes only `published` content (FR-A-06, SEC-47, NFR-18)."""

from __future__ import annotations

from datetime import date

import pytest
from carnaval.core.models import ModerationStatus
from rest_framework.test import APIClient

from tests.factories import DayFactory, EditionFactory, EventFactory, VenueFactory

pytestmark = pytest.mark.django_db


def test_pending_and_rejected_content_is_invisible() -> None:
    published = EditionFactory(status=ModerationStatus.PUBLISHED)
    pending = EditionFactory(status=ModerationStatus.PENDING)
    rejected = EditionFactory(
        status=ModerationStatus.REJECTED, rejection_reason="duplicate"
    )
    client = APIClient()

    listing = client.get("/api/editions/")
    ids = {row["id"] for row in listing.json()["results"]}

    assert listing.status_code == 200  # noqa: S101
    assert str(published.id) in ids  # noqa: S101
    assert str(pending.id) not in ids  # noqa: S101
    assert str(rejected.id) not in ids  # noqa: S101
    assert client.get(f"/api/editions/{published.id}/").status_code == 200  # noqa: S101
    assert client.get(f"/api/editions/{pending.id}/").status_code == 404  # noqa: S101
    assert client.get(f"/api/editions/{rejected.id}/").status_code == 404  # noqa: S101


def test_a_pending_event_is_invisible_even_under_a_published_day() -> None:
    edition = EditionFactory(status=ModerationStatus.PUBLISHED)
    day = DayFactory(
        edition=edition, date=date(2026, 1, 5), status=ModerationStatus.PUBLISHED
    )
    published = EventFactory(day=day, status=ModerationStatus.PUBLISHED)
    pending = EventFactory(day=day, status=ModerationStatus.PENDING)
    client = APIClient()

    ids = {row["id"] for row in client.get("/api/events/").json()["results"]}

    assert str(published.id) in ids  # noqa: S101
    assert str(pending.id) not in ids  # noqa: S101


def test_the_anonymous_surface_is_read_only() -> None:
    client = APIClient()

    assert client.post("/api/events/", {}).status_code == 405  # noqa: S101
    assert client.delete("/api/events/").status_code == 405  # noqa: S101
    assert client.post("/api/editions/", {}).status_code == 405  # noqa: S101


def test_venues_and_days_are_published_only() -> None:
    edition = EditionFactory(status=ModerationStatus.PUBLISHED)
    DayFactory(edition=edition, status=ModerationStatus.PUBLISHED)
    DayFactory(edition=edition, status=ModerationStatus.PENDING)
    VenueFactory(status=ModerationStatus.PUBLISHED)
    VenueFactory(status=ModerationStatus.PENDING)
    client = APIClient()

    assert len(client.get("/api/days/").json()["results"]) == 1  # noqa: S101
    assert len(client.get("/api/venues/").json()["results"]) == 1  # noqa: S101
    assert client.get("/api/days/").json()["results"][0]["label_es"]  # noqa: S101
