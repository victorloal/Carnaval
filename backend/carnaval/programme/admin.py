"""The content admin and the review queue (FR-C-06/09, roles-permisos.md).

Nothing is registered for a user who lacks the permission, so a fresh install
shows no `pending` content (FR-D-03). The moderation actions live in
`carnaval.moderation.admin`.
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from carnaval.ingestion.models import RawDocument
from carnaval.moderation.admin import ModeratedAdmin
from carnaval.programme.models import Day, Edition, Event, Venue


@admin.register(Edition)
class EditionAdmin(ModeratedAdmin):
    list_display = ("year", "title_es", "status", "origin", "reviewed_at")
    search_fields = ("title_es", "slug_es", "slug_en")


@admin.register(Day)
class DayAdmin(ModeratedAdmin):
    list_display = ("date", "label_es", "edition", "status", "origin")
    search_fields = ("label_es", "slug_es", "slug_en")


@admin.register(Venue)
class VenueAdmin(ModeratedAdmin):
    list_display = ("name_es", "city", "status", "origin")
    search_fields = ("name_es",)


@admin.register(Event)
class EventAdmin(ModeratedAdmin):
    list_display = (
        "title_es",
        "day",
        "status",
        "origin",
        "source_url",
        "raw_payload_link",
    )
    search_fields = ("title_es", "source_url")
    readonly_fields = (
        "id",
        "ingestion_run",
        "staged_changes",
        "reviewed_by",
        "reviewed_at",
        "raw_payload_link",
    )

    @admin.display(description="Raw payload")
    def raw_payload_link(self, obj: Event) -> str:
        """Surface the stored payload behind a pending record (FR-C-09)."""
        run = obj.ingestion_run
        if run is None or run.scrape_source_id is None:
            return "—"
        document = (
            RawDocument.objects.filter(scrape_source_id=run.scrape_source_id)
            .order_by("-fetched_at")
            .first()
        )
        if document is None:
            return "—"
        url = reverse("raw-payload", args=[document.pk])
        return format_html('<a href="{}">view</a>', url)
