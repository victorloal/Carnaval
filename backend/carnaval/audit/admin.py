from __future__ import annotations

from typing import Any

from django.contrib import admin

from carnaval.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "actor",
        "actor_kind",
        "action",
        "object_type",
        "object_id",
    )
    list_filter = ("actor_kind", "action")
    search_fields = ("action", "object_type")
    readonly_fields = tuple(field.name for field in AuditLog._meta.fields)

    def has_add_permission(self, request: Any) -> bool:
        return False

    def has_change_permission(self, request: Any, obj: Any = None) -> bool:
        return False

    def has_delete_permission(self, request: Any, obj: Any = None) -> bool:
        return False
