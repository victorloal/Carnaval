"""The public takedown channel (FR-G-03/04/05)."""

from __future__ import annotations

from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from carnaval.legal.models import ClaimType, TakedownRequest
from carnaval.legal.serializers import (
    TakedownRequestSerializer,
    TakedownResponseSerializer,
)


@extend_schema(
    request=TakedownRequestSerializer,
    responses={201: TakedownResponseSerializer},
)
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def takedown(request: Request) -> Response:
    email = str(request.data.get("email", "")).strip()
    claim = str(request.data.get("claim_type", "")).strip()
    if not email or claim not in ClaimType.values:
        return Response(
            {"detail": "email and a valid claim_type are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    record = TakedownRequest.objects.create(
        requester_name=str(request.data.get("name", "")),
        requester_email=email,
        claim_type=claim,
        evidence_url=str(request.data.get("evidence_url", "")),
        subject_type=str(request.data.get("subject_type", "")),
    )
    return Response({"status": record.status}, status=status.HTTP_201_CREATED)
