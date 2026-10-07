"""Query filters for the public catalogue (FR-A-11).

`edition` is the edition **year**, because an edition is identified by its year
(FR-A-01) and it makes a stable, human-readable query parameter.
"""

from __future__ import annotations

import django_filters

from carnaval.programme.models import Day, Event, Venue


class DayFilter(django_filters.FilterSet):
    edition = django_filters.NumberFilter(field_name="edition__year")

    class Meta:
        model = Day
        fields = ["edition"]


class EventFilter(django_filters.FilterSet):
    edition = django_filters.NumberFilter(field_name="day__edition__year")
    date_from = django_filters.DateFilter(field_name="day__date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="day__date", lookup_expr="lte")

    class Meta:
        model = Event
        fields = ["edition", "date_from", "date_to"]


class VenueFilter(django_filters.FilterSet):
    class Meta:
        model = Venue
        fields: list[str] = []
