"""v3 backend: image validation, video links, submissions, status and takedown."""

from __future__ import annotations

import io
from typing import Any

import pytest
from carnaval.core.models import ModerationOrigin, ModerationStatus
from carnaval.legal.models import ClaimType, TakedownRequest, TakedownStatus
from carnaval.submissions.images import ImageValidationError, validate_image
from carnaval.submissions.models import Submission, SubmissionFile
from carnaval.submissions.video import normalise_video
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def _jpeg_with_exif() -> bytes:
    image = Image.new("RGB", (12, 12), "red")
    exif = image.getexif()
    exif[315] = "Some Photographer"  # Artist, IFD0
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", exif=exif)
    return buffer.getvalue()


def _png() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), "blue").save(buffer, format="PNG")
    return buffer.getvalue()


def test_image_validation_strips_exif_and_detects_bytes() -> None:
    validated = validate_image(_jpeg_with_exif())

    assert validated.mime == "image/jpeg"  # noqa: S101
    assert validated.exif_stripped is True  # noqa: S101
    assert validated.width == 12  # noqa: S101
    # The metadata is gone from the re-encoded bytes.
    with Image.open(io.BytesIO(validated.body)) as reopened:
        assert not reopened.getexif()  # noqa: S101


def test_a_non_image_is_rejected() -> None:
    with pytest.raises(ImageValidationError):
        validate_image(b"not an image at all")


def test_a_disallowed_format_is_rejected() -> None:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), "green").save(buffer, format="GIF")

    with pytest.raises(ImageValidationError):
        validate_image(buffer.getvalue())


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", ("youtube", "dQw4w9WgXcQ")),
        ("https://youtu.be/dQw4w9WgXcQ", ("youtube", "dQw4w9WgXcQ")),
        ("https://vimeo.com/123456789", ("vimeo", "123456789")),
        ("https://example.org/watch?v=x", None),
        ("not a url", None),
    ],
)
def test_video_normalisation(url: str, expected: Any) -> None:
    assert normalise_video(url) == expected  # noqa: S101


def test_a_video_submission_is_created_pending_and_community() -> None:
    response = APIClient().post(
        "/api/submissions/",
        {
            "kind": "video_link",
            "video_url": "https://vimeo.com/123456789",
            "rights": True,
            "author": "Nobody",
        },
        format="json",
    )

    assert response.status_code == 201  # noqa: S101
    submission = Submission.objects.get(public_token=response.json()["token"])
    assert submission.status == ModerationStatus.PENDING  # noqa: S101
    assert submission.origin == ModerationOrigin.COMMUNITY  # noqa: S101
    assert submission.video_provider == "vimeo"  # noqa: S101
    assert submission.video_id == "123456789"  # noqa: S101


def test_an_image_submission_is_stored_in_quarantine(
    tmp_path: Any, settings: Any
) -> None:
    settings.SUBMISSION_QUARANTINE_ROOT = str(tmp_path)
    client = APIClient()

    response = client.post(
        "/api/submissions/",
        {
            "kind": "image",
            "rights": True,
            "file": SimpleUploadedFile("photo.jpg", _png(), content_type="image/png"),
        },
        format="multipart",
    )

    assert response.status_code == 201  # noqa: S101
    file = SubmissionFile.objects.get()
    assert file.exif_stripped is True  # noqa: S101
    assert file.mime_detected == "image/png"  # noqa: S101
    assert (tmp_path / file.quarantine_key).exists()  # noqa: S101


def test_a_submission_without_a_rights_declaration_is_refused() -> None:
    response = APIClient().post(
        "/api/submissions/",
        {"kind": "video_link", "video_url": "https://vimeo.com/1"},
        format="json",
    )

    assert response.status_code == 400  # noqa: S101


def test_the_honeypot_drops_a_bot() -> None:
    response = APIClient().post(
        "/api/submissions/",
        {
            "kind": "video_link",
            "video_url": "https://vimeo.com/1",
            "rights": True,
            "website": "http://spam.example",
        },
        format="json",
    )

    assert response.status_code == 400  # noqa: S101
    assert not Submission.objects.exists()  # noqa: S101


def test_the_per_ip_quota_is_enforced(settings: Any) -> None:
    settings.SUBMISSION_IP_QUOTA_PER_HOUR = 1
    client = APIClient()
    payload = {
        "kind": "video_link",
        "video_url": "https://vimeo.com/1",
        "rights": True,
    }

    assert client.post("/api/submissions/", payload, format="json").status_code == 201  # noqa: S101
    assert client.post("/api/submissions/", payload, format="json").status_code == 429  # noqa: S101


def test_submission_status_lookup() -> None:
    client = APIClient()
    created = client.post(
        "/api/submissions/",
        {"kind": "video_link", "video_url": "https://vimeo.com/1", "rights": True},
        format="json",
    ).json()

    found = client.get(f"/api/submissions/{created['token']}/")
    assert found.status_code == 200  # noqa: S101
    assert found.json()["status"] == ModerationStatus.PENDING  # noqa: S101
    assert client.get("/api/submissions/does-not-exist/").status_code == 404  # noqa: S101


def test_an_illegal_content_takedown_is_escalated() -> None:
    response = APIClient().post(
        "/takedown/",
        {"email": "someone@example.org", "claim_type": ClaimType.ILLEGAL_CONTENT},
        format="json",
    )

    assert response.status_code == 201  # noqa: S101
    record = TakedownRequest.objects.get()
    assert record.status == TakedownStatus.ESCALATED  # noqa: S101
