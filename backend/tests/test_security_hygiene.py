"""Repository hygiene — SEC-46 (.env is ignored), part of NFR-09."""

from pathlib import Path

from django.conf import settings

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
