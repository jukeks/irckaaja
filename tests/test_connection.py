import socket
import ssl
import threading
from datetime import timedelta

import pytest

from irckaaja.connection import IrcConnection
from irckaaja.protocol import MessageType


def test_connection() -> None:
    ld = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ld.bind(("", 0))
    hostname, port = ld.getsockname()
    ld.listen()

    client = IrcConnection(
        hostname, port, use_tls=False, timeout=timedelta(milliseconds=1)
    )
    client.connect()
    server, _ = ld.accept()

    server.sendall(bytearray("PING :test\r\n", "utf-8"))
    messages = client.read()
    assert messages[0].type == MessageType.PING

    client.write("PONG :test\r\n")
    buff = server.recv(4096)
    assert buff == b"PONG :test\r\n"

    assert client.read() == []

    server.close()
    with pytest.raises(EOFError):
        client.read()

    client.close()


def test_tls_connection() -> None:
    ld = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ld.bind(("localhost", 0))
    hostname, port = ld.getsockname()
    ld.listen()

    context = ssl.create_default_context(
        purpose=ssl.Purpose.CLIENT_AUTH,
        cafile="tests/fixtures/localhost.ca.pem",
    )
    context.load_cert_chain(
        certfile="tests/fixtures/localhost.crt",
        keyfile="tests/fixtures/localhost.key",
    )

    client = IrcConnection(
        hostname,
        port,
        use_tls=True,
        cafile="tests/fixtures/localhost.ca.pem",
        timeout=timedelta(milliseconds=1),
    )

    def server_do() -> None:
        tls_ld = context.wrap_socket(ld, server_side=True)
        server, _ = tls_ld.accept()
        server.sendall(bytearray("PING :test\r\n", "utf-8"))
        buff = server.recv(4096)
        assert buff == b"PONG :test\r\n"
        server.close()

    t = threading.Thread(target=server_do)
    t.start()

    client.connect()

    client.write("PONG :test\r\n")
    messages = client.read()
    assert messages[0].type == MessageType.PING
    client.close()

    t.join()
