"""The anonymous public API is rate-limited per IP (NFR-17)."""

from __future__ import annotations

import pytest
from carnaval.core.models import ModerationStatus
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework.throttling import AnonRateThrottle

from tests.factories import EditionFactory

pytestmark = pytest.mark.django_db


def _two_per_minute(self: AnonRateThrottle) -> str:
    return "2/min"


def test_anonymous_requests_are_rate_limited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    EditionFactory(status=ModerationStatus.PUBLISHED)
    # Patching the rate (not the REST_FRAMEWORK setting) keeps the test
    # independent of test order and of DRF's settings cache.
    monkeypatch.setattr(AnonRateThrottle, "get_rate", _two_per_minute)
    cache.clear()
    client = APIClient()

    assert client.get("/api/editions/").status_code == 200  # noqa: S101
    assert client.get("/api/editions/").status_code == 200  # noqa: S101
    assert client.get("/api/editions/").status_code == 429  # noqa: S101
