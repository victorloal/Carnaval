"""Typed accessors for `site_settings` (ADR 0013: no schema, Python accessors).

Secrets are refused at the model (`SiteSetting.clean`), and every change is
audited in the admin, so a value read here is either a configuration value or a
loud error.
"""

from __future__ import annotations

from typing import Any

from carnaval.editorial.models import SiteSetting


def get_setting(key: str, default: Any = None) -> Any:
    row = SiteSetting.objects.filter(key=key).first()
    return row.value if row is not None else default


def get_bool(key: str, default: bool = False) -> bool:
    value = get_setting(key, default)
    return bool(value)


def get_int(key: str, default: int = 0) -> int:
    value = get_setting(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
