from __future__ import annotations

from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "carnaval.audit"
    verbose_name = "Audit trail"

    def ready(self) -> None:
        from carnaval.audit import signals  # noqa: F401  (connects the receivers)
