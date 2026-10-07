"""The moderation verbs and the append-only decision log (v1 / Sprint 09)."""

from __future__ import annotations

from typing import Any

import pytest
from carnaval.audit.models import AuditLog
from carnaval.core.models import ModerationStatus
from carnaval.moderation import service
from carnaval.moderation.models import ModerationAction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command

from tests.factories import DayFactory, EditionFactory, EventFactory

pytestmark = pytest.mark.django_db


def _user_in(group: str) -> Any:
    call_command("seed_roles")
    user = get_user_model().objects.create_user(username=f"u-{group}", password="pw")  # noqa: S106
    user.groups.add(Group.objects.get(name=group))
    return user


def test_approve_publishes_and_records_both_logs() -> None:
    editor = _user_in("editor")
    event = EventFactory()

    service.approve(event, actor=editor)

    event.refresh_from_db()
    assert event.status == ModerationStatus.PUBLISHED  # noqa: S101
    assert event.reviewed_by_id == editor.pk  # noqa: S101
    assert ModerationAction.objects.filter(  # noqa: S101
        subject_id=event.pk, action="approve"
    ).exists()
    assert AuditLog.objects.filter(object_id=event.pk, action="approve").exists()  # noqa: S101


def test_approving_an_edition_publishes_its_pending_children() -> None:
    editor = _user_in("editor")
    edition = EditionFactory()
    day = DayFactory(edition=edition)
    event = EventFactory(day=day)

    service.approve(edition, actor=editor)

    edition.refresh_from_db()
    day.refresh_from_db()
    event.refresh_from_db()
    assert edition.status == ModerationStatus.PUBLISHED  # noqa: S101
    assert day.status == ModerationStatus.PUBLISHED  # noqa: S101
    assert event.status == ModerationStatus.PUBLISHED  # noqa: S101


def test_a_rejection_requires_a_reason() -> None:
    editor = _user_in("editor")
    event = EventFactory()

    with pytest.raises(ValueError):
        service.reject(event, actor=editor, reason="   ")


def test_a_rejection_records_the_reason() -> None:
    editor = _user_in("editor")
    event = EventFactory()

    service.reject(event, actor=editor, reason="not ours")

    event.refresh_from_db()
    assert event.status == ModerationStatus.REJECTED  # noqa: S101
    assert event.rejection_reason == "not ours"  # noqa: S101
    assert ModerationAction.objects.filter(  # noqa: S101
        subject_id=event.pk, action="reject", reason="not ours"
    ).exists()


def test_unpublish_returns_to_pending() -> None:
    editor = _user_in("editor")
    event = EventFactory(status=ModerationStatus.PUBLISHED)

    service.unpublish(event, actor=editor)

    event.refresh_from_db()
    assert event.status == ModerationStatus.PENDING  # noqa: S101


def test_a_viewer_cannot_moderate() -> None:
    viewer = _user_in("viewer")
    event = EventFactory()

    with pytest.raises(PermissionDenied):
        service.approve(event, actor=viewer)


def test_apply_proposal_writes_the_published_row_and_logs_it() -> None:
    editor = _user_in("editor")
    event = EventFactory(
        status=ModerationStatus.PUBLISHED,
        title_es="Original",
        staged_changes={"title_es": "Updated"},
    )

    applied = service.apply_proposal(event, actor=editor)

    event.refresh_from_db()
    assert applied is True  # noqa: S101
    assert event.title_es == "Updated"  # noqa: S101
    assert event.staged_changes is None  # noqa: S101
    assert ModerationAction.objects.filter(subject_id=event.pk).exists()  # noqa: S101


def test_moderation_actions_are_append_only() -> None:
    editor = _user_in("editor")
    service.approve(EventFactory(), actor=editor)

    with pytest.raises(ValidationError):
        ModerationAction.objects.all().update(action="reject")
    with pytest.raises(ValidationError):
        ModerationAction.objects.all().delete()
