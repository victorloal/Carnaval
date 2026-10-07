from django.apps import AppConfig


class PrivacyConfig(AppConfig):
    """Retention enforcement for personal data (PRV-03, ADR 0018).

    No models: this app owns the purge command and the retention defaults.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "carnaval.privacy"
