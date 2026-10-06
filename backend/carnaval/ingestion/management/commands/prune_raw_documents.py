"""``manage.py prune_raw_documents`` — enforce the raw retention window.

ADR 0013: keep payloads for 30 days **and** within a per-source byte cap.
The exemption for payloads referenced by a live record cannot be implemented
yet — that link (a content row to its raw payload) lands with staging — so this
command deletes strictly by age and size until then.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from carnaval.ingestion import storage
from carnaval.ingestion.models import RawDocument, ScrapeSource


class Command(BaseCommand):
    help = "Delete raw payloads beyond the retention window (FR-B-16, ADR 0013)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--days",
            type=int,
            default=settings.INGESTION_RAW_RETENTION_DAYS,
        )
        parser.add_argument(
            "--bytes",
            type=int,
            default=settings.INGESTION_RAW_RETENTION_BYTES,
        )

    def handle(self, *args: Any, **options: Any) -> None:
        removed = self._prune_by_age(options["days"])
        removed += self._prune_by_size(options["bytes"])
        self.stdout.write(self.style.SUCCESS(f"pruned {removed} raw payload(s)"))

    def _delete(self, document: RawDocument) -> None:
        storage.delete_payload(document.storage_key)
        document.delete()

    def _prune_by_age(self, days: int) -> int:
        cutoff = timezone.now() - timedelta(days=days)
        removed = 0
        for document in RawDocument.objects.filter(fetched_at__lt=cutoff):
            self._delete(document)
            removed += 1
        return removed

    def _prune_by_size(self, cap: int) -> int:
        removed = 0
        for source in ScrapeSource.objects.all():
            documents = list(
                RawDocument.objects.filter(scrape_source=source).order_by("fetched_at")
            )
            total = sum(document.byte_size for document in documents)
            for document in documents:
                if total <= cap:
                    break
                self._delete(document)
                total -= document.byte_size
                removed += 1
        return removed
