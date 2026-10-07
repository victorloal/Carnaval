"""The generated schema covers the whole public catalogue (NFR-12, ADR 0011)."""

from __future__ import annotations

from drf_spectacular.generators import SchemaGenerator


def test_the_schema_covers_the_public_catalogue() -> None:
    schema = SchemaGenerator().get_schema(request=None, public=True)

    for path in (
        "/api/editions/",
        "/api/days/",
        "/api/events/",
        "/api/venues/",
    ):
        assert path in schema["paths"]  # noqa: S101
