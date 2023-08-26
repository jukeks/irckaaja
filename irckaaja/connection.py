import socket
from typing import List

from irckaaja.protocol import MessageParser, ParsedMessage


class IrcConnection:
    """
    IRC Connection
    """

    def __init__(self, hostname: str, port: int) -> None:
        self._hostname = hostname
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._buff = ""
        self._parser = MessageParser()
        self._encoding = "utf-8"

    def connect(self) -> None:
        self._socket.connect((self._hostname, self._port))
        self._socket.settimeout(1.0)

    def write(self, message: str) -> None:
        self._socket.sendall(bytearray(message, self._encoding))

    def read(self) -> List[ParsedMessage]:
        try:
            read = self._socket.recv(4096)
        except socket.timeout:
            return []

        if read == "":
            # socket.recv() returns empty string for closed sockets
            raise EOFError()

        self._buff += read.decode(self._encoding)
        parsed_messages, self._buff = self._parser.parse_buffer(self._buff)
        return parsed_messages

    def close(self) -> None:
        self._socket.close()
