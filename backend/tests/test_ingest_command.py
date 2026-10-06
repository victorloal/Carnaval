"""`ingest_source` and the absolute rule (FR-B-08/09, SEC-38)."""

from __future__ import annotations

from collections.abc import Callable
from io import StringIO
from typing import Any

import httpx
import pytest
from carnaval.core.models import ModerationStatus
from carnaval.ingestion import pipeline
from carnaval.ingestion.models import IngestionRun, IngestionStatus, RawDocument
from django.core.management import call_command
from django.core.management.base import CommandError

from tests.factories import EditionFactory, ScrapeSourceFactory

pytestmark = pytest.mark.django_db

Handler = Callable[[httpx.Request], httpx.Response]


def _client(handler: Handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def _robots_ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, text="User-agent: *\nAllow: /\n", request=request)


def _ok(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/robots.txt":
        return _robots_ok(request)
    return httpx.Response(200, content=b"data", request=request)


def test_dry_run_lists_without_touching_the_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def explode() -> httpx.Client:
        raise AssertionError("dry-run must not open a client")

    monkeypatch.setattr(pipeline, "default_client", explode)
    ScrapeSourceFactory(name="uno")

    out = StringIO()
    call_command("ingest_source", "--all", "--dry-run", stdout=out)

    assert "uno" in out.getvalue()  # noqa: S101


def test_successful_run_stores_and_records(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any, settings: Any
) -> None:
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    monkeypatch.setattr(pipeline, "default_client", lambda: _client(_ok))
    source = ScrapeSourceFactory(name="ok", url="https://example.org/feed")

    call_command("ingest_source", "--all")

    assert RawDocument.objects.count() == 1  # noqa: S101
    run = IngestionRun.objects.get(scrape_source=source)
    assert run.status == IngestionStatus.SUCCEEDED  # noqa: S101
    assert run.stats["skipped"] == 0  # noqa: S101

    call_command("ingest_source", "--all")

    assert RawDocument.objects.count() == 1  # noqa: S101
    latest = IngestionRun.objects.filter(scrape_source=source).latest("started_at")
    assert latest.stats["skipped"] == 1  # noqa: S101


def test_inactive_source_is_skipped_without_a_network_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def explode(request: httpx.Request) -> httpx.Response:
        raise AssertionError("a disabled source must not be fetched")

    monkeypatch.setattr(pipeline, "default_client", lambda: _client(explode))
    source = ScrapeSourceFactory(name="off", is_active=False)

    call_command("ingest_source", "--all")

    run = IngestionRun.objects.get(scrape_source=source)
    assert run.status == IngestionStatus.SKIPPED  # noqa: S101


def test_failed_run_leaves_published_content_untouched(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any, settings: Any
) -> None:
    """SEC-38: a failure never modifies, degrades or deletes a published row."""
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    settings.INGESTION_RETRY_BASE = 0
    settings.INGESTION_RETRY_CAP = 0
    published = EditionFactory(status=ModerationStatus.PUBLISHED, title_es="Original")
    original_updated_at = published.updated_at

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return _robots_ok(request)
        return httpx.Response(500, request=request)

    monkeypatch.setattr(pipeline, "default_client", lambda: _client(handler))
    ScrapeSourceFactory(
        name="roto", url="https://example.org/feed", rate_limit_seconds=0
    )

    with pytest.raises(CommandError):
        call_command("ingest_source", "--all")

    published.refresh_from_db()
    assert published.title_es == "Original"  # noqa: S101
    assert published.status == ModerationStatus.PUBLISHED  # noqa: S101
    assert published.updated_at == original_updated_at  # noqa: S101
    assert RawDocument.objects.count() == 0  # noqa: S101
