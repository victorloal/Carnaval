from __future__ import annotations

from django.urls import path

from carnaval.api import search, views

router = views.PublicRouter()
router.register("editions", views.EditionViewSet, basename="edition")
router.register("days", views.DayViewSet, basename="day")
router.register("events", views.EventViewSet, basename="event")
router.register("venues", views.VenueViewSet, basename="venue")
router.register("news", views.NewsItemViewSet, basename="news")
router.register("media", views.MediaAssetViewSet, basename="media")

urlpatterns = [
    *router.urls,
    path("search/", search.search, name="search"),
]
