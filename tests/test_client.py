from socketserver import StreamRequestHandler, TCPServer
from threading import Thread
from typing import Any

from irckaaja.client import IrcClient
from irckaaja.config import BotConfig, ServerConfig


class ReusableSingleRequestTCPServer(TCPServer):
    allow_reuse_address = True
    allow_reuse_port = True

    def shutdown_request(self, request: Any) -> None:
        Thread(target=self.shutdown).start()  # stop server after first request
        return super().shutdown_request(request)


def get_test_client(host: str, port: int) -> IrcClient:
    return IrcClient(
        server_config=ServerConfig(
            name="test",
            hostname=host,
            port=port,
            channels=["#test"],
        ),
        bot_config=BotConfig(
            nick="test",
            altnick="test_",
            realname="tester",
            username="testuser",
            owner="owner",
        ),
        modules_config={},
    )


def test_client() -> None:
    host, port = "localhost", 9999
    client = get_test_client(host, port)

    class MockIRCServerHandler(StreamRequestHandler):
        lines = []

        def handle(self) -> None:
            while True:
                line = self.rfile.readline().strip().decode()
                print(line)
                self.lines.append(line)

                if "USER " in line:
                    self.wfile.write(
                        b":localhost 376 \r\n"
                    )  # respond with end of MOTD

                if "JOIN " in line:
                    self.wfile.write(
                        b":localhost 353 test @ #test :test juke\r\n"
                        b":localhost 366 test @ #test : \r\n"
                        b"PING :test1 \r\n"
                    )

                if "PING " in line:
                    self.wfile.write(b"PONG :localhost\r\n")

                if "PONG " in line:
                    return

    with ReusableSingleRequestTCPServer(
        (host, port), MockIRCServerHandler, True
    ) as server:
        client.connect()
        server.serve_forever()
        client.kill()

    assert not client.alive
    assert client._channel_list[0].userlist == ["test", "juke"]
    msgs = MockIRCServerHandler.lines
    assert "NICK test" in msgs
    assert "USER testuser 0 * :tester" in msgs
    assert "PING localhost" in msgs
    assert "JOIN :#test" in msgs
    assert "PONG :test1" in msgs
