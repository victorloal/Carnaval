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
        #
        # The template must move with the form: Django's own `admin/login.html`
        # only renders username and password, so the OTP field would never
        # appear and `OTPAdminAuthenticationForm.clean_otp` would reject every
        # login with "enter your OTP token" — with no input to enter it into.
        # django-otp ships the matching template (and its own `es` catalog, so
        # the label stays Spanish per FR-H-08).
        from django.contrib import admin
        from django_otp.admin import OTPAdminAuthenticationForm

        admin.site.login_form = OTPAdminAuthenticationForm
        admin.site.login_template = "otp/admin111/login.html"

        from carnaval.accounts import signals  # noqa: F401  (connects receivers)
