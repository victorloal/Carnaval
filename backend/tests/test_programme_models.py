"""Unit tests for the programme spine — FR-A-01 and FR-A-02.

FR-A-01: editions are identified by year, with a slug and a publication flag.
FR-A-02: days are rows, not a fixed enum — names vary by year.
Also covers the shared moderation mixin (modelo-datos.md §2).
"""

import pytest
from carnaval.core.models import ModerationOrigin, ModerationStatus
from django.db import IntegrityError, transaction

from tests.factories import DayFactory, EditionFactory, EventFactory, VenueFactory

pytestmark = pytest.mark.django_db


def test_edition_starts_pending_and_manual() -> None:
    """FR-A-01 / modelo-datos §2: content is born pending, with an origin."""
    edition = EditionFactory()
    assert edition.status == ModerationStatus.PENDING  # noqa: S101
    assert edition.origin == ModerationOrigin.MANUAL  # noqa: S101
    assert edition.is_published is False  # noqa: S101
    assert edition.pk is not None  # noqa: S101


def test_is_published_is_derived_from_status() -> None:
    """There is no independent publication flag to flip by accident."""
    edition = EditionFactory()
    edition.status = ModerationStatus.PUBLISHED
    edition.save()
    assert edition.is_published is True  # noqa: S101


def test_a_rejection_requires_a_reason() -> None:
    """modelo-datos §9: `status = rejected` demands a non-empty reason."""
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            EditionFactory(status=ModerationStatus.REJECTED, rejection_reason="")


def test_a_rejection_with_a_reason_is_accepted() -> None:
    edition = EditionFactory(
        status=ModerationStatus.REJECTED, rejection_reason="Duplicate of 2026"
    )
    assert edition.pk is not None  # noqa: S101


def test_every_spine_model_carries_the_mixin() -> None:
    """The mixin is on editions, days and venues, not just editions."""
    for record in (DayFactory(), VenueFactory()):
        assert record.status == ModerationStatus.PENDING  # noqa: S101
        assert record.origin == ModerationOrigin.MANUAL  # noqa: S101
        assert record.is_published is False  # noqa: S101


def test_event_is_a_moderated_row_inside_a_day() -> None:
    """FR-A-03: an event hangs off a day, is pending and has a sort order."""
    event = EventFactory()
    assert event.day_id is not None  # noqa: S101
    assert event.status == ModerationStatus.PENDING  # noqa: S101
    assert event.is_published is False  # noqa: S101
    assert event.sort_order >= 0  # noqa: S101


def test_edition_year_is_unique() -> None:
    """FR-A-01: an edition is identified by its year."""
    EditionFactory(year=2999)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            EditionFactory(year=2999)


def test_day_labels_are_rows_not_an_enum() -> None:
    """FR-A-02: any day label can be stored, without a migration."""
    negro = DayFactory(label_es="Dia de Negros", slug_es="dia-negros")
    carnavalito = DayFactory(label_es="Carnavalito", slug_es="carnavalito")
    assert negro.pk != carnavalito.pk  # noqa: S101
    assert negro.label_es != carnavalito.label_es  # noqa: S101


def test_day_slug_is_unique_within_an_edition_only() -> None:
    """FR-A-02: the slug constraint binds per edition, not globally."""
    edition = EditionFactory()
    DayFactory(edition=edition, slug_es="viernes")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            DayFactory(edition=edition, slug_es="viernes")

    # The same slug in a different edition is allowed.
    other = DayFactory(edition=EditionFactory(), slug_es="viernes")
    assert other.pk is not None  # noqa: S101


def test_a_slug_is_resolved_per_locale_with_fallback() -> None:
    """FR-H-07: the English URL is used when it exists, else the source one."""
    edition = EditionFactory(slug_es="edicion-2026", slug_en="edition-2026")
    fallback = EditionFactory(slug_es="solo-es")

    assert edition.slug_for("es") == "edicion-2026"  # noqa: S101
    assert edition.slug_for("en") == "edition-2026"  # noqa: S101
    assert fallback.slug_for("en") == "solo-es"  # noqa: S101


def test_an_english_slug_cannot_collide() -> None:
    """FR-H-07: two rows cannot share a translated URL."""
    EditionFactory(slug_en="edition-2026")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            EditionFactory(slug_en="edition-2026")
