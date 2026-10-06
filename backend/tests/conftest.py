"""Session-wide egress guard: no test may reach a live source (NFR-16).

Permits loopback only (``localhost``, ``127.0.0.1``, ``::1``, and AF_UNIX,
which is local IPC and cannot leave the machine) so local services such as
PostgreSQL still connect; refuses every other destination at ``connect``,
``sendto`` and at name resolution. See ``docs/sprints/sprint-01-plan.md``
item 7: a guard, not a convention — a test that reaches for the network fails
for an infrastructure reason.
"""

import socket
from collections.abc import Generator
from typing import Any

import pytest

_LOOPBACK_HOSTS = frozenset({"", "127.0.0.1", "localhost", "::1"})

_EGRESS_BLOCKED = "egress blocked in tests (NFR-16)"

_ORIGINAL_GETADDRINFO = socket.getaddrinfo
_ORIGINAL_GETHOSTBYNAME = socket.gethostbyname
_ORIGINAL_GETHOSTBYNAME_EX = socket.gethostbyname_ex


def _ensure_outbound_allowed(address: Any) -> None:
    """Refuse any destination that is not loopback.

    A non-tuple address is an AF_UNIX path: local IPC, allowed because it
    cannot leave the machine.
    """
    if not isinstance(address, tuple):
        return
    host = address[0] if address else None
    if host in _LOOPBACK_HOSTS:
        return
    raise OSError(_EGRESS_BLOCKED)


class GuardedSocket(socket.socket):
    """A socket that refuses to reach anything but loopback."""

    def connect(self, address: Any) -> None:
        _ensure_outbound_allowed(address)
        super().connect(address)

    def connect_ex(self, address: Any) -> int:
        # Raises instead of returning an errno: a blocked egress must fail
        # loudly, not look like a politely refused connection.
        _ensure_outbound_allowed(address)
        return super().connect_ex(address)

    def sendto(self, *args: Any, **kwargs: Any) -> int:
        address = args[-1] if args else kwargs.get("address")
        _ensure_outbound_allowed(address)
        return super().sendto(*args, **kwargs)


def _guarded_getaddrinfo(host: Any, *args: Any, **kwargs: Any) -> Any:
    if host is None or host in _LOOPBACK_HOSTS:
        return _ORIGINAL_GETADDRINFO(host, *args, **kwargs)
    raise socket.gaierror(socket.EAI_NONAME, _EGRESS_BLOCKED)


def _guarded_gethostbyname(host: str) -> str:
    if host in _LOOPBACK_HOSTS:
        return _ORIGINAL_GETHOSTBYNAME(host)
    raise socket.gaierror(socket.EAI_NONAME, _EGRESS_BLOCKED)


def _guarded_gethostbyname_ex(host: str) -> tuple[str, list[str], list[str]]:
    if host in _LOOPBACK_HOSTS:
        return _ORIGINAL_GETHOSTBYNAME_EX(host)
    raise socket.gaierror(socket.EAI_NONAME, _EGRESS_BLOCKED)


@pytest.fixture(scope="session", autouse=True)
def block_external_egress() -> Generator[None, None, None]:
    """Route every outbound path in the ``socket`` module through the guard."""
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(socket, "socket", GuardedSocket)
    monkeypatch.setattr(socket, "getaddrinfo", _guarded_getaddrinfo)
    monkeypatch.setattr(socket, "gethostbyname", _guarded_gethostbyname)
    monkeypatch.setattr(socket, "gethostbyname_ex", _guarded_gethostbyname_ex)
    yield
    monkeypatch.undo()


@pytest.fixture(autouse=True)
def _no_https_redirect(settings: Any) -> None:
    """Production sets SECURE_SSL_REDIRECT; the test client speaks plain HTTP."""
    settings.SECURE_SSL_REDIRECT = False
