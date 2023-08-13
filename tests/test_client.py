from socketserver import StreamRequestHandler, TCPServer
from threading import Thread

from irckaaja.client import IrcClient
from irckaaja.config import BotConfig, ServerConfig


class ReusableTCPServer(TCPServer):
    allow_reuse_address = True
    allow_reuse_port = True


def test_client() -> None:
    host, port = "localhost", 9999

    client = IrcClient(
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

    class MockIRCServerHandler(StreamRequestHandler):
        lines = []

        def handle(self) -> None:
            while True:
                line = self.rfile.readline().strip().decode()
                print(line)
                self.lines.append(line)

                if "JOIN " in line:

                    def shutdown() -> None:
                        client.kill()
                        self.server.shutdown()

                    Thread(target=shutdown).start()
                    return
                if "USER " in line:
                    self.wfile.write(
                        b":localhost 376 \r\n"
                    )  # respond with end of MOTD

    with ReusableTCPServer((host, port), MockIRCServerHandler, True) as server:
        client.connect()
        server.serve_forever()

    assert not client.alive
    msgs = MockIRCServerHandler.lines
    assert "NICK test" in msgs
    assert "USER testuser 0 * :tester" in msgs
    assert "PING localhost" in msgs
    assert "JOIN :#test" in msgs
