"""Typed failures for the ingestion pipeline.

The distinction matters: a transient failure is retried, a permanent one is
not, and a robots refusal disables the source instead of being worked around.
"""

from __future__ import annotations


class IngestionError(Exception):
    """Base class for every ingestion failure."""


class FetchError(IngestionError):
    """A fetch did not produce a usable payload."""


class TransientFetchError(FetchError):
    """Retryable: 5xx, timeout, connection/DNS/TLS error, or a 429."""


class PermanentFetchError(FetchError):
    """Not retried: 4xx other than 429. Retrying a 404 wastes requests."""


class RobotsDisallowed(FetchError):
    """robots.txt forbids the target; the source is disabled and flagged."""


class TransformError(IngestionError):
    """The payload could not be turned into records (malformed, wrong shape)."""


class SanityError(IngestionError):
    """The sanity gate refused the run: something looks like a markup change."""
