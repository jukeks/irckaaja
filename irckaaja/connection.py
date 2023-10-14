import socket
import ssl
from datetime import timedelta
from typing import List, Optional

from irckaaja.protocol import MessageParser, ParsedMessage


class IrcConnection:
    """
    IRC Connection
    """

    def __init__(
        self,
        hostname: str,
        port: int,
        use_tls: bool,
        cafile: Optional[str] = None,
        timeout: timedelta = timedelta(seconds=1),
        connect_timeout: timedelta = timedelta(seconds=10),
    ) -> None:
        self._hostname = hostname
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._use_tls = use_tls
        self._cafile = cafile
        self._buff = ""
        self._parser = MessageParser()
        self._encoding = "utf-8"
        self._timeout = timeout.total_seconds()
        self._connect_timeout = connect_timeout.total_seconds()

    def connect(self) -> None:
        self._socket = socket.create_connection(
            (self._hostname, self._port), self._connect_timeout
        )
        if self._use_tls:
            ssl_context = ssl.create_default_context(cafile=self._cafile)
            self._socket = ssl_context.wrap_socket(
                self._socket, server_hostname=self._hostname
            )
        self._socket.settimeout(self._timeout)

    def write(self, message: str) -> None:
        self._socket.sendall(bytearray(message, self._encoding))

    def read(self) -> List[ParsedMessage]:
        try:
            read = self._socket.recv(4096)
        except socket.timeout:
            return []

        if len(read) == 0:
            # socket.recv() returns empty buff for closed sockets
            raise EOFError()

        self._buff += read.decode(self._encoding)
        parsed_messages, self._buff = self._parser.parse_buffer(self._buff)
        return parsed_messages

    def close(self) -> None:
        self._socket.close()
