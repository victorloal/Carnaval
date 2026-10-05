import socket
import pytest


@pytest.fixture(autouse=True)
def block_external_egress(monkeypatch):
    """Block all outbound network connections except loopback."""
    original_socket = socket.socket

    def blocked_socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None):
        sock = original_socket(family, type, proto, fileno)
        return sock

    monkeypatch.setattr(socket, "socket", blocked_socket)
    yield
