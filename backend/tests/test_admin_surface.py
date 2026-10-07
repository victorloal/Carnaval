"""The admin surface: FR-D-03 and the raw-payload permission (matrix row 11)."""

from __future__ import annotations

import hashlib
from typing import Any

import pytest
from carnaval.ingestion.http import FetchedPayload
from carnaval.ingestion.raw_store import store_raw
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import Client

from tests.factories import ScrapeSourceFactory

pytestmark = pytest.mark.django_db


def _staff_in(group: str | None) -> Any:
    if group:
        call_command("seed_roles")
    user = get_user_model().objects.create_user(
        username=f"u-{group or 'none'}",
        password="pw",  # noqa: S106
        is_staff=True,  # noqa: S106
    )
    if group:
        user.groups.add(Group.objects.get(name=group))
    return user


def test_a_fresh_staff_user_sees_no_content() -> None:
    """FR-D-03: the console exposes no unreviewed content until roles exist."""
    client = Client()
    client.force_login(_staff_in(None))

    content = client.get("/admin/").content.decode()

    assert "/admin/programme/event/" not in content  # noqa: S101


def test_an_editor_sees_the_review_queue() -> None:
    client = Client()
    client.force_login(_staff_in("editor"))

    content = client.get("/admin/").content.decode()

    assert "/admin/programme/event/" in content  # noqa: S101


def test_the_raw_payload_is_readable_by_an_editor_and_not_a_viewer(
    tmp_path: Any, settings: Any
) -> None:
    settings.INGESTION_RAW_ROOT = str(tmp_path)
    body = b"payload-body"
    payload = FetchedPayload(
        url="https://example.org/x",
        http_status=200,
        content_type="application/json",
        body=body,
        sha256=hashlib.sha256(body).hexdigest(),
    )
    document, _ = store_raw(ScrapeSourceFactory(), payload)

    editor_client = Client()
    editor_client.force_login(_staff_in("editor"))
    editor_response = editor_client.get(f"/admin/raw-payload/{document.pk}/")
    assert editor_response.status_code == 200  # noqa: S101
    assert editor_response.content == body  # noqa: S101

    viewer_client = Client()
    viewer_client.force_login(_staff_in("viewer"))
    assert viewer_client.get(f"/admin/raw-payload/{document.pk}/").status_code == 403  # noqa: S101
