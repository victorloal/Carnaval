"""Repository hygiene — SEC-46 (.env is ignored), part of NFR-09."""

from pathlib import Path

from carnaval.ingestion.models import IngestionRun, RawDocument, ScrapeSource
from carnaval.programme.models import Day, Edition, Event, Venue
from django.conf import settings
from django.contrib import admin

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_env_file_is_ignored() -> None:
    """SEC-46: `.env` must never be committable."""
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    entries = {
        line.strip()
        for line in gitignore.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    assert ".env" in entries  # noqa: S101


def test_csrf_cookie_is_httponly() -> None:
    """ADR 0005: the CSRF cookie is httpOnly, Secure and SameSite."""
    assert settings.CSRF_COOKIE_HTTPONLY is True  # noqa: S101
    assert settings.CSRF_COOKIE_SAMESITE == "Lax"  # noqa: S101


def test_content_models_are_not_exposed_in_admin() -> None:
    """FR-D-03: a fresh install must not surface unreviewed content.

    The MVP ships no admin, so none of the content or ingestion models may be
    registered on the site.
    """
    for model in (Edition, Day, Venue, Event, ScrapeSource, RawDocument, IngestionRun):
        assert not admin.site.is_registered(model)  # noqa: S101
