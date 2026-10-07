"""Full-text search over published events and news (FR-I-01/02/03).

On PostgreSQL it uses the documented `SearchVector`/`SearchRank`; on the SQLite
development database it falls back to `icontains`, because `django.contrib.postgres`
needs the extension-aware backend. The visibility rule is the same either way:
**only `published` rows are searched.**
"""

from __future__ import annotations

from typing import Any

from django.db import connection
from django.db.models import Q, QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from carnaval.api.serializers import SearchResponseSerializer
from carnaval.core.models import ModerationStatus
from carnaval.editorial.models import NewsItem
from carnaval.programme.models import Event


def _search(queryset: QuerySet[Any], fields: list[str], query: str) -> QuerySet[Any]:
    if connection.vendor == "postgresql":
        from django.contrib.postgres.search import (
            SearchQuery,
            SearchRank,
            SearchVector,
        )

        vector = SearchVector(*fields)
        ranked: QuerySet[Any] = (
            queryset.annotate(rank=SearchRank(vector, SearchQuery(query)))
            .filter(rank__gt=0.01)
            .order_by("-rank")
        )
        return ranked
    condition = Q()
    for field in fields:
        condition |= Q(**{f"{field}__icontains": query})
    return queryset.filter(condition)


@extend_schema(responses=SearchResponseSerializer)
@api_view(["GET"])
@permission_classes([AllowAny])
def search(request: Request) -> Response:
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response({"query": "", "events": [], "news": []})

    events = _search(
        Event.objects.filter(status=ModerationStatus.PUBLISHED),
        ["title_es", "title_en", "description_es", "description_en"],
        query,
    )
    news = _search(
        NewsItem.objects.filter(status=ModerationStatus.PUBLISHED),
        ["headline", "summary_es", "summary_en"],
        query,
    )
    return Response(
        {
            "query": query,
            "events": [
                {
                    "id": str(event.pk),
                    "title_es": event.title_es,
                    "title_en": event.title_en,
                }
                for event in events
            ],
            "news": [{"id": str(item.pk), "headline": item.headline} for item in news],
        }
    )
