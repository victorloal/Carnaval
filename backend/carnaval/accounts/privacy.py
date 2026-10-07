"""Salted IP hashing. The raw address is never stored or logged (PRV-01)."""

from __future__ import annotations

import hashlib

from django.conf import settings


def hash_ip(ip: str | None) -> str:
    if not ip:
        return ""
    salt = settings.PRIVACY_IP_SALT
    return hashlib.sha256(f"{salt}:{ip}".encode()).hexdigest()
