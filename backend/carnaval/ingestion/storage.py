"""Raw-payload storage behind one module.

The MVP writes to a gitignored local directory (`INGESTION_RAW_ROOT`). This
module is the swap point for object storage: ADR 0015 chooses the provider, and
only these three functions change. The database holds an opaque ``storage_key``,
never a filesystem path, so a provider change does not touch the schema.
"""

from __future__ import annotations

from pathlib import Path

from django.conf import settings


def _root() -> Path:
    root = Path(settings.INGESTION_RAW_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_payload(storage_key: str, body: bytes) -> str:
    """Write ``body`` at ``storage_key`` and return the key that was used."""
    path = _root() / storage_key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return storage_key


def read_payload(storage_key: str) -> bytes:
    return (_root() / storage_key).read_bytes()


def delete_payload(storage_key: str) -> None:
    path = _root() / storage_key
    if path.exists():
        path.unlink()
