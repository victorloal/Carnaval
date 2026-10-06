"""Unit tests for the programme spine — FR-A-01 and FR-A-02.

FR-A-01: editions are identified by year, with a slug and a publication flag.
FR-A-02: days are rows, not a fixed enum — names vary by year.
"""

import pytest
from django.db import IntegrityError, transaction

from tests.factories import DayFactory, EditionFactory

pytestmark = pytest.mark.django_db


def test_edition_starts_unpublished() -> None:
    """FR-A-01: an edition carries a publication flag, off until published."""
    edition = EditionFactory()
    assert edition.is_published is False  # noqa: S101
    assert edition.pk is not None  # noqa: S101


def test_edition_year_is_unique() -> None:
    """FR-A-01: an edition is identified by its year."""
    EditionFactory(year=2999)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            EditionFactory(year=2999)


def test_day_labels_are_rows_not_an_enum() -> None:
    """FR-A-02: any day label can be stored, without a migration."""
    negro = DayFactory(label_es="Dia de Negros", slug="dia-negros")
    carnavalito = DayFactory(label_es="Carnavalito", slug="carnavalito")
    assert negro.pk != carnavalito.pk  # noqa: S101
    assert negro.label_es != carnavalito.label_es  # noqa: S101


def test_day_slug_is_unique_within_an_edition_only() -> None:
    """FR-A-02: the slug constraint binds per edition, not globally."""
    edition = EditionFactory()
    DayFactory(edition=edition, slug="viernes")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            DayFactory(edition=edition, slug="viernes")

    # The same slug in a different edition is allowed.
    other = DayFactory(edition=EditionFactory(), slug="viernes")
    assert other.pk is not None  # noqa: S101
