"""factory_boy factories for the programme spine (plan-pruebas.md §5).

No raw model instantiation in tests: every model gets a factory.
"""

from datetime import date, timedelta

import factory
from carnaval.programme.models import Day, Edition, Venue


class EditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Edition

    year = factory.Sequence(lambda n: 2026 + n)
    slug = factory.Sequence(lambda n: f"edicion-{n}")
    title_es = factory.Sequence(lambda n: f"Edicion {n}")


class DayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Day

    edition = factory.SubFactory(EditionFactory)
    date = factory.Sequence(lambda n: date(2026, 1, 1) + timedelta(days=n))
    slug = factory.Sequence(lambda n: f"dia-{n}")
    label_es = factory.Sequence(lambda n: f"Dia {n}")


class VenueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Venue

    name_es = factory.Sequence(lambda n: f"Escenario {n}")
