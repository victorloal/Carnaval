"""Staging: candidates become `pending`; published rows are never touched."""

from __future__ import annotations

from datetime import date

import pytest
from carnaval.core.models import ModerationOrigin, ModerationStatus
from carnaval.ingestion import staging
from carnaval.ingestion.transforms import EventCandidate, TransformReport
from carnaval.programme.models import Day, Edition, Event

from tests.factories import (
    DayFactory,
    EditionFactory,
    EventFactory,
    IngestionRunFactory,
)

pytestmark = pytest.mark.django_db

FIELDS = ("id", "date", "title", "link")


def _candidate(
    source_record_key: str = "101", title_es: str = "Dia de Negros"
) -> EventCandidate:
    return EventCandidate(
        source_record_key=source_record_key,
        year=2020,
        day_date=date(2020, 1, 5),
        day_slug="5-de-enero",
        day_label_es="5 de enero",
        day_label_en="",
        title_es=title_es,
        title_en="",
        source_url="https://carnavaldepasto.org/x/",
    )


def _report(*candidates: EventCandidate) -> TransformReport:
    return TransformReport(
        candidates=list(candidates),
        posts_seen=len(candidates),
        rejected=0,
        field_hits={field: len(candidates) for field in FIELDS},
    )


def test_stage_creates_pending_rows() -> None:
    run = IngestionRunFactory()

    stats = staging.stage(run, _report(_candidate()))

    assert stats["inserted"] == 1  # noqa: S101
    event = Event.objects.get(source_record_key="101")
    assert event.status == ModerationStatus.PENDING  # noqa: S101
    assert event.origin == ModerationOrigin.SCRAPED  # noqa: S101
    assert event.ingestion_run_id == run.id  # noqa: S101
    assert Edition.objects.get(year=2020).status == ModerationStatus.PENDING  # noqa: S101
    assert Day.objects.get(slug="5-de-enero").status == ModerationStatus.PENDING  # noqa: S101


def test_restaging_updates_the_pending_row() -> None:
    run = IngestionRunFactory()
    staging.stage(run, _report(_candidate()))

    stats = staging.stage(run, _report(_candidate(title_es="Renamed")))

    assert stats["updated"] == 1  # noqa: S101
    assert Event.objects.count() == 1  # noqa: S101
    assert Event.objects.get(source_record_key="101").title_es == "Renamed"  # noqa: S101


def test_a_published_event_is_never_modified() -> None:
    edition = EditionFactory(year=2020, status=ModerationStatus.PUBLISHED)
    day = DayFactory(edition=edition, slug="5-de-enero")
    EventFactory(
        day=day,
        source_record_key="101",
        title_es="Live",
        status=ModerationStatus.PUBLISHED,
        origin=ModerationOrigin.SCRAPED,
    )
    run = IngestionRunFactory()

    stats = staging.stage(run, _report(_candidate(title_es="Changed")))

    assert stats["skipped"] == 1  # noqa: S101
    published = Event.objects.get(source_record_key="101")
    assert published.title_es == "Live"  # noqa: S101
    assert published.status == ModerationStatus.PUBLISHED  # noqa: S101
    # §5.1: the change is proposed, never written.
    assert published.staged_changes is not None  # noqa: S101
    assert published.staged_changes["title_es"] == "Changed"  # noqa: S101


def test_an_existing_edition_is_not_modified() -> None:
    published = EditionFactory(year=2020, status=ModerationStatus.PUBLISHED)
    run = IngestionRunFactory()

    staging.stage(run, _report(_candidate()))

    published.refresh_from_db()
    assert published.status == ModerationStatus.PUBLISHED  # noqa: S101
