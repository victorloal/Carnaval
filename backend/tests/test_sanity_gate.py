"""The sanity gate turns a markup change into an alarm (FR-B-11, SEC-40)."""

from __future__ import annotations

from datetime import date

from carnaval.ingestion import sanity
from carnaval.ingestion.transforms import EventCandidate, TransformReport

FIELDS = ("id", "date", "title", "link")


def _candidate(index: int, *, year: int = 2020) -> EventCandidate:
    return EventCandidate(
        source_record_key=str(index),
        year=year,
        day_date=date(year, 1, 2),
        day_slug="2-de-enero",
        day_label_es="2 de enero",
        day_label_en="",
        title_es="Carnavalito",
        title_en="",
        source_url="https://carnavaldepasto.org/x/",
    )


def _report(
    count: int,
    *,
    posts_seen: int | None = None,
    field_hits: dict[str, int] | None = None,
    years: list[int] | None = None,
) -> TransformReport:
    years = years or [2020] * count
    candidates = [_candidate(i, year=years[i]) for i in range(count)]
    seen = count if posts_seen is None else posts_seen
    hits = field_hits or {field: seen for field in FIELDS}
    return TransformReport(
        candidates=candidates, posts_seen=seen, rejected=0, field_hits=hits
    )


def test_a_healthy_run_passes() -> None:
    result = sanity.check(_report(5), history=[])

    assert result.passed is True  # noqa: S101
    assert result.reasons == []  # noqa: S101


def test_zero_extraction_with_history_fails() -> None:
    result = sanity.check(_report(0, posts_seen=5), history=[5])

    assert result.passed is False  # noqa: S101
    assert any("zero extraction" in reason for reason in result.reasons)  # noqa: S101


def test_an_empty_payload_fails() -> None:
    result = sanity.check(_report(0, posts_seen=0), history=[])

    assert result.passed is False  # noqa: S101


def test_a_drop_ratio_fails() -> None:
    result = sanity.check(_report(2), history=[5])

    assert result.passed is False  # noqa: S101
    assert any("dropped" in reason for reason in result.reasons)  # noqa: S101


def test_a_spike_ratio_fails() -> None:
    result = sanity.check(_report(10), history=[2])

    assert result.passed is False  # noqa: S101
    assert any("spiked" in reason for reason in result.reasons)  # noqa: S101


def test_a_required_field_that_matches_nothing_fails() -> None:
    hits = {"id": 3, "date": 3, "title": 3, "link": 0}
    result = sanity.check(_report(3, field_hits=hits), history=[])

    assert result.passed is False  # noqa: S101
    assert any("'link'" in reason for reason in result.reasons)  # noqa: S101


def test_poor_field_completeness_fails() -> None:
    hits = {field: 3 for field in FIELDS}
    result = sanity.check(_report(3, posts_seen=10, field_hits=hits), history=[])

    assert result.passed is False  # noqa: S101
    assert any("present in only" in reason for reason in result.reasons)  # noqa: S101


def test_candidates_outside_the_target_edition_fail() -> None:
    result = sanity.check(_report(2, years=[2019, 2020]), history=[], target_year=2026)

    assert result.passed is False  # noqa: S101
    assert any("edition alignment" in reason for reason in result.reasons)  # noqa: S101
