import socket
from datetime import timedelta

import pytest

from irckaaja.connection import IrcConnection
from irckaaja.protocol import MessageType


def test_connection() -> None:
    ld = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ld.bind(("", 0))
    hostname, port = ld.getsockname()
    ld.listen()

    client = IrcConnection(hostname, port, timeout=timedelta(milliseconds=1))
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
