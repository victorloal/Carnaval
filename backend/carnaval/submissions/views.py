"""The public submission endpoints (FR-F-01/02, FR-F-22).

A submission is validated by content, re-encoded, stored in quarantine and left
`pending` with `origin = community`. The CAPTCHA, the honeypot and the quotas
are the anti-abuse layer; there is no account and no CSRF cookie to rely on, so
the view is explicitly CSRF-exempt and says why.
"""

from __future__ import annotations

import hashlib

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    parser_classes,
    permission_classes,
)
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from carnaval.accounts.privacy import hash_ip
from carnaval.legal.models import LegalDocType, LegalDocument
from carnaval.submissions import captcha, quotas, storage
from carnaval.submissions.images import ImageValidationError, validate_image
from carnaval.submissions.models import (
    ConsentRecord,
    Submission,
    SubmissionFile,
    SubmissionKind,
)
from carnaval.submissions.serializers import (
    SubmissionCreatedSerializer,
    SubmissionStatusSerializer,
    SubmissionSubmitSerializer,
)
from carnaval.submissions.video import normalise_video


def _bad(detail: str, code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response({"detail": detail}, status=code)


@extend_schema(
    request=SubmissionSubmitSerializer,
    responses={201: SubmissionCreatedSerializer},
)
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def submit(request: Request) -> Response:
    # The honeypot: a filled hidden field is a bot; drop it silently.
    if request.data.get("website"):
        return _bad("rejected")

    if not captcha.verify(
        str(request.data.get("captcha", "")), request.META.get("REMOTE_ADDR")
    ):
        return _bad("captcha verification failed")

    if not request.data.get("rights"):
        return _bad("a rights declaration is required")

    ip_hash = hash_ip(request.META.get("REMOTE_ADDR"))
    if quotas.over_ip_quota(ip_hash) or quotas.over_daily_quota():
        return _bad("submission quota exceeded", status.HTTP_429_TOO_MANY_REQUESTS)

    kind = request.data.get("kind")

    if kind == SubmissionKind.VIDEO_LINK:
        normalised = normalise_video(str(request.data.get("video_url", "")))
        if normalised is None:
            return _bad("only YouTube and Vimeo links are accepted")
        provider, video_id = normalised
        submission = Submission.objects.create(
            kind=SubmissionKind.VIDEO_LINK,
            video_provider=provider,
            video_id=video_id,
            declared_author=str(request.data.get("author", "")),
            description_es=str(request.data.get("description", "")),
        )
    elif kind == SubmissionKind.IMAGE:
        upload = request.FILES.get("file")
        if upload is None:
            return _bad("a file is required")
        data = upload.read()
        if len(data) > int(settings.SUBMISSION_MAX_UPLOAD_BYTES):
            return _bad("the file is larger than the limit")
        try:
            validated = validate_image(data)
        except ImageValidationError as exc:
            return _bad(str(exc))
        storage_key = f"submissions/{hashlib.sha256(validated.body).hexdigest()}"
        storage.save_quarantine(storage_key, validated.body)
        submission = Submission.objects.create(
            kind=SubmissionKind.IMAGE,
            declared_author=str(request.data.get("author", "")),
            description_es=str(request.data.get("description", "")),
        )
        SubmissionFile.objects.create(
            submission=submission,
            quarantine_key=storage_key,
            mime_detected=validated.mime,
            declared_mime=upload.content_type or "",
            content_hash=hashlib.sha256(validated.body).hexdigest(),
            byte_size=len(validated.body),
            width=validated.width,
            height=validated.height,
            exif_stripped=validated.exif_stripped,
        )
    else:
        return _bad("unknown submission kind")

    ConsentRecord.objects.create(
        submission=submission,
        legal_document=LegalDocument.current(LegalDocType.TERMS, "es"),
        ip_hash=ip_hash,
        user_agent_hash=hash_ip(request.META.get("HTTP_USER_AGENT")),
        declaration_rights=True,
        declaration_minor_subject=bool(request.data.get("minor_subject")),
    )

    return Response(
        {"token": submission.public_token, "status": submission.status},
        status=status.HTTP_201_CREATED,
    )


@extend_schema(responses=SubmissionStatusSerializer)
@api_view(["GET"])
@permission_classes([AllowAny])
def submission_status(request: Request, token: str) -> Response:
    submission = Submission.objects.filter(public_token=token).first()
    if submission is None:
        # An invalid token reveals nothing and does not confirm existence.
        return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(
        {
            "status": submission.status,
            "rejection_reason": submission.rejection_reason,
        }
    )
