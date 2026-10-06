"""The demo seed that lets the MVP show published content without an admin."""

import pytest
from carnaval.programme.models import Day, Edition, Event, Venue
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

pytestmark = pytest.mark.django_db


def test_seed_demo_is_idempotent() -> None:
    """Running the seed twice leaves the same rows and no duplicates."""
    call_command("seed_demo", force=True)
    counts = (
        Edition.objects.count(),
        Day.objects.count(),
        Venue.objects.count(),
        Event.objects.count(),
    )

    call_command("seed_demo", force=True)

    assert counts == (  # noqa: S101
        Edition.objects.count(),
        Day.objects.count(),
        Venue.objects.count(),
        Event.objects.count(),
    )
    assert Day.objects.count() == 5  # noqa: S101
    assert Edition.objects.get(year=2026).is_published  # noqa: S101


def test_seed_demo_publishes_everything_it_creates() -> None:
    call_command("seed_demo", force=True)
    assert all(edition.is_published for edition in Edition.objects.all())  # noqa: S101
    assert all(day.is_published for day in Day.objects.all())  # noqa: S101
    assert all(event.is_published for event in Event.objects.all())  # noqa: S101


def test_seed_demo_refuses_when_debug_is_off() -> None:
    """Risk 4: the review bypass must not run unattended in production."""
    with override_settings(DEBUG=False):
        with pytest.raises(CommandError):
            call_command("seed_demo")
