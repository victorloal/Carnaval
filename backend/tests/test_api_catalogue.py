"""Filtering, pagination and the cached read contract (FR-A-11, NFR-02)."""

from __future__ import annotations

from datetime import date

import pytest
from carnaval.core.models import ModerationStatus
from rest_framework.test import APIClient

from tests.factories import DayFactory, EditionFactory, EventFactory

pytestmark = pytest.mark.django_db


def test_events_filter_by_edition_and_date_range() -> None:
    edition = EditionFactory(year=2026, status=ModerationStatus.PUBLISHED)
    day_five = DayFactory(
        edition=edition, date=date(2026, 1, 5), status=ModerationStatus.PUBLISHED
    )
    day_six = DayFactory(
        edition=edition, date=date(2026, 1, 6), status=ModerationStatus.PUBLISHED
    )
    event_five = EventFactory(day=day_five, status=ModerationStatus.PUBLISHED)
    event_six = EventFactory(day=day_six, status=ModerationStatus.PUBLISHED)
    client = APIClient()

    by_edition = client.get("/api/events/", {"edition": 2026})
    assert {row["id"] for row in by_edition.json()["results"]} == {  # noqa: S101
        str(event_five.id),
        str(event_six.id),
    }

    by_date = client.get(
        "/api/events/", {"date_from": "2026-01-06", "date_to": "2026-01-06"}
    )
    assert {row["id"] for row in by_date.json()["results"]} == {str(event_six.id)}  # noqa: S101


def test_public_reads_are_cacheable() -> None:
    EditionFactory(status=ModerationStatus.PUBLISHED)

    response = APIClient().get("/api/editions/")

    assert "public" in response["Cache-Control"]  # noqa: S101
    assert "max-age=300" in response["Cache-Control"]  # noqa: S101


def test_results_are_paginated() -> None:
    EditionFactory(status=ModerationStatus.PUBLISHED)

    body = APIClient().get("/api/editions/").json()

    assert {"count", "next", "previous", "results"} <= set(body)  # noqa: S101


def test_the_browsable_api_renders_without_a_500() -> None:
    """A browser (Accept: text/html) must not hit the filter-form template error."""
    EditionFactory(status=ModerationStatus.PUBLISHED)

    response = APIClient().get("/api/editions/", HTTP_ACCEPT="text/html")

    assert response.status_code == 200  # noqa: S101
