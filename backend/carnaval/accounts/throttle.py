"""Login throttling with exponential backoff (SEC-06).

State lives in the cache, keyed by the username and the **salted IP hash** —
never the raw address. After `LOGIN_THROTTLE_THRESHOLD` failures the delay grows
as `base * 2^(n - threshold)`, capped, so a slow attacker is slowed and a
mistyping human is not locked out for long.
"""

from __future__ import annotations

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


def _key(kind: str, value: str) -> str:
    return f"login-throttle:{kind}:{value}"


def _delay(failures: int) -> float:
    if failures < settings.LOGIN_THROTTLE_THRESHOLD:
        return 0.0
    exponent = failures - settings.LOGIN_THROTTLE_THRESHOLD
    return float(
        min(
            settings.LOGIN_THROTTLE_BASE_SECONDS * (2**exponent),
            settings.LOGIN_THROTTLE_MAX_SECONDS,
        )
    )


def _state(kind: str, value: str) -> dict[str, float]:
    state = cache.get(_key(kind, value))
    if not isinstance(state, dict):
        return {"count": 0.0, "last": 0.0}
    return state


def retry_after(username: str, ip_hash: str) -> float:
    worst = 0.0
    now = timezone.now().timestamp()
    for kind, value in (("user", username), ("ip", ip_hash)):
        if not value:
            continue
        state = _state(kind, value)
        remaining = _delay(int(state["count"])) - (now - state["last"])
        worst = max(worst, remaining)
    return max(0.0, worst)


def is_locked(username: str, ip_hash: str) -> bool:
    return retry_after(username, ip_hash) > 0


def record_failure(username: str, ip_hash: str) -> None:
    now = timezone.now().timestamp()
    timeout = max(settings.LOGIN_THROTTLE_MAX_SECONDS * 2, 60)
    for kind, value in (("user", username), ("ip", ip_hash)):
        if not value:
            continue
        state = _state(kind, value)
        state = {"count": state["count"] + 1, "last": now}
        cache.set(_key(kind, value), state, timeout=timeout)


def reset(username: str, ip_hash: str) -> None:
    for kind, value in (("user", username), ("ip", ip_hash)):
        if value:
            cache.delete(_key(kind, value))
