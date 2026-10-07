"""Enrol a confirmed TOTP device for a user and print its provisioning URL.

Django admin has no bootstrap for the first device: an `admin`-group user must
already own a confirmed device before the console accepts them, so the maintainer
enrols it here. Recovery codes come from `django-otp`'s `otp_static` app.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice


class Command(BaseCommand):
    help = "Enrol a confirmed TOTP device for a user and print the provisioning URL."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("username")
        parser.add_argument(
            "--name", default="default", help="Device label (default: default)."
        )

    def handle(self, *args: Any, **options: Any) -> None:
        user = get_user_model().objects.filter(username=options["username"]).first()
        if user is None:
            raise CommandError(f"no user named {options['username']!r}")

        device, _ = TOTPDevice.objects.get_or_create(user=user, name=options["name"])
        device.confirmed = True
        device.save()
        # A static device holds the single-use recovery codes (SEC-05).
        StaticDevice.objects.get_or_create(user=user, name="recovery")

        self.stdout.write(
            self.style.SUCCESS(f"TOTP enrolled for {user.get_username()}.")
        )
        self.stdout.write(f"Provisioning URL: {device.config_url}")
