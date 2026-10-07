"""``/health`` reports reachability and discloses nothing else (FR-D-11)."""

from __future__ import annotations

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_health_is_ok_and_discloses_nothing() -> None:
    response = Client().get("/health")

    assert response.status_code == 200  # noqa: S101
    assert response.json() == {"status": "ok", "database": "ok"}  # noqa: S101
