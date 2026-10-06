"""The RAW STORE — one row per successfully fetched payload.

The unique ``content_hash`` is what makes re-running a source idempotent
(FR-B-03): a payload already seen is a no-op, never reprocessed. A concurrent
duplicate insert raises ``IntegrityError``; that is caught and treated as a
skip, because the constraint is the last line of defence, not a crash.
"""

from __future__ import annotations

from django.db import IntegrityError
from django.utils import timezone

from carnaval.ingestion import storage
from carnaval.ingestion.http import FetchedPayload
from carnaval.ingestion.models import RawDocument, ScrapeSource

_CONTENT_TYPE_EXT = {
    "application/json": ".json",
    "text/html": ".html",
    "application/pdf": ".pdf",
}


def _extension(content_type: str) -> str:
    main = content_type.split(";", 1)[0].strip().lower()
    return _CONTENT_TYPE_EXT.get(main, ".bin")


def store_raw(
    source: ScrapeSource, payload: FetchedPayload
) -> tuple[RawDocument, bool]:
    """Store a payload once. Returns ``(document, created)``.

    ``created=False`` is the idempotent no-op: the same bytes were already seen,
    so nothing is transformed and nothing is queued.
    """
    existing = RawDocument.objects.filter(content_hash=payload.sha256).first()
    if existing is not None:
        return existing, False

    storage_key = f"raw/{source.pk}/{payload.sha256}{_extension(payload.content_type)}"
    storage.write_payload(storage_key, payload.body)
    try:
        document = RawDocument.objects.create(
            scrape_source=source,
            url=payload.url,
            http_status=payload.http_status,
            content_type=payload.content_type,
            content_hash=payload.sha256,
            byte_size=len(payload.body),
            storage_key=storage_key,
            fetched_at=timezone.now(),
        )
    except IntegrityError:
        # A concurrent run inserted the same hash first.
        return RawDocument.objects.get(content_hash=payload.sha256), False
    return document, True
