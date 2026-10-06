"""Load committed HTTP fixtures.

A fixture is a directory ``backend/tests/fixtures/<source>/<case>/`` holding the
response ``body`` and a ``meta.json`` with the URL, status, content type and the
``content_hash`` the pipeline should compute (plan-pruebas.md §1). No test may
reach a live source, so these files are the only payloads the suite ever sees.
"""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load(source: str, case: str) -> tuple[bytes, dict[str, object]]:
    base = FIXTURES / source / case
    meta = json.loads((base / "meta.json").read_text(encoding="utf-8"))
    return (base / "body").read_bytes(), meta
