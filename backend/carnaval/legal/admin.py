from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.http import HttpRequest

from carnaval.legal.models import LegalDocument, TakedownRequest


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ("doc_type", "version", "locale", "is_current", "effective_from")
    list_filter = ("doc_type", "locale", "is_current")

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        # Once a version has been current it is read-only (FR-G-02).
        if obj is not None and obj.is_current:
            return False
        return super().has_change_permission(request, obj)


@admin.register(TakedownRequest)
class TakedownRequestAdmin(admin.ModelAdmin):
    list_display = ("received_at", "claim_type", "status", "requester_email")
    list_filter = ("claim_type", "status")
    search_fields = ("requester_email",)
