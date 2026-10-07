"""Request and response shapes for the submission endpoints (schema only)."""

from __future__ import annotations

from rest_framework import serializers

from carnaval.submissions.models import SubmissionKind


class SubmissionSubmitSerializer(serializers.Serializer[object]):
    kind = serializers.ChoiceField(choices=SubmissionKind.choices)
    rights = serializers.BooleanField()
    video_url = serializers.URLField(required=False, allow_blank=True)
    author = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    minor_subject = serializers.BooleanField(required=False)
    captcha = serializers.CharField(required=False, allow_blank=True)
    website = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=False)


class SubmissionCreatedSerializer(serializers.Serializer[object]):
    token = serializers.CharField()
    status = serializers.CharField()


class SubmissionStatusSerializer(serializers.Serializer[object]):
    status = serializers.CharField()
    rejection_reason = serializers.CharField(allow_blank=True)
