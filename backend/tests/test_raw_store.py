"""The RAW STORE gates idempotence on a unique content hash (FR-B-02/03, SEC-37)."""

from __future__ import annotations

import hashlib
from typing import Any

import pytest
from carnaval.ingestion import storage
from carnaval.ingestion.http import FetchedPayload
from carnaval.ingestion.models import RawDocument
from carnaval.ingestion.raw_store import store_raw

from tests.factories import ScrapeSourceFactory

pytestmark = pytest.mark.django_db


def _payload(body: bytes = b"hello") -> FetchedPayload:
    return FetchedPayload(
        url="https://example.org/post/1",
        http_status=200,
        content_type="application/json",
        body=body,
        sha256=hashlib.sha256(body).hexdigest(),
    )


def test_same_bytes_are_stored_once(tmp_path: Any, settings: Any) -> None:
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    source = ScrapeSourceFactory()

    document, created = store_raw(source, _payload())

    assert created is True  # noqa: S101
    assert RawDocument.objects.count() == 1  # noqa: S101
    assert storage.read_payload(document.storage_key) == b"hello"  # noqa: S101

    again, created_again = store_raw(source, _payload())

    assert created_again is False  # noqa: S101
    assert again.pk == document.pk  # noqa: S101
    assert RawDocument.objects.count() == 1  # noqa: S101


def test_storage_key_is_derived_from_the_hash(tmp_path: Any, settings: Any) -> None:
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    payload = _payload()

    document, _ = store_raw(ScrapeSourceFactory(), payload)

    assert payload.sha256 in document.storage_key  # noqa: S101
    assert document.storage_key.endswith(".json")  # noqa: S101


def test_a_different_payload_creates_a_second_row(tmp_path: Any, settings: Any) -> None:
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    source = ScrapeSourceFactory()

    store_raw(source, _payload(b"one"))
    store_raw(source, _payload(b"two"))

    assert RawDocument.objects.count() == 2  # noqa: S101
