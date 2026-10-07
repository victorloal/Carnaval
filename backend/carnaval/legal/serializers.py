"""Request and response shapes for the takedown endpoint (schema only)."""

from __future__ import annotations

from rest_framework import serializers

from carnaval.legal.models import ClaimType


class TakedownRequestSerializer(serializers.Serializer[object]):
    email = serializers.EmailField()
    claim_type = serializers.ChoiceField(choices=ClaimType.choices)
    name = serializers.CharField(required=False, allow_blank=True)
    evidence_url = serializers.URLField(required=False, allow_blank=True)
    subject_type = serializers.CharField(required=False, allow_blank=True)


class TakedownResponseSerializer(serializers.Serializer[object]):
    status = serializers.CharField()
