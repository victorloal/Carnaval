from __future__ import annotations

from carnaval.api import views

router = views.PublicRouter()
router.register("editions", views.EditionViewSet, basename="edition")
router.register("days", views.DayViewSet, basename="day")
router.register("events", views.EventViewSet, basename="event")
router.register("venues", views.VenueViewSet, basename="venue")

urlpatterns = router.urls
