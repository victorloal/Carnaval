"""TOTP is required for the console; the login form is OTP-aware (SEC-04)."""

from __future__ import annotations

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import Client
from django_otp.admin import OTPAdminAuthenticationForm
from django_otp.oath import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice

pytestmark = pytest.mark.django_db


def test_the_admin_login_form_is_otp_aware() -> None:
    assert admin.site.login_form is OTPAdminAuthenticationForm  # noqa: S101


def test_the_login_page_renders_the_otp_field() -> None:
    """SEC-04: the form is useless if the template cannot draw its token field.

    Swapping `admin.site.login_form` without swapping `admin.site.login_template`
    left the console unreachable: `clean_otp` demanded a token that Django's own
    `admin/login.html` never rendered.
    """
    content = Client().get("/admin/login/").content.decode()

    assert 'name="otp_token"' in content  # noqa: S101


def _enrol(username: str, password: str) -> str:
    """Create a staff admin in the `admin` group and return a valid TOTP token."""
    user = get_user_model().objects.create_user(
        username=username,
        password=password,
        is_staff=True,
    )
    user.groups.add(Group.objects.get_or_create(name="admin")[0])
    call_command("enrol_totp", username)
    device = TOTPDevice.objects.get(user=user, name="default")
    totp = TOTP(device.bin_key, device.step, device.t0, device.digits, device.drift)
    return str(totp.token())


def test_an_admin_logs_in_with_password_and_a_totp_token() -> None:
    token = _enrol("adm", "pw")
    client = Client()

    response = client.post(
        "/admin/login/",
        {"username": "adm", "password": "pw", "otp_token": token, "next": "/admin/"},
    )

    assert response.status_code == 302  # noqa: S101
    assert response.headers["Location"] == "/admin/"  # noqa: S101
    # The console is actually reachable once authenticated.
    assert client.get("/admin/").status_code == 200  # noqa: S101


def test_a_bare_login_lands_on_the_console() -> None:
    """Without `next`, Django falls back to LOGIN_REDIRECT_URL (a 404 by default)."""
    token = _enrol("adm", "pw")

    response = Client().post(
        "/admin/login/",
        {"username": "adm", "password": "pw", "otp_token": token},
    )

    assert response.status_code == 302  # noqa: S101
    assert response.headers["Location"] == "/admin/"  # noqa: S101


def test_a_user_without_a_device_cannot_log_in() -> None:
    """Enrolment is a management command, not a first-login wizard (`enrol_totp`).

    Without a device the password alone is not enough, and the refusal is a form
    error, never a server error.
    """
    get_user_model().objects.create_user(
        username="adm",
        password="pw",  # noqa: S106
        is_staff=True,
    )

    client = Client()
    response = client.post(
        "/admin/login/",
        {"username": "adm", "password": "pw", "otp_token": "000000"},
    )

    assert response.status_code == 200  # noqa: S101
    assert "_auth_user_id" not in client.session  # noqa: S101


def test_an_unverified_admin_is_sent_to_step_up() -> None:
    user = get_user_model().objects.create_user(
        username="adm",
        password="pw",  # noqa: S106
        is_staff=True,  # noqa: S106
    )
    user.groups.add(Group.objects.get_or_create(name="admin")[0])
    client = Client()
    client.force_login(user)

    response = client.get("/admin/")

    assert response.status_code == 302  # noqa: S101
    assert response["Location"] == "/accounts/step-up/"  # noqa: S101


def test_the_console_is_not_indexed_and_has_no_signup() -> None:
    client = Client()

    assert client.get("/admin/login/").headers["X-Robots-Tag"] == "noindex, nofollow"  # noqa: S101
    # FR-D-13: there is no public signup path.
    assert client.get("/signup/").status_code == 404  # noqa: S101


def test_the_admin_is_spanish_while_the_api_surface_stays_english() -> None:
    from django.conf import settings

    content = Client().get("/admin/login/").content.decode()

    assert settings.LANGUAGE_CODE == "en-us"  # noqa: S101
    assert "Contraseña" in content  # noqa: S101
