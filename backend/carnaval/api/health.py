"""``/health``: application and database reachability only (FR-D-11).

It discloses no configuration, no version and no counts: a probe that leaks
internals is a reconnaissance endpoint.
"""

from __future__ import annotations

from django.db import connection
from django.db.utils import Error as DatabaseError
from django.http import HttpRequest, JsonResponse


def health(request: HttpRequest) -> JsonResponse:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse(
            {"status": "degraded", "database": "unavailable"}, status=503
        )
    return JsonResponse({"status": "ok", "database": "ok"})
