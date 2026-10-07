"""Roles, seed commands, throttling, sessions and step-up (v1 / Sprint 08a)."""

from __future__ import annotations

from typing import Any

import pytest
from carnaval.accounts import sessions, throttle
from carnaval.accounts.backends import ThrottledModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import Client
from django.utils import timezone
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice

pytestmark = pytest.mark.django_db


def test_seed_roles_creates_the_three_groups() -> None:
    call_command("seed_roles")

    assert set(Group.objects.values_list("name", flat=True)) == {  # noqa: S101
        "admin",
        "editor",
        "viewer",
    }
    viewer = Group.objects.get(name="viewer")
    assert viewer.permissions.filter(codename="view_event").exists()  # noqa: S101
    # A viewer never gets an editing permission (FR-D-05).
    assert not viewer.permissions.filter(codename="change_event").exists()  # noqa: S101


def test_seed_admin_is_staff_but_not_superuser() -> None:
    call_command("seed_roles")
    call_command("seed_admin", "root", "--password", "s3cret-pass-123")

    user = get_user_model().objects.get(username="root")
    assert user.is_staff is True  # noqa: S101
    assert user.is_superuser is False  # noqa: S101
    assert user.groups.filter(name="admin").exists()  # noqa: S101


def test_enrol_totp_creates_a_confirmed_device() -> None:
    get_user_model().objects.create_user(username="root", password="pw")  # noqa: S106

    call_command("enrol_totp", "root")

    device = TOTPDevice.objects.get(user__username="root")
    assert device.confirmed is True  # noqa: S101
    assert device.config_url.startswith("otpauth://totp/")  # noqa: S101


def test_login_throttle_locks_after_the_threshold(settings: Any) -> None:
    settings.LOGIN_THROTTLE_THRESHOLD = 3
    settings.LOGIN_THROTTLE_BASE_SECONDS = 60
    backend = ThrottledModelBackend()
    get_user_model().objects.create_user(username="a", password="right")  # noqa: S106
    throttle.reset("a", "")

    for _ in range(3):
        assert backend.authenticate(None, username="a", password="wrong") is None  # noqa: S101, S106

    assert throttle.is_locked("a", "") is True  # noqa: S101
    # Even the correct password is refused while the account is locked.
    assert backend.authenticate(None, username="a", password="right") is None  # noqa: S101, S106


def test_revoke_sessions_drops_the_users_sessions() -> None:
    user = get_user_model().objects.create_user(username="a", password="pw")  # noqa: S106
    client = Client()
    client.force_login(user)

    assert sessions.revoke_sessions(user) == 1  # noqa: S101


def test_group_change_requires_a_recent_step_up() -> None:
    call_command("seed_roles")
    user = get_user_model().objects.create_user(
        username="adm",
        password="pw",  # noqa: S106
        is_staff=True,  # noqa: S106
    )
    user.groups.add(Group.objects.get(name="admin"))
    device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)

    client = Client()
    client.force_login(user)
    session = client.session
    session["otp_device_id"] = device.persistent_id
    session.save()

    group = Group.objects.get(name="editor")
    blocked = client.get(f"/admin/auth/group/{group.pk}/change/")
    assert blocked.status_code == 302  # noqa: S101
    assert "/accounts/step-up/" in blocked["Location"]  # noqa: S101

    session = client.session
    session["stepup_at"] = timezone.now().timestamp()
    session.save()
    allowed = client.get(f"/admin/auth/group/{group.pk}/change/")
    assert allowed.status_code == 200  # noqa: S101


def test_step_up_view_accepts_password_and_token() -> None:
    user = get_user_model().objects.create_user(username="adm", password="pw")  # noqa: S106
    user.groups.add(Group.objects.get_or_create(name="admin")[0])
    device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
    token = str(totp(device.bin_key, device.step, device.t0, device.digits))

    client = Client()
    client.force_login(user)
    response = client.post(
        "/accounts/step-up/",
        {"password": "pw", "token": token, "next": "/admin/"},
    )

    assert response.status_code == 302  # noqa: S101
    assert client.session["stepup_at"]  # noqa: S101
