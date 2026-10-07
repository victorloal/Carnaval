"""The content admin and the review queue (FR-C-06/09, roles-permisos.md).

Nothing is registered for a user who lacks the permission, so a fresh install
shows no `pending` content (FR-D-03). The moderation actions call the shared
service; they never write a status directly.
"""

from __future__ import annotations

from typing import Any

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html

from carnaval.ingestion.models import RawDocument
from carnaval.moderation import service
from carnaval.programme.models import Day, Edition, Event, Venue


class ModeratedAdmin(admin.ModelAdmin):
    list_filter = ("status", "origin")
    actions = [
        "approve_selected",
        "reject_selected",
        "unpublish_selected",
        "request_changes_selected",
        "apply_proposal_selected",
    ]

    @admin.action(description="Approve (publish)")
    def approve_selected(self, request: HttpRequest, queryset: Any) -> None:
        count = 0
        for obj in queryset:
            service.approve(obj, actor=request.user, request=request)
            count += 1
        self.message_user(request, f"Approved {count} record(s).")

    @admin.action(description="Reject with a reason")
    def reject_selected(
        self, request: HttpRequest, queryset: Any
    ) -> HttpResponse | None:
        if "reason" not in request.POST:
            # First pass: ask for the reason that a rejection requires.
            return render(
                request,
                "admin/moderation_reject.html",
                {
                    "queryset": queryset,
                    "action": "reject_selected",
                    "opts": self.model._meta,
                },
            )
        reason = request.POST.get("reason", "").strip()
        if not reason:
            self.message_user(request, "A reason is required.", messages.ERROR)
            return None
        count = 0
        for obj in queryset:
            service.reject(obj, actor=request.user, reason=reason, request=request)
            count += 1
        self.message_user(request, f"Rejected {count} record(s).")
        return None

    @admin.action(description="Unpublish (back to pending)")
    def unpublish_selected(self, request: HttpRequest, queryset: Any) -> None:
        count = 0
        for obj in queryset:
            service.unpublish(obj, actor=request.user, request=request)
            count += 1
        self.message_user(request, f"Unpublished {count} record(s).")

    @admin.action(description="Request changes")
    def request_changes_selected(self, request: HttpRequest, queryset: Any) -> None:
        count = 0
        for obj in queryset:
            service.request_changes(obj, actor=request.user, request=request)
            count += 1
        self.message_user(request, f"Requested changes on {count} record(s).")

    @admin.action(description="Apply a staged change to published content")
    def apply_proposal_selected(self, request: HttpRequest, queryset: Any) -> None:
        count = 0
        for obj in queryset:
            if service.apply_proposal(obj, actor=request.user, request=request):
                count += 1
        self.message_user(request, f"Applied {count} staged change(s).")


@admin.register(Edition)
class EditionAdmin(ModeratedAdmin):
    list_display = ("year", "title_es", "status", "origin", "reviewed_at")
    search_fields = ("title_es", "slug")


@admin.register(Day)
class DayAdmin(ModeratedAdmin):
    list_display = ("date", "label_es", "edition", "status", "origin")
    search_fields = ("label_es", "slug")


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
