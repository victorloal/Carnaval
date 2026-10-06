from django.apps import AppConfig


class IngestionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "carnaval.ingestion"
    verbose_name = "Ingestion"
