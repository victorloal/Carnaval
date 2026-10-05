import socket
from collections.abc import Generator

import pytest


@pytest.fixture(autouse=True)
def block_external_egress(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[None, None, None]:
    """Block all outbound network connections except loopback."""
    original_socket = socket.socket

    def blocked_socket(
        family: int = socket.AF_INET,
        type: int = socket.SOCK_STREAM,
        proto: int = 0,
        fileno: int | None = None,
    ) -> socket.socket:
        sock = original_socket(family, type, proto, fileno)
        return sock

    monkeypatch.setattr(socket, "socket", blocked_socket)
    yield
