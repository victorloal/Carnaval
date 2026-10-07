from __future__ import annotations

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "carnaval.accounts"
    verbose_name = "Accounts and access"

    def ready(self) -> None:
        # The admin login form gains a TOTP field for users who have a device
        # (SEC-04). Replacing the form is safer than swapping the whole
        # AdminSite, which would drop every registration done by other apps.
        from django.contrib import admin
        from django_otp.admin import OTPAdminAuthenticationForm

        admin.site.login_form = OTPAdminAuthenticationForm

        from carnaval.accounts import signals  # noqa: F401  (connects receivers)
