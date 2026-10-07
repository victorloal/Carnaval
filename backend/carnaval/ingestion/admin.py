from __future__ import annotations

from typing import Any

from django.contrib import admin

from carnaval.ingestion.models import IngestionRun, RawDocument, ScrapeSource


@admin.register(ScrapeSource)
class ScrapeSourceAdmin(admin.ModelAdmin):
    """The circuit-breaker state, shown as FR-D-12 requires."""

    list_display = (
        "name",
        "source_type",
        "is_active",
        "consecutive_failures",
        "last_success_at",
        "last_failure_at",
    )
    list_filter = ("source_type", "is_active")
    search_fields = ("name", "url")
    readonly_fields = (
        "consecutive_failures",
        "last_success_at",
        "last_failure_at",
        "last_error",
    )


@admin.register(RawDocument)
class RawDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "content_hash",
        "scrape_source",
        "http_status",
        "byte_size",
        "fetched_at",
    )
    list_filter = ("scrape_source",)
    readonly_fields = tuple(field.name for field in RawDocument._meta.fields)

    def has_add_permission(self, request: Any) -> bool:
        return False

    def has_change_permission(self, request: Any, obj: Any = None) -> bool:
        return False


@admin.register(IngestionRun)
class IngestionRunAdmin(admin.ModelAdmin):
    list_display = ("started_at", "scrape_source", "trigger", "status", "finished_at")
    list_filter = ("trigger", "status")
    readonly_fields = tuple(field.name for field in IngestionRun._meta.fields)

    def has_add_permission(self, request: Any) -> bool:
        return False

    def has_change_permission(self, request: Any, obj: Any = None) -> bool:
        return False
