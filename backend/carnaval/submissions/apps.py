from __future__ import annotations

from django.apps import AppConfig


class SubmissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "carnaval.submissions"
    verbose_name = "Public submissions"
