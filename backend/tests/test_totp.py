"""TOTP is required for the console; the login form is OTP-aware (SEC-04)."""

from __future__ import annotations

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client
from django_otp.admin import OTPAdminAuthenticationForm

pytestmark = pytest.mark.django_db


def test_the_admin_login_form_is_otp_aware() -> None:
    assert admin.site.login_form is OTPAdminAuthenticationForm  # noqa: S101


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
