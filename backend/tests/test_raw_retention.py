"""Raw retention: 30 days and a per-source byte cap (FR-B-16, ADR 0013)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from carnaval.ingestion import storage
from carnaval.ingestion.models import RawDocument, ScrapeSource
from django.core.management import call_command
from django.utils import timezone

from tests.factories import ScrapeSourceFactory

pytestmark = pytest.mark.django_db


def _document(
    source: ScrapeSource, *, key: str, size: int, age_days: int
) -> RawDocument:
    return RawDocument.objects.create(
        scrape_source=source,
        url="https://example.org/x",
        http_status=200,
        content_type="text/plain",
        content_hash=key.ljust(64, "0"),
        byte_size=size,
        storage_key=key,
        fetched_at=timezone.now() - timedelta(days=age_days),
    )


def test_prunes_by_age(tmp_path: Any, settings: Any) -> None:
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    source = ScrapeSourceFactory()
    storage.write_payload("old", b"x")
    old = _document(source, key="old", size=1, age_days=40)
    fresh = _document(source, key="fresh", size=1, age_days=1)

    call_command("prune_raw_documents", "--days", "30")

    assert not RawDocument.objects.filter(pk=old.pk).exists()  # noqa: S101
    assert RawDocument.objects.filter(pk=fresh.pk).exists()  # noqa: S101
    assert not (tmp_path / "old").exists()  # noqa: S101


def test_prunes_by_size_oldest_first(tmp_path: Any, settings: Any) -> None:
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    source = ScrapeSourceFactory()
    a = _document(source, key="a", size=100, age_days=3)
    b = _document(source, key="b", size=100, age_days=2)
    c = _document(source, key="c", size=100, age_days=1)

    call_command("prune_raw_documents", "--days", "3650", "--bytes", "250")

    assert not RawDocument.objects.filter(pk=a.pk).exists()  # noqa: S101
    assert RawDocument.objects.filter(pk=b.pk).exists()  # noqa: S101
    assert RawDocument.objects.filter(pk=c.pk).exists()  # noqa: S101
