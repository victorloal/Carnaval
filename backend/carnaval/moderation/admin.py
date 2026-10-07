"""The moderation admin actions, shared by every moderated model.

The actions only call `carnaval.moderation.service`; they never write a status
directly.
"""

from __future__ import annotations

from typing import Any

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from carnaval.moderation import service


class ModeratedAdmin(admin.ModelAdmin):
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
