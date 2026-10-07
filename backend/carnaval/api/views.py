"""The public read API: published-only, read-only, rate-limited.

Every queryset starts from ``status = published``, so a ``pending`` or
``rejected`` row is a 404, not a redacted 200. The viewsets are read-only and
opt in to ``AllowAny`` explicitly; the project default stays fail-closed.
"""

from __future__ import annotations

from typing import Any

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from rest_framework import routers
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from carnaval.api import filters, serializers
from carnaval.core.models import ModerationStatus
from carnaval.editorial.models import MediaAsset, NewsItem
from carnaval.programme.models import Day, Edition, Event, Venue


@method_decorator(cache_control(public=True, max_age=300), name="list")
@method_decorator(cache_control(public=True, max_age=300), name="retrieve")
class PublishedReadOnlyViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self) -> Any:
        queryset = super().get_queryset()
        return queryset.filter(status=ModerationStatus.PUBLISHED)


class EditionViewSet(PublishedReadOnlyViewSet):
    queryset = Edition.objects.all()
    serializer_class = serializers.EditionSerializer
    filterset_fields = ["year"]


class DayViewSet(PublishedReadOnlyViewSet):
    queryset = Day.objects.all()
    serializer_class = serializers.DaySerializer
    filterset_class = filters.DayFilter


class EventViewSet(PublishedReadOnlyViewSet):
    queryset = Event.objects.select_related("day", "venue")
    serializer_class = serializers.EventSerializer
    filterset_class = filters.EventFilter


class VenueViewSet(PublishedReadOnlyViewSet):
    queryset = Venue.objects.all()
    serializer_class = serializers.VenueSerializer


class NewsItemViewSet(PublishedReadOnlyViewSet):
    queryset = NewsItem.objects.all()
    serializer_class = serializers.NewsItemSerializer


class MediaAssetViewSet(PublishedReadOnlyViewSet):
    queryset = MediaAsset.objects.all()
    serializer_class = serializers.MediaAssetSerializer


class PublicAPIRootView(routers.APIRootView):
    permission_classes = [AllowAny]


class PublicRouter(routers.DefaultRouter):
    APIRootView = PublicAPIRootView
