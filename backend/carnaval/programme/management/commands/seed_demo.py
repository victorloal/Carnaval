"""Seed a demonstrable programme for the MVP — development only.

The MVP ships no admin (publishing waits for v1), so nothing would otherwise
reach ``published`` for the public API to serve. This command is the deliberate
exception: it creates the canonical 2026 edition, its five day rows and a few
sample events **already published**, bypassing review.

Hard limits (see ``docs/sprints/sprint-02-plan.md``, Risk 4):

- It never creates a user.
- It is idempotent: running it twice leaves the same rows.
- It refuses to run with ``DEBUG`` off unless ``--force`` is passed.
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from carnaval.core.models import ModerationOrigin, ModerationStatus
from carnaval.programme.models import Day, Edition, Event, Venue

_CANONICAL_DAYS = [
    (date(2026, 1, 2), "carnavalito", "Carnavalito", "Carnavalito"),
    (
        date(2026, 1, 3),
        "colectivos-coreograficos",
        "Colectivos coreográficos",
        "Choreographic collectives",
    ),
    (
        date(2026, 1, 4),
        "desfile-familia-castaneda",
        "Desfile Familia Castañeda",
        "Familia Castañeda Parade",
    ),
    (date(2026, 1, 5), "dia-de-negros", "Día de Negros", "Day of Blacks"),
    (
        date(2026, 1, 6),
        "dia-de-blancos",
        "Día de Blancos / Gran Desfile",
        "Day of Whites / Grand Parade",
    ),
]

# (day slug, starts_at time, title_es, title_en, venue name or None)
_EVENTS = [
    (
        "carnavalito",
        time(14, 0),
        "Desfile del Carnavalito",
        "Carnavalito Parade",
        "Senda del Carnaval",
    ),
    (
        "colectivos-coreograficos",
        time(15, 0),
        "Muestra de colectivos",
        "Collectives showcase",
        "Plaza del Carnaval",
    ),
    (
        "desfile-familia-castaneda",
        time(14, 0),
        "Desfile Familia Castañeda",
        "Familia Castañeda Parade",
        "Senda del Carnaval",
    ),
    (
        "dia-de-negros",
        time(9, 0),
        "Descenso de la Familia Castañeda",
        "Familia Castañeda Descent",
        "Plaza del Carnaval",
    ),
    (
        "dia-de-negros",
        time(14, 0),
        "Gran Desfile Día de Negros",
        "Grand Parade of the Day of Blacks",
        "Senda del Carnaval",
    ),
    (
        "dia-de-blancos",
        time(14, 0),
        "Gran Desfile Día de Blancos",
        "Grand Parade of the Day of Whites",
        "Senda del Carnaval",
    ),
]

_OFFICIAL_SOURCE = "https://www.carnavaldepasto.org/"


class Command(BaseCommand):
    help = "Create a demo edition, days, venues and events (development only)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--force",
            action="store_true",
            help="Run even with DEBUG off (CI, throwaway environments).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                "seed_demo is for development only: it publishes content without "
                "review. Pass --force to override (DEBUG is off)."
            )

        self.stdout.write(
            self.style.WARNING(
                "seed_demo publishes demo content, bypassing review. Demo only."
            )
        )

        edition, _ = Edition.objects.update_or_create(
            year=2026,
            defaults={
                "slug_es": "carnaval-2026",
                "title_es": "Carnaval de Negros y Blancos 2026",
                "title_en": "Carnival of Blacks and Whites 2026",
                "starts_on": date(2026, 1, 2),
                "ends_on": date(2026, 1, 6),
                "summary_es": "Programa de ejemplo para desarrollo.",
                "summary_en": "Sample programme for development.",
                "status": ModerationStatus.PUBLISHED,
                "origin": ModerationOrigin.MANUAL,
            },
        )

        venues: dict[str, Venue] = {}
        for name_es, name_en in [
            ("Senda del Carnaval", "Carnival Route"),
            ("Plaza del Carnaval", "Carnival Square"),
        ]:
            venue, _ = Venue.objects.update_or_create(
                name_es=name_es,
                defaults={
                    "name_en": name_en,
                    "city": "Pasto",
                    "status": ModerationStatus.PUBLISHED,
                    "origin": ModerationOrigin.MANUAL,
                },
            )
            venues[name_es] = venue

        days: dict[str, Day] = {}
        for day_date, slug, label_es, label_en in _CANONICAL_DAYS:
            day, _ = Day.objects.update_or_create(
                edition=edition,
                slug_es=slug,
                defaults={
                    "date": day_date,
                    "label_es": label_es,
                    "label_en": label_en,
                    "status": ModerationStatus.PUBLISHED,
                    "origin": ModerationOrigin.MANUAL,
                },
            )
            days[slug] = day

        for sort_order, (day_slug, start, title_es, title_en, venue_name) in enumerate(
            _EVENTS
        ):
            starts_at = timezone.make_aware(
                datetime.combine(days[day_slug].date, start)
            )
            Event.objects.update_or_create(
                day=days[day_slug],
                title_es=title_es,
                defaults={
                    "title_en": title_en,
                    "starts_at": starts_at,
                    "venue": venues.get(venue_name) if venue_name else None,
                    "sort_order": sort_order,
                    "source_url": _OFFICIAL_SOURCE,
                    "status": ModerationStatus.PUBLISHED,
                    "origin": ModerationOrigin.MANUAL,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded edition {edition.year}: "
                f"{len(days)} days, {len(venues)} venues, {len(_EVENTS)} events."
            )
        )
