"""Staging: validated candidates become `pending` rows. Nothing becomes public.

Two rules make this safe:

- Editions and days are created with ``get_or_create`` and are never modified: an
  edition that already exists (a published one, say) is left untouched.
- An event is only written when it is a new row, or an existing ``pending`` row
  the pipeline itself created (``origin = scraped``). A ``published``, ``rejected``
  or human-authored row is left alone, so a failed or repeated run can never
  change or degrade public content. Proposing a change to a published row is
  ``flujo-datos.md`` §5.1 and waits for its own ADR.
"""

from __future__ import annotations

from carnaval.core.models import ModerationOrigin, ModerationStatus
from carnaval.ingestion.models import IngestionRun
from carnaval.ingestion.transforms import EventCandidate, TransformReport
from carnaval.programme.models import Day, Edition, Event


def stage(run: IngestionRun, report: TransformReport) -> dict[str, object]:
    inserted = 0
    updated = 0
    skipped = 0

    for candidate in report.candidates:
        edition, _ = Edition.objects.get_or_create(
            year=candidate.year,
            defaults={
                "slug_es": f"carnaval-{candidate.year}",
                "title_es": f"Carnaval {candidate.year}",
                "status": ModerationStatus.PENDING,
                "origin": ModerationOrigin.SCRAPED,
                "ingestion_run": run,
            },
        )
        day, _ = Day.objects.get_or_create(
            edition=edition,
            slug_es=candidate.day_slug,
            defaults={
                "date": candidate.day_date,
                "label_es": candidate.day_label_es,
                "label_en": candidate.day_label_en,
                "status": ModerationStatus.PENDING,
                "origin": ModerationOrigin.SCRAPED,
                "ingestion_run": run,
            },
        )
        outcome = _upsert_event(day, candidate, run)
        if outcome == "inserted":
            inserted += 1
        elif outcome == "updated":
            updated += 1
        else:
            skipped += 1

    return {
        "extracted": len(report.candidates),
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "rejected": report.rejected,
    }


def _upsert_event(day: Day, candidate: EventCandidate, run: IngestionRun) -> str:
    existing = Event.objects.filter(
        day=day, source_record_key=candidate.source_record_key
    ).first()
    if existing is None:
        Event.objects.create(
            day=day,
            source_record_key=candidate.source_record_key,
            title_es=candidate.title_es,
            title_en=candidate.title_en,
            description_es=candidate.description_es,
            description_en=candidate.description_en,
            starts_at=candidate.starts_at,
            ends_at=candidate.ends_at,
            source_url=candidate.source_url,
            status=ModerationStatus.PENDING,
            origin=ModerationOrigin.SCRAPED,
            ingestion_run=run,
        )
        return "inserted"

    if existing.status == ModerationStatus.PUBLISHED and (
        existing.origin == ModerationOrigin.SCRAPED
    ):
        # §5.1: propose the change, never write the published row.
        proposed = {
            field: value
            for field, value in _candidate_fields(candidate).items()
            if getattr(existing, field) != value
        }
        if proposed:
            existing.staged_changes = {**proposed, "ingestion_run": str(run.pk)}
            existing.save(update_fields=["staged_changes"])
        return "skipped"

    if (
        existing.status != ModerationStatus.PENDING
        or existing.origin != ModerationOrigin.SCRAPED
    ):
        # A human or community decision stands. The pipeline does not touch it.
        return "skipped"

    for field, value in _candidate_fields(candidate).items():
        setattr(existing, field, value)
    existing.ingestion_run = run
    existing.save()
    return "updated"


def _candidate_fields(candidate: EventCandidate) -> dict[str, object]:
    return {
        "title_es": candidate.title_es,
        "title_en": candidate.title_en,
        "description_es": candidate.description_es,
        "description_en": candidate.description_en,
        "starts_at": candidate.starts_at,
        "ends_at": candidate.ends_at,
        "source_url": candidate.source_url,
    }
