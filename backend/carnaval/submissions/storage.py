"""Quarantine storage for submitted files (ADR 0006).

Separate from the raw-payload store and private by construction: the file is
written under `SUBMISSION_QUARANTINE_ROOT`, which is gitignored, and only a
reviewer can move it to public storage on approval.
"""

from __future__ import annotations

from pathlib import Path

from django.conf import settings


def _root() -> Path:
    root = Path(settings.SUBMISSION_QUARANTINE_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    return root


def save_quarantine(storage_key: str, body: bytes) -> str:
    path = _root() / storage_key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return storage_key


def read_quarantine(storage_key: str) -> bytes:
    return (_root() / storage_key).read_bytes()


def delete_quarantine(storage_key: str) -> None:
    path = _root() / storage_key
    if path.exists():
        path.unlink()
