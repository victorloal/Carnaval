"""NFR-16: prove that egress is blocked and loopback still works.

Verification for NFR-16 (``CI: no egress``): a test that attempts an outbound
connection must fail the run. The external targets are RFC 5737 / RFC 2606
reserved (TEST-NET-1, ``.invalid``) so that even a broken guard can never
reach a live source.
"""

import socket

import pytest

TEST_NET_1 = "192.0.2.1"  # RFC 5737 — not routable on the public internet
NONEXISTENT_HOST = "carnaval-test.invalid"  # RFC 2606 — can never resolve


def test_outbound_tcp_connect_is_blocked() -> None:
    with socket.socket() as sock:
        sock.settimeout(2)
        with pytest.raises(OSError, match="egress blocked"):
            sock.connect((TEST_NET_1, 80))


def test_dns_resolution_of_external_host_is_blocked() -> None:
    with pytest.raises(socket.gaierror, match="egress blocked"):
        socket.getaddrinfo(NONEXISTENT_HOST, 80)


def test_gethostbyname_of_external_host_is_blocked() -> None:
    with pytest.raises(socket.gaierror, match="egress blocked"):
        socket.gethostbyname(NONEXISTENT_HOST)


def test_loopback_connect_is_allowed() -> None:
    # The kernel completes the handshake from the listen backlog, so no
    # accept() thread is needed for connect() to succeed on loopback.
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]
        with socket.socket() as client:
            client.settimeout(2)
            client.connect(("127.0.0.1", port))


def test_loopback_name_resolution_is_allowed() -> None:
    answers = socket.getaddrinfo("localhost", 0, type=socket.SOCK_STREAM)
    assert answers  # noqa: S101
