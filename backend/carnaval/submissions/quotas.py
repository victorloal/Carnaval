"""Anti-abuse quotas (FR-F-16, SEC-14).

Counted on the **salted IP hash**, never the raw address, and bounded globally so
the pending queue cannot grow without limit.
"""

from __future__ import annotations

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


def _key(kind: str, value: str) -> str:
    return f"submission-quota:{kind}:{value}"


def over_ip_quota(ip_hash: str) -> bool:
    if not ip_hash:
        return False
    bucket = timezone.now().strftime("%Y%m%d%H")
    key = _key("ip", f"{ip_hash}:{bucket}")
    count = int(cache.get(key, 0)) + 1
    cache.set(key, count, timeout=3600)
    return count > int(settings.SUBMISSION_IP_QUOTA_PER_HOUR)


def over_daily_quota() -> bool:
    bucket = timezone.now().strftime("%Y%m%d")
    key = _key("global", bucket)
    count = int(cache.get(key, 0)) + 1
    cache.set(key, count, timeout=86400)
    return count > int(settings.SUBMISSION_DAILY_PENDING_QUOTA)
