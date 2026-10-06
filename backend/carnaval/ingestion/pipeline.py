"""One source, one run: fetch, store, transform, sanity-check, stage.

The pipeline's only writes are to `raw_documents`, `ingestion_runs`, the breaker
columns on `scrape_sources`, and `pending` rows the pipeline itself owns. It
never modifies, degrades or deletes a `published` row (FR-B-09), so a failed run
cannot change public content.
"""

from __future__ import annotations

import logging

import httpx
from django.conf import settings

from carnaval.ingestion import breaker, runs, sanity, staging
from carnaval.ingestion.exceptions import (
    IngestionError,
    RobotsDisallowed,
    SanityError,
    TransformError,
)
from carnaval.ingestion.http import Fetcher
from carnaval.ingestion.models import (
    IngestionRun,
    IngestionStatus,
    ScrapeSource,
)
from carnaval.ingestion.raw_store import store_raw
from carnaval.ingestion.transforms import Transform
from carnaval.ingestion.transforms.registry import TRANSFORMS

logger = logging.getLogger(__name__)


def default_client() -> httpx.Client:
    return httpx.Client(
        timeout=settings.INGESTION_HTTP_TIMEOUT,
        follow_redirects=True,
    )


def transform_for(source: ScrapeSource) -> Transform:
    transform = TRANSFORMS.get(source.source_type)
    if transform is None:
        raise TransformError(f"no transform for source_type={source.source_type!r}")
    return transform


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
        return run
    except IngestionError as exc:
        _fail(source, run, str(exc))
        return run

    _, created = store_raw(source, payload)
    if not created:
        # Change detection: the same bytes were already processed.
        breaker.record_success(source)
        stats = runs.empty_stats()
        stats["skipped"] = 1
        runs.close_run(run, IngestionStatus.SUCCEEDED, stats=stats)
        return run

    try:
        report = transform_for(source)(payload, source)
        result = sanity.check(
            report,
            history=_history(source),
            target_year=_target_year(),
        )
        if not result.passed:
            raise SanityError("; ".join(result.reasons))
        stats = staging.stage(run, report)
    except IngestionError as exc:
        _fail(source, run, str(exc))
        return run

    breaker.record_success(source)
    stats["selector_hits"] = report.field_hits
    runs.close_run(run, IngestionStatus.SUCCEEDED, stats=stats)
    return run


def _history(source: ScrapeSource) -> list[int]:
    """Extracted counts of the last successful runs, for the sanity gate."""
    counts: list[int] = []
    recent = IngestionRun.objects.filter(
        scrape_source=source, status=IngestionStatus.SUCCEEDED
    ).order_by("-started_at")[:5]
    for run in recent:
        value = (run.stats or {}).get("extracted")
        if isinstance(value, int) and value > 0:
            counts.append(value)
    return counts


def _target_year() -> int | None:
    value = settings.INGESTION_TARGET_YEAR
    if value not in (None, ""):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    # Default: the newest edition being prepared, so the alignment guard is on
    # without configuration. None only before any edition exists.
    from carnaval.programme.models import Edition

    return Edition.objects.order_by("-year").values_list("year", flat=True).first()


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
