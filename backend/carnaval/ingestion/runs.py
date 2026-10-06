"""Bookkeeping for one execution of the pipeline (``ingestion_runs``)."""

from __future__ import annotations

from django.utils import timezone

from carnaval.ingestion.models import (
    IngestionRun,
    IngestionStatus,
    ScrapeSource,
)


def empty_stats() -> dict[str, object]:
    """The per-stage statistics the run records (``modelo-datos.md`` §3.7)."""
    return {"extracted": 0, "inserted": 0, "updated": 0, "skipped": 0, "rejected": 0}


def open_run(source: ScrapeSource | None, trigger: str) -> IngestionRun:
    return IngestionRun.objects.create(
        scrape_source=source,
        trigger=trigger,
        status=IngestionStatus.RUNNING,
        started_at=timezone.now(),
        stats=empty_stats(),
    )


def close_run(
    run: IngestionRun,
    status: str,
    *,
    stats: dict[str, object] | None = None,
    error: str = "",
) -> IngestionRun:
    run.status = status
    if stats is not None:
        run.stats = stats
    run.error_message = error
    run.finished_at = timezone.now()
    run.save(update_fields=["status", "stats", "error_message", "finished_at"])
    return run
