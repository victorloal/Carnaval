from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode

from carnaval.accounts import sessions, stepup, throttle


@admin.action(description="Revoke all sessions of the selected users")
def revoke_sessions(modeladmin: Any, request: HttpRequest, queryset: Any) -> None:
    total = sum(sessions.revoke_sessions(user) for user in queryset)
    modeladmin.message_user(request, f"Revoked {total} session(s).")


@admin.action(description="Clear the login throttle of the selected users")
def unlock_account(modeladmin: Any, request: HttpRequest, queryset: Any) -> None:
    for user in queryset:
        throttle.reset(user.get_username(), "")
    modeladmin.message_user(request, "Login throttle cleared.")


class UserAdmin(BaseUserAdmin):
    # No bulk delete of accounts: FR-D-30 is create/deactivate, not delete.
    actions = [revoke_sessions, unlock_account]


class GroupAdmin(BaseGroupAdmin):
    def change_view(
        self,
        request: HttpRequest,
        object_id: str,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        if not stepup.is_stepped_up(request):
            target = reverse("step-up")
            return redirect(f"{target}?{urlencode({'next': request.path})}")
        return super().change_view(request, object_id, form_url, extra_context)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
