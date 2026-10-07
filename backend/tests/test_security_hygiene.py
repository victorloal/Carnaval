"""Repository hygiene — SEC-46 (.env is ignored), part of NFR-09."""

from pathlib import Path

import pytest
from carnaval.ingestion.models import IngestionRun, RawDocument, ScrapeSource
from carnaval.programme.models import Day, Edition, Event, Venue
from django.conf import settings

REPO_ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.django_db


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


def test_content_models_are_permission_gated() -> None:
    """FR-D-03: registration is permission-gated, not open to any staff user.

    The content models are registered in v1, but a fresh staff user with no role
    has no `view` permission on them, so the console exposes nothing.
    """
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.create_user(
        username="fresh-staff",
        password="pw",  # noqa: S106
        is_staff=True,  # noqa: S106
    )
    for model in (Edition, Day, Venue, Event, ScrapeSource, RawDocument, IngestionRun):
        app, name = model._meta.app_label, model._meta.model_name
        assert not user.has_perm(f"{app}.view_{name}")  # noqa: S101
