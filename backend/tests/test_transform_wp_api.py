"""The WordPress REST API transform (FR-B-01/15, and the two source traps)."""

from __future__ import annotations

import hashlib
import json
from datetime import date

import pytest
from carnaval.ingestion.exceptions import TransformError
from carnaval.ingestion.http import FetchedPayload
from carnaval.ingestion.transforms import wp_api

from tests import fixture_data
from tests.factories import ScrapeSourceFactory

pytestmark = pytest.mark.django_db


def _payload(body: bytes) -> FetchedPayload:
    return FetchedPayload(
        url="https://carnavaldepasto.org/wp-json/wp/v2/posts",
        http_status=200,
        content_type="application/json",
        body=body,
        sha256=hashlib.sha256(body).hexdigest(),
    )


def test_fixture_maps_the_five_canonical_days() -> None:
    body, _ = fixture_data.load("carnavaldepasto", "wp_posts")

    report = wp_api.transform(_payload(body), ScrapeSourceFactory())

    days = {candidate.day_date for candidate in report.candidates}
    assert len(report.candidates) == 5  # noqa: S101
    assert report.posts_seen == 5  # noqa: S101
    assert date(2020, 1, 5) in days  # noqa: S101
    # The `6 de enero` trap: it is a root category, not a child of DIAS.
    assert date(2020, 1, 6) in days  # noqa: S101
    first = report.candidates[0]
    assert first.source_record_key == "101"  # noqa: S101
    assert first.year == 2020  # noqa: S101
    assert first.source_url.startswith("https://carnavaldepasto.org/")  # noqa: S101


def test_day_comes_from_the_category_and_year_from_the_date() -> None:
    """A post dated in October but labelled `2 de enero` is January, year 2024."""
    post = {
        "id": 900,
        "date": "2024-10-21T10:00:00",
        "slug": "2-de-enero",
        "link": "https://carnavaldepasto.org/2-de-enero/",
        "title": {"rendered": "2 de enero"},
        "_embedded": {
            "wp:term": [
                [{"taxonomy": "category", "name": "2 de enero", "slug": "2-de-enero"}]
            ]
        },
    }
    body = json.dumps([post]).encode("utf-8")

    report = wp_api.transform(_payload(body), ScrapeSourceFactory())

    assert report.candidates[0].day_date == date(2024, 1, 2)  # noqa: S101


def test_a_post_missing_a_required_field_is_rejected() -> None:
    post = {"id": 1, "date": "2020-01-05T09:00:00", "title": {"rendered": "x"}}
    body = json.dumps([post]).encode("utf-8")

    report = wp_api.transform(_payload(body), ScrapeSourceFactory())

    assert report.candidates == []  # noqa: S101
    assert report.rejected == 1  # noqa: S101
    assert report.field_hits["link"] == 0  # noqa: S101


def test_a_non_json_payload_raises() -> None:
    with pytest.raises(TransformError):
        wp_api.transform(_payload(b"<html>not json</html>"), ScrapeSourceFactory())
