"""The sanity gate: a markup change must become an alarm, not a quiet success.

The dangerous case is not an error. It is a 200 whose body the extractor can no
longer understand, where it confidently produces zero records and reports
success. This gate runs after validation and **before** anything is staged; a
failure disables nothing by itself but fails the run, which trips the breaker.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median

from carnaval.ingestion.transforms import TransformReport

MIN_COMPLETENESS = 0.8
DROP_RATIO = 0.5
SPIKE_RATIO = 3.0


@dataclass(frozen=True)
class SanityResult:
    passed: bool
    reasons: list[str]


def check(
    report: TransformReport,
    *,
    history: list[int],
    target_year: int | None = None,
) -> SanityResult:
    reasons: list[str] = []
    extracted = len(report.candidates)

    if report.posts_seen == 0:
        reasons.append("the payload contained no records")

    for field, hits in report.field_hits.items():
        if hits == 0:
            reasons.append(f"required field {field!r} matched nothing")
        elif report.posts_seen and hits < MIN_COMPLETENESS * report.posts_seen:
            reasons.append(
                f"required field {field!r} present in only {hits}/{report.posts_seen}"
            )

    if history:
        baseline = median(history)
        if extracted == 0 and baseline > 0:
            reasons.append(
                "zero extraction from a source that previously yielded records"
            )
        elif baseline > 0 and extracted > 0:
            if extracted < DROP_RATIO * baseline:
                reasons.append(
                    f"extraction dropped to {extracted} (baseline {baseline:g})"
                )
            elif extracted > SPIKE_RATIO * baseline:
                reasons.append(
                    f"extraction spiked to {extracted} (baseline {baseline:g})"
                )

    if target_year is not None:
        off = sorted({c.year for c in report.candidates if c.year != target_year})
        if off:
            reasons.append(
                f"edition alignment: candidates outside {target_year}: {off}"
            )

    return SanityResult(passed=not reasons, reasons=reasons)
