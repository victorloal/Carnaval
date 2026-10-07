from __future__ import annotations

from django.apps import AppConfig


class EditorialConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "carnaval.editorial"
    verbose_name = "Editorial content"
