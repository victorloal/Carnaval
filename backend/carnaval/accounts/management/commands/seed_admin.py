"""Create the first administrator (FR-D-14).

The account is a **staff user in the `admin` group, never a superuser**:
`is_superuser` bypasses every check in `roles-permisos.md` and would make the
matrix decorative for the one account that matters most.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the first administrator as a staff user in the admin group."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("username")
        parser.add_argument("--email", default="")
        parser.add_argument(
            "--password",
            default="",
            help="Required when the user does not exist yet.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        user_model = get_user_model()
        username: str = options["username"]
        user = user_model.objects.filter(username=username).first()

        if user is None:
            password: str = options["password"]
            if not password:
                raise CommandError(
                    "--password is required to create a new administrator."
                )
            user = user_model.objects.create_user(
                username=username, email=options["email"], password=password
            )

        user.is_staff = True
        user.is_superuser = False
        user.save(update_fields=["is_staff", "is_superuser"])

        group, _ = Group.objects.get_or_create(name="admin")
        user.groups.add(group)

        self.stdout.write(
            self.style.SUCCESS(
                f"{username} is a staff user in 'admin' (not a superuser)."
            )
        )
