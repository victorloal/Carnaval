"""Source type -> transform. HTML and PDF are interfaces, not parsers yet.

A source whose type has no working transform fails loudly rather than silently
producing nothing.
"""

from __future__ import annotations

from carnaval.ingestion.exceptions import TransformError
from carnaval.ingestion.http import FetchedPayload
from carnaval.ingestion.models import ScrapeSource, SourceType
from carnaval.ingestion.transforms import Transform, TransformReport, wp_api


def _not_implemented(source_type: str) -> Transform:
    def transform(payload: FetchedPayload, source: ScrapeSource) -> TransformReport:
        raise TransformError(
            f"no transform implemented for source_type={source_type!r} yet"
        )

    return transform


TRANSFORMS: dict[str, Transform] = {
    SourceType.WP_API: wp_api.transform,
    SourceType.HTML: _not_implemented(SourceType.HTML),
    SourceType.PDF: _not_implemented(SourceType.PDF),
}
