"""One source, one run: fetch, store and record — nothing else.

The pipeline's only writes are to ``raw_documents``, ``ingestion_runs`` and the
breaker columns on ``scrape_sources``. It never touches a content table, so a
failed run cannot modify, degrade or delete a ``published`` row (FR-B-09).
"""

from __future__ import annotations

import logging

import httpx
from django.conf import settings

from carnaval.ingestion import breaker, runs
from carnaval.ingestion.exceptions import FetchError, RobotsDisallowed
from carnaval.ingestion.http import Fetcher
from carnaval.ingestion.models import (
    IngestionRun,
    IngestionStatus,
    ScrapeSource,
)
from carnaval.ingestion.raw_store import store_raw

logger = logging.getLogger(__name__)


def default_client() -> httpx.Client:
    return httpx.Client(
        timeout=settings.INGESTION_HTTP_TIMEOUT,
        follow_redirects=True,
    )


def run_source(
    source: ScrapeSource,
    *,
    trigger: str,
    client: httpx.Client,
    fetcher: Fetcher | None = None,
) -> IngestionRun:
    if not source.is_active:
        # Disabled, breaker-open or not due: skipped without a network call.
        return runs.close_run(runs.open_run(source, trigger), IngestionStatus.SKIPPED)

    run = runs.open_run(source, trigger)
    fetcher = fetcher or Fetcher(source, client=client)
    try:
        payload = fetcher.fetch(source.url)
    except RobotsDisallowed as exc:
        _fail(source, run, str(exc), alarm="robots.txt refused")
    except FetchError as exc:
        _fail(source, run, str(exc))
    else:
        _, created = store_raw(source, payload)
        breaker.record_success(source)
        stats = runs.empty_stats()
        stats["skipped"] = 0 if created else 1
        runs.close_run(run, IngestionStatus.SUCCEEDED, stats=stats)
    return run


def _fail(
    source: ScrapeSource,
    run: IngestionRun,
    message: str,
    *,
    alarm: str | None = None,
) -> None:
    tripped = breaker.record_failure(source, message)
    runs.close_run(run, IngestionStatus.FAILED, error=message)
    if alarm:
        logger.error("%s: %s", alarm, message)
    if tripped:
        logger.error(
            "circuit breaker disabled source %s after %s consecutive failures: %s",
            source.name,
            settings.INGESTION_BREAKER_THRESHOLD,
            message,
        )
