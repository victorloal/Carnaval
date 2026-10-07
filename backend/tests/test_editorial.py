"""v2 editorial backend: rights gate, settings, visibility and search."""

from __future__ import annotations

from typing import Any, cast

import pytest
from carnaval.audit.models import AuditLog
from carnaval.core.models import ModerationStatus
from carnaval.editorial.admin import SiteSettingAdmin
from carnaval.editorial.models import MediaAsset, RightsStatus, SiteSetting
from carnaval.moderation import service
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.http import HttpRequest
from rest_framework.test import APIClient

from tests.factories import (
    DayFactory,
    EditionFactory,
    EventFactory,
    MediaAssetFactory,
    NewsItemFactory,
    SiteSettingFactory,
)

pytestmark = pytest.mark.django_db


def _editor() -> Any:
    call_command("seed_roles")
    user = get_user_model().objects.create_user(username="ed-v2", password="pw")  # noqa: S106
    user.groups.add(Group.objects.get(name="editor"))
    return user


def test_an_unknown_rights_image_cannot_be_published() -> None:
    editor = _editor()
    asset = MediaAssetFactory(rights_status=RightsStatus.UNKNOWN)

    with pytest.raises(ValidationError):
        service.approve(asset, actor=editor)


def test_a_fully_cited_image_publishes() -> None:
    editor = _editor()
    asset = MediaAssetFactory(
        rights_status=RightsStatus.LICENSED,
        author="A. Photographer",
        source_ref="Archive",
        citation_text="A. Photographer, Archive, CC BY 4.0",
        exif_stripped=True,
    )

    service.approve(asset, actor=editor)

    asset.refresh_from_db()
    assert asset.status == ModerationStatus.PUBLISHED  # noqa: S101


def test_the_database_refuses_publishing_an_unknown_rights_image() -> None:
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            MediaAsset.objects.create(
                title_es="Cheating", status=ModerationStatus.PUBLISHED
            )


def test_minor_subject_requires_guardian_consent() -> None:
    editor = _editor()
    asset = MediaAssetFactory(
        rights_status=RightsStatus.LICENSED,
        author="A",
        source_ref="B",
        citation_text="C",
        exif_stripped=True,
        minor_subject=True,
        guardian_consent_on_file=False,
    )

    with pytest.raises(ValidationError):
        service.approve(asset, actor=editor)


def test_a_setting_may_not_hold_a_secret() -> None:
    setting = SiteSetting(key="stripe.api_key", value="sk_live_123")

    with pytest.raises(ValidationError):
        setting.full_clean()


def test_a_setting_change_is_audited() -> None:
    setting = SiteSettingFactory(key="site.tagline", value="old")

    class _Request:
        user = None

    setting.value = "new"
    SiteSettingAdmin(SiteSetting, admin.site).save_model(
        cast(HttpRequest, _Request()), setting, None, True
    )

    assert AuditLog.objects.filter(object_type="editorial.sitesetting").exists()  # noqa: S101


def test_news_and_media_are_published_only() -> None:
    NewsItemFactory(status=ModerationStatus.PUBLISHED)
    NewsItemFactory(status=ModerationStatus.PENDING)
    published_asset = MediaAssetFactory(
        status=ModerationStatus.PUBLISHED,
        rights_status=RightsStatus.LICENSED,
        author="A",
        source_ref="B",
        citation_text="C",
        exif_stripped=True,
    )
    MediaAssetFactory(status=ModerationStatus.PENDING)
    client = APIClient()

    assert len(client.get("/api/news/").json()["results"]) == 1  # noqa: S101
    media = client.get("/api/media/").json()["results"]
    assert [row["id"] for row in media] == [str(published_asset.pk)]  # noqa: S101


def test_search_returns_published_only() -> None:
    edition = EditionFactory(status=ModerationStatus.PUBLISHED)
    day = DayFactory(edition=edition, status=ModerationStatus.PUBLISHED)
    EventFactory(day=day, title_es="Gran Desfile", status=ModerationStatus.PUBLISHED)
    EventFactory(title_es="Gran Desfile oculto", status=ModerationStatus.PENDING)
    NewsItemFactory(headline="Gran noticia", status=ModerationStatus.PUBLISHED)
    client = APIClient()

    body = client.get("/api/search/", {"q": "Gran"}).json()

    assert len(body["events"]) == 1  # noqa: S101
    assert len(body["news"]) == 1  # noqa: S101
