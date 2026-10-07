"""Read-only serializers for the public catalogue.

Bilingual fields are exposed as `*_es` and `*_en`; the client falls back to the
source locale (FR-H-06, ADR 0012). The serializers expose no moderation fields:
what is not `published` is not in the queryset at all.
"""

from __future__ import annotations

from rest_framework import serializers

from carnaval.programme.models import Day, Edition, Event, Venue


class EditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edition
        fields = [
            "id",
            "year",
            "slug",
            "title_es",
            "title_en",
            "starts_on",
            "ends_on",
            "summary_es",
            "summary_en",
        ]


class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = ["id", "edition", "date", "slug", "label_es", "label_en"]


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = [
            "id",
            "name_es",
            "name_en",
            "address",
            "city",
            "latitude",
            "longitude",
            "capacity",
        ]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "day",
            "venue",
            "starts_at",
            "ends_at",
            "title_es",
            "title_en",
            "description_es",
            "description_en",
            "sort_order",
            "source_url",
        ]
