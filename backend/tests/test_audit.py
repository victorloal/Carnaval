"""`audit_logs` is append-only and records the auth events (FR-D-08/09/10)."""

from __future__ import annotations

import pytest
from carnaval.audit import services
from carnaval.audit.models import AuditLog
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import Client

pytestmark = pytest.mark.django_db


def test_an_audit_log_cannot_be_changed_or_deleted() -> None:
    log = services.record(action="test")
    log.changes = {"tampered": True}

    with pytest.raises(ValidationError):
        log.save()
    with pytest.raises(ValidationError):
        AuditLog.objects.all().update(action="other")
    with pytest.raises(ValidationError):
        AuditLog.objects.all().delete()


def test_only_the_view_permission_exists() -> None:
    codenames = set(
        Permission.objects.filter(content_type__app_label="audit").values_list(
            "codename", flat=True
        )
    )

    assert codenames == {"view_auditlog"}  # noqa: S101


def test_a_successful_login_is_audited() -> None:
    user = get_user_model().objects.create_user(username="a", password="pw")  # noqa: S106
    client = Client()

    assert client.login(username="a", password="pw") is True  # noqa: S101, S106
    assert AuditLog.objects.filter(action="login", actor=user).exists()  # noqa: S101


def test_a_failed_login_is_audited() -> None:
    get_user_model().objects.create_user(username="a", password="pw")  # noqa: S106

    Client().login(username="a", password="wrong")  # noqa: S106

    assert AuditLog.objects.filter(action="login_failed").exists()  # noqa: S101
