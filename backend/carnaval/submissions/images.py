"""Image validation: by magic bytes, never by extension (FR-F-03/04/05/06).

Pillow detects the format from the bytes; the image is then fully decoded and
**re-encoded**, which is what strips an embedded payload and every EXIF tag
including GPS. `exif_stripped` is verified, not assumed.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

from PIL import Image, ImageOps, UnidentifiedImageError

ALLOWED_FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


class ImageValidationError(Exception):
    """The bytes are not an allowed image."""


@dataclass(frozen=True)
class ValidatedImage:
    body: bytes
    mime: str
    width: int
    height: int
    exif_stripped: bool


def validate_image(data: bytes) -> ValidatedImage:
    if not data:
        raise ImageValidationError("empty file")
    try:
        with Image.open(io.BytesIO(data)) as probe:
            fmt = probe.format
    except UnidentifiedImageError as exc:
        raise ImageValidationError("content is not a recognised image") from exc

    if fmt not in ALLOWED_FORMATS:
        raise ImageValidationError(f"image format {fmt} is not allowed")

    mime = ALLOWED_FORMATS[fmt]
    try:
        with Image.open(io.BytesIO(data)) as image:
            # Apply EXIF orientation before discarding the metadata.
            oriented = ImageOps.exif_transpose(image) or image
            mode = "RGB" if fmt == "JPEG" else oriented.mode
            converted = oriented.convert(mode) if mode != oriented.mode else oriented
            buffer = io.BytesIO()
            converted.save(buffer, format=fmt)
            body = buffer.getvalue()
            width, height = converted.size
    except OSError as exc:
        raise ImageValidationError("the image could not be fully decoded") from exc

    # Verify the metadata is gone rather than trusting the re-encode.
    with Image.open(io.BytesIO(body)) as check:
        exif_stripped = not check.getexif()
    if not exif_stripped:
        raise ImageValidationError("EXIF metadata survived re-encoding")

    return ValidatedImage(
        body=body, mime=mime, width=width, height=height, exif_stripped=exif_stripped
    )
