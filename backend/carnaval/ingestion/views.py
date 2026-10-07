"""Stream a stored raw payload to a reviewer (FR-C-09, matrix row 11).

Only a user with `view_rawdocument` may read it: the payload is third-party
material that LEG-05 and ADR 0004 keep out of unlicensed circulation.
"""

from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from carnaval.ingestion import storage
from carnaval.ingestion.models import RawDocument


@staff_member_required
def raw_payload(request: HttpRequest, pk: str) -> HttpResponse:
    document = get_object_or_404(RawDocument, pk=pk)
    if not request.user.has_perm("ingestion.view_rawdocument"):
        raise PermissionDenied("missing permission ingestion.view_rawdocument")
    body = storage.read_payload(document.storage_key)
    response = HttpResponse(
        body, content_type=document.content_type or "application/octet-stream"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{document.content_hash[:12]}.bin"'
    )
    return response
