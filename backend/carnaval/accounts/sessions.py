"""Central session revocation (SEC-08).

Django does not index sessions by user, so this walks the unexpired ones and
discards those whose decoded payload belongs to the account. The admin pool is
tiny; a large deployment would keep an index instead.
"""

from __future__ import annotations

from typing import Any

from django.contrib.sessions.models import Session
from django.utils import timezone


def revoke_sessions(user: Any) -> int:
    removed = 0
    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        if session.get_decoded().get("_auth_user_id") == str(user.pk):
            session.delete()
            removed += 1
    return removed
