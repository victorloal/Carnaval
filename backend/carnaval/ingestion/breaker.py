"""The circuit breaker: state lives on ``scrape_sources``.

A failure increments the counter and stores the reason; the source is disabled
once the counter reaches the threshold and a human re-enables it. A success
resets everything.
"""

from __future__ import annotations

from django.conf import settings
from django.utils import timezone

from carnaval.ingestion.models import ScrapeSource

_MAX_ERROR = 2000


def record_success(source: ScrapeSource) -> None:
    source.consecutive_failures = 0
    source.last_success_at = timezone.now()
    source.last_error = ""
    source.save(update_fields=["consecutive_failures", "last_success_at", "last_error"])


def record_failure(source: ScrapeSource, message: str) -> bool:
    """Increment the breaker. Returns ``True`` when the source was just disabled."""
    source.consecutive_failures += 1
    source.last_failure_at = timezone.now()
    source.last_error = message[:_MAX_ERROR]
    tripped = source.consecutive_failures >= settings.INGESTION_BREAKER_THRESHOLD
    if tripped:
        source.is_active = False
    source.save(
        update_fields=[
            "consecutive_failures",
            "last_failure_at",
            "last_error",
            "is_active",
        ]
    )
    return tripped
