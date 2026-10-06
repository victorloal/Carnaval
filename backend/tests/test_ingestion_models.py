"""Unit tests for the ingestion tables (FR-B-02, FR-B-03, FR-B-08, FR-B-12)."""

import pytest
from carnaval.ingestion.models import IngestionStatus, ScrapeSource, SourceType
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from tests.factories import (
    IngestionRunFactory,
    RawDocumentFactory,
    ScrapeSourceFactory,
)

pytestmark = pytest.mark.django_db


def test_scrape_source_defaults() -> None:
    """FR-B-12: a source is active, rate-limited and starts with a clean counter."""
    source = ScrapeSourceFactory()
    assert source.is_active is True  # noqa: S101
    assert source.rate_limit_seconds > 0  # noqa: S101
    assert source.consecutive_failures == 0  # noqa: S101
    assert source.source_type == SourceType.WP_API  # noqa: S101


def test_raw_document_content_hash_is_unique() -> None:
    """FR-B-03: the raw store gates idempotence on a unique content hash."""
    RawDocumentFactory(content_hash="a" * 64)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            RawDocumentFactory(content_hash="a" * 64)


def test_raw_document_keeps_its_source() -> None:
    """A source with stored payloads is protected from deletion."""
    source = ScrapeSourceFactory()
    RawDocumentFactory(scrape_source=source)
    with pytest.raises(ProtectedError):
        source.delete()


def test_ingestion_run_starts_running() -> None:
    """FR-B-08: a run is opened, then closed with stats and a terminal status."""
    run = IngestionRunFactory()
    assert run.status == IngestionStatus.RUNNING  # noqa: S101
    assert run.finished_at is None  # noqa: S101
    assert run.stats == {}  # noqa: S101


def test_ingestion_run_without_a_source() -> None:
    """A manual run need not be bound to a single source."""
    run = IngestionRunFactory(scrape_source=None)
    assert run.scrape_source is None  # noqa: S101
    assert ScrapeSource.objects.count() == 0  # noqa: S101
