"""``manage.py ingest_source`` — fetch and store raw payloads (FR-B-17, FR-B-18).

It stops at RAW STORE: nothing is transformed, staged or published. It exits
non-zero when any source fails, so a scheduled job fails loudly.
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from carnaval.ingestion import pipeline
from carnaval.ingestion.models import (
    IngestionStatus,
    IngestionTrigger,
    ScrapeSource,
)


class Command(BaseCommand):
    help = (
        "Fetch configured sources and store their raw payloads. Never publishes "
        "anything (transform and staging are Sprint 04)."
    )

    def add_arguments(self, parser: Any) -> None:
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--all", action="store_true", help="Every source.")
        group.add_argument(
            "--due",
            action="store_true",
            help=(
                "Active sources. Per-source cron matching is deferred; the "
                "schedule is applied by the GitHub Actions cron (flujo-datos §11)."
            ),
        )
        group.add_argument("--source", help="One source, by name or UUID.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List what would run, calling nothing.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        sources = self._resolve(options)

        if options["dry_run"]:
            for source in sources:
                self.stdout.write(f"would run: {source.name}")
            return

        trigger = IngestionTrigger.CRON if options["due"] else IngestionTrigger.MANUAL
        failures = 0
        with pipeline.default_client() as client:
            for source in sources:
                run = pipeline.run_source(source, trigger=trigger, client=client)
                self.stdout.write(f"{source.name}: {run.status} {run.stats}")
                if run.status == IngestionStatus.FAILED:
                    failures += 1

        if failures:
            raise CommandError(f"{failures} source(s) failed")

    def _resolve(self, options: dict[str, Any]) -> list[ScrapeSource]:
        if options["source"]:
            source = self._one(options["source"])
            if source is None:
                raise CommandError(f"no source matches {options['source']!r}")
            return [source]

        queryset = ScrapeSource.objects.order_by("name")
        if options["due"]:
            queryset = queryset.filter(is_active=True)
        return list(queryset)

    @staticmethod
    def _one(identifier: str) -> ScrapeSource | None:
        by_name = ScrapeSource.objects.filter(name=identifier).first()
        if by_name is not None:
            return by_name
        try:
            return ScrapeSource.objects.filter(pk=identifier).first()
        except (ValidationError, ValueError):
            return None
