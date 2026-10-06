"""The circuit breaker disables a failing source (FR-B-10, SEC-39)."""

from __future__ import annotations

from typing import Any

import pytest
from carnaval.ingestion import breaker

from tests.factories import ScrapeSourceFactory

pytestmark = pytest.mark.django_db


def test_breaker_disables_the_source_at_the_threshold(settings: Any) -> None:
    settings.INGESTION_BREAKER_THRESHOLD = 3
    source = ScrapeSourceFactory()

    assert breaker.record_failure(source, "boom") is False  # noqa: S101
    assert breaker.record_failure(source, "boom") is False  # noqa: S101
    assert breaker.record_failure(source, "boom") is True  # noqa: S101

    source.refresh_from_db()
    assert source.is_active is False  # noqa: S101
    assert source.consecutive_failures == 3  # noqa: S101
    assert source.last_failure_at is not None  # noqa: S101
    assert source.last_error == "boom"  # noqa: S101


def test_success_resets_the_breaker() -> None:
    source = ScrapeSourceFactory(consecutive_failures=4, last_error="boom")

    breaker.record_success(source)

    source.refresh_from_db()
    assert source.consecutive_failures == 0  # noqa: S101
    assert source.last_error == ""  # noqa: S101
    assert source.last_success_at is not None  # noqa: S101
