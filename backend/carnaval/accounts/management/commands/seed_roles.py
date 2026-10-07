"""Create the three role groups with their permissions (roles-permisos.md)."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from carnaval.accounts.roles import role_permissions


class Command(BaseCommand):
    help = "Create the admin, editor and viewer groups and set their permissions."

    def handle(self, *args: Any, **options: Any) -> None:
        for name, permissions in role_permissions().items():
            group, _ = Group.objects.get_or_create(name=name)
            group.permissions.set(permissions)
            self.stdout.write(
                self.style.SUCCESS(f"{name}: {len(permissions)} permission(s)")
            )
