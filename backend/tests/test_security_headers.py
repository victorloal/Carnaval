"""Security headers on the public surface (SEC-15, NFR-07/08)."""

from __future__ import annotations

import pytest
from django.test import Client, override_settings

pytestmark = pytest.mark.django_db


def test_public_responses_carry_a_strict_csp() -> None:
    client = Client()

    for path in ("/api/editions/", "/health"):
        csp = client.get(path).headers.get("Content-Security-Policy", "")
        assert "default-src 'self'" in csp  # noqa: S101
        assert "'unsafe-inline'" not in csp  # noqa: S101


def test_referrer_policy_and_nosniff_are_set() -> None:
    response = Client().get("/health")

    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"  # noqa: S101
    assert response.headers["X-Content-Type-Options"] == "nosniff"  # noqa: S101


def test_cors_is_closed_by_default() -> None:
    response = Client().get("/api/editions/", HTTP_ORIGIN="https://evil.example")

    assert "Access-Control-Allow-Origin" not in response.headers  # noqa: S101


def test_cors_allows_a_configured_origin() -> None:
    with override_settings(CORS_ALLOWED_ORIGINS=["https://carnaval.example"]):
        response = Client().get(
            "/api/editions/", HTTP_ORIGIN="https://carnaval.example"
        )

    assert (  # noqa: S101
        response.headers.get("Access-Control-Allow-Origin")
        == "https://carnaval.example"
    )
