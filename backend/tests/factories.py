"""factory_boy factories for the programme spine and the ingestion tables.

No raw model instantiation in tests: every model gets a factory
(plan-pruebas.md §5).
"""

from datetime import date, timedelta

import factory
from carnaval.editorial.models import (
    MediaAsset,
    NewsItem,
    SiteSetting,
    Source,
    SourceKind,
)
from carnaval.ingestion.models import (
    IngestionRun,
    IngestionStatus,
    IngestionTrigger,
    RawDocument,
    ScrapeSource,
    SourceType,
)
from carnaval.legal.models import ClaimType, TakedownRequest
from carnaval.programme.models import Day, Edition, Event, Venue
from carnaval.submissions.models import ConsentRecord, Submission
from django.utils import timezone


class EditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Edition

    year = factory.Sequence(lambda n: 2026 + n)
    slug_es = factory.Sequence(lambda n: f"edicion-{n}")
    title_es = factory.Sequence(lambda n: f"Edicion {n}")


class DayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Day

    edition = factory.SubFactory(EditionFactory)
    date = factory.Sequence(lambda n: date(2026, 1, 1) + timedelta(days=n))
    slug_es = factory.Sequence(lambda n: f"dia-{n}")
    label_es = factory.Sequence(lambda n: f"Dia {n}")


class VenueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Venue

    name_es = factory.Sequence(lambda n: f"Escenario {n}")


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    day = factory.SubFactory(DayFactory)
    title_es = factory.Sequence(lambda n: f"Evento {n}")
    sort_order = factory.Sequence(lambda n: n)


class ScrapeSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScrapeSource

    name = factory.Sequence(lambda n: f"fuente-{n}")
    url = factory.Sequence(lambda n: f"https://example.org/feed/{n}")
    source_type = SourceType.WP_API
    user_agent = "CarnavalPastoSync/1.0 (test)"


class RawDocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RawDocument

    scrape_source = factory.SubFactory(ScrapeSourceFactory)
    url = factory.Sequence(lambda n: f"https://example.org/post/{n}")
    http_status = 200
    content_type = "application/json"
    content_hash = factory.Sequence(lambda n: f"{n:064x}")
    byte_size = 1024
    storage_key = factory.Sequence(lambda n: f"raw/{n}.json")
    fetched_at = factory.LazyFunction(timezone.now)


class IngestionRunFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IngestionRun

    scrape_source = factory.SubFactory(ScrapeSourceFactory)
    trigger = IngestionTrigger.MANUAL
    status = IngestionStatus.RUNNING
    started_at = factory.LazyFunction(timezone.now)


class SourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Source

    name = factory.Sequence(lambda n: f"source-{n}")
    kind = SourceKind.NEWS_OUTLET


class NewsItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsItem

    headline = factory.Sequence(lambda n: f"News {n}")
    url = factory.Sequence(lambda n: f"https://example.org/news/{n}")
    outlet = "Example"


class MediaAssetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MediaAsset

    title_es = factory.Sequence(lambda n: f"Foto {n}")


class SiteSettingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SiteSetting

    key = factory.Sequence(lambda n: f"setting.{n}")
    value = "value"


class SubmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Submission

    kind = "image"
    contact_email = factory.Sequence(lambda n: f"person{n}@example.org")


class ConsentRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ConsentRecord

    submission = factory.SubFactory(SubmissionFactory)


class TakedownRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TakedownRequest

    requester_email = factory.Sequence(lambda n: f"claimant{n}@example.org")
    claim_type = ClaimType.COPYRIGHT
