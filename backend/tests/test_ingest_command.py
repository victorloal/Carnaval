"""`ingest_source` end to end, and the absolute rule (FR-B-08/09, SEC-37/38/40)."""

from __future__ import annotations

import json
from collections.abc import Callable
from io import StringIO
from typing import Any

import httpx
import pytest
from carnaval.core.models import ModerationStatus
from carnaval.ingestion import pipeline
from carnaval.ingestion.models import (
    IngestionRun,
    IngestionStatus,
    RawDocument,
    SourceType,
)
from carnaval.programme.models import Event
from django.core.management import call_command
from django.core.management.base import CommandError

from tests import fixture_data
from tests.factories import EditionFactory, ScrapeSourceFactory

pytestmark = pytest.mark.django_db

Handler = Callable[[httpx.Request], httpx.Response]

WP_POSTS_URL = "https://carnavaldepasto.org/wp-json/wp/v2/posts"

ONE_POST = json.dumps(
    [
        {
            "id": 1,
            "date": "2020-01-05T09:00:00",
            "slug": "x",
            "link": "https://example.org/x/",
            "title": {"rendered": "X"},
        }
    ]
).encode("utf-8")


def _client(handler: Handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def _robots_ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, text="User-agent: *\nAllow: /\n", request=request)


def _ok(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/robots.txt":
        return _robots_ok(request)
    return httpx.Response(
        200,
        content=ONE_POST,
        headers={"content-type": "application/json"},
        request=request,
    )


def _fixture_handler(body: bytes) -> Handler:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return _robots_ok(request)
        return httpx.Response(
            200,
            content=body,
            headers={"content-type": "application/json"},
            request=request,
        )

    return handler


def _wp_source() -> Any:
    return ScrapeSourceFactory(
        name="wp",
        url=WP_POSTS_URL,
        source_type=SourceType.WP_API,
        rate_limit_seconds=0,
    )


# --- The command itself ---------------------------------------------------


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


# --- Fetch and raw store --------------------------------------------------


def test_a_successful_fetch_stores_and_records(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any, settings: Any
) -> None:
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    settings.INGESTION_TARGET_YEAR = 2020
    monkeypatch.setattr(pipeline, "default_client", lambda: _client(_ok))
    source = ScrapeSourceFactory(name="ok", url="https://example.org/feed")

    call_command("ingest_source", "--all")

    assert RawDocument.objects.count() == 1  # noqa: S101
    run = IngestionRun.objects.get(scrape_source=source)
    assert run.status == IngestionStatus.SUCCEEDED  # noqa: S101
    assert run.stats["extracted"] == 1  # noqa: S101


# --- Transform and staging ------------------------------------------------


def test_pipeline_stages_pending_events(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any, settings: Any
) -> None:
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    settings.INGESTION_TARGET_YEAR = 2020
    body, _ = fixture_data.load("carnavaldepasto", "wp_posts")
    monkeypatch.setattr(
        pipeline, "default_client", lambda: _client(_fixture_handler(body))
    )
    source = _wp_source()

    call_command("ingest_source", "--all")

    run = IngestionRun.objects.get(scrape_source=source)
    assert run.status == IngestionStatus.SUCCEEDED  # noqa: S101
    assert run.stats["extracted"] == 5  # noqa: S101
    assert Event.objects.filter(status=ModerationStatus.PENDING).count() == 5  # noqa: S101
    # The pipeline stages pending rows; it never publishes.
    assert Event.objects.filter(status=ModerationStatus.PUBLISHED).count() == 0  # noqa: S101


def test_the_default_target_year_is_the_newest_edition(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any, settings: Any
) -> None:
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    settings.INGESTION_TARGET_YEAR = ""
    EditionFactory(year=2026)
    body, _ = fixture_data.load("carnavaldepasto", "wp_posts")
    monkeypatch.setattr(
        pipeline, "default_client", lambda: _client(_fixture_handler(body))
    )
    _wp_source()

    with pytest.raises(CommandError):
        call_command("ingest_source", "--all")

    assert Event.objects.count() == 0  # noqa: S101


def test_the_same_payload_is_a_noop(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any, settings: Any
) -> None:
    """SEC-37: two runs over one payload produce zero duplicates."""
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    settings.INGESTION_TARGET_YEAR = 2020
    body, _ = fixture_data.load("carnavaldepasto", "wp_posts")
    monkeypatch.setattr(
        pipeline, "default_client", lambda: _client(_fixture_handler(body))
    )
    source = _wp_source()

    call_command("ingest_source", "--all")
    call_command("ingest_source", "--all")

    assert Event.objects.count() == 5  # noqa: S101
    assert RawDocument.objects.count() == 1  # noqa: S101
    latest = IngestionRun.objects.filter(scrape_source=source).latest("started_at")
    assert latest.stats["skipped"] == 1  # noqa: S101


def test_zero_extraction_alarms_and_stages_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any, settings: Any
) -> None:
    """SEC-40: a changed payload that yields nothing is an alarm, not a success."""
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    settings.INGESTION_TARGET_YEAR = 2020
    full, _ = fixture_data.load("carnavaldepasto", "wp_posts")
    empty, _ = fixture_data.load("carnavaldepasto", "wp_posts_empty")
    holder = {"handler": _fixture_handler(full)}
    monkeypatch.setattr(pipeline, "default_client", lambda: _client(holder["handler"]))
    source = _wp_source()

    call_command("ingest_source", "--all")
    assert Event.objects.count() == 5  # noqa: S101

    holder["handler"] = _fixture_handler(empty)
    with pytest.raises(CommandError):
        call_command("ingest_source", "--all")

    assert Event.objects.count() == 5  # noqa: S101
    latest = IngestionRun.objects.filter(scrape_source=source).latest("started_at")
    assert latest.status == IngestionStatus.FAILED  # noqa: S101


# --- The absolute rule ----------------------------------------------------


def test_a_failed_run_leaves_published_content_untouched(
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
