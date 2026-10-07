"""Purge personal data once its retention period expires (PRV-03, ADR 0018).

Every period is an operational default set by the maintainer (ADR 0018), not
legal advice. The command clears or deletes:

- a submission's contact email, 12 months after the submission was decided;
- `consent_records`, 24 months after acceptance;
- a takedown request's requester email, 24 months after `responded_at`;
- `ingestion_runs`, after 12 months.

`audit_logs` is deliberately **not touched**: it is append-only (FR-D-09) and
holds only salted hashes, so the evidence value outweighs the period. That
exception is stated in the privacy policy rather than silently applied.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

CONTACT_EMAIL_DAYS = 365
CONSENT_DAYS = 730
TAKEDOWN_EMAIL_DAYS = 730
INGESTION_RUN_DAYS = 365


class Command(BaseCommand):
    help = "Delete or clear personal data past the ADR 0018 retention periods."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="count what would be purged without changing anything",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        from carnaval.ingestion.models import IngestionRun
        from carnaval.legal.models import TakedownRequest
        from carnaval.submissions.models import ConsentRecord, Submission

        dry_run: bool = options["dry_run"]
        now = timezone.now()

        submissions = Submission.objects.filter(
            reviewed_at__lt=now - timedelta(days=CONTACT_EMAIL_DAYS)
        ).exclude(contact_email="")
        consents = ConsentRecord.objects.filter(
            accepted_at__lt=now - timedelta(days=CONSENT_DAYS)
        )
        takedowns = TakedownRequest.objects.filter(
            responded_at__lt=now - timedelta(days=TAKEDOWN_EMAIL_DAYS)
        ).exclude(requester_email="")
        runs = IngestionRun.objects.filter(
            started_at__lt=now - timedelta(days=INGESTION_RUN_DAYS)
        )

        summary = {
            "submissions.contact_email": submissions.count(),
            "consent_records": consents.count(),
            "takedown_requests.requester_email": takedowns.count(),
            "ingestion_runs": runs.count(),
        }

        if not dry_run:
            with transaction.atomic():
                submissions.update(contact_email="")
                consents.delete()
                takedowns.update(requester_email="")
                runs.delete()

        prefix = "would purge" if dry_run else "purged"
        for label, count in summary.items():
            self.stdout.write(f"{prefix} {label}: {count}")
