"""Retention enforcement: the purge command honours the ADR 0018 periods."""

from __future__ import annotations

from datetime import timedelta

import pytest
from carnaval.audit import services as audit
from carnaval.audit.models import AuditLog
from carnaval.core.models import ModerationStatus
from carnaval.ingestion.models import IngestionRun
from carnaval.submissions.models import ConsentRecord
from django.core.management import call_command
from django.utils import timezone

from tests.factories import (
    ConsentRecordFactory,
    IngestionRunFactory,
    SubmissionFactory,
    TakedownRequestFactory,
)

pytestmark = pytest.mark.django_db


def test_contact_email_is_cleared_after_its_period() -> None:
    old = SubmissionFactory(
        status=ModerationStatus.PUBLISHED,
        reviewed_at=timezone.now() - timedelta(days=400),
    )
    recent = SubmissionFactory(
        status=ModerationStatus.PUBLISHED,
        reviewed_at=timezone.now() - timedelta(days=10),
    )
    pending = SubmissionFactory()  # never decided, so its email stays

    call_command("purge_personal_data")

    old.refresh_from_db()
    recent.refresh_from_db()
    pending.refresh_from_db()
    assert old.contact_email == ""  # noqa: S101
    assert recent.contact_email != ""  # noqa: S101
    assert pending.contact_email != ""  # noqa: S101


def test_consent_records_are_deleted_after_two_years() -> None:
    old = ConsentRecordFactory()
    recent = ConsentRecordFactory()
    ConsentRecord.objects.filter(pk=old.pk).update(
        accepted_at=timezone.now() - timedelta(days=800)
    )

    call_command("purge_personal_data")

    assert not ConsentRecord.objects.filter(pk=old.pk).exists()  # noqa: S101
    assert ConsentRecord.objects.filter(pk=recent.pk).exists()  # noqa: S101


def test_takedown_email_is_cleared_only_after_a_reply() -> None:
    responded = TakedownRequestFactory(
        responded_at=timezone.now() - timedelta(days=800)
    )
    waiting = TakedownRequestFactory()

    call_command("purge_personal_data")

    responded.refresh_from_db()
    waiting.refresh_from_db()
    assert responded.requester_email == ""  # noqa: S101
    assert waiting.requester_email != ""  # noqa: S101


def test_ingestion_runs_are_pruned_after_a_year() -> None:
    old = IngestionRunFactory()
    IngestionRun.objects.filter(pk=old.pk).update(
        started_at=timezone.now() - timedelta(days=400)
    )
    recent = IngestionRunFactory()

    call_command("purge_personal_data")

    assert not IngestionRun.objects.filter(pk=old.pk).exists()  # noqa: S101
    assert IngestionRun.objects.filter(pk=recent.pk).exists()  # noqa: S101


def test_the_audit_trail_is_never_purged() -> None:
    audit.record(action="approve")

    call_command("purge_personal_data")

    assert AuditLog.objects.count() == 1  # noqa: S101


def test_dry_run_changes_nothing() -> None:
    old = SubmissionFactory(
        status=ModerationStatus.PUBLISHED,
        reviewed_at=timezone.now() - timedelta(days=400),
    )

    call_command("purge_personal_data", "--dry-run")

    old.refresh_from_db()
    assert old.contact_email != ""  # noqa: S101
