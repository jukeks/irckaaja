import re
import time
from typing import TYPE_CHECKING, Any, Dict, List

from irckaaja.protocol import User

if TYPE_CHECKING:
    from irckaaja.client import IrcClient


class BotScript:
    """
    Abstract script class. Should be inherited by script classes.
    See HelloWorld in scripts.helloworld.py for example.
    """

    def __init__(self, client: "IrcClient", config: Dict[str, Any]) -> None:
        self.client = client
        self.config = config
        self.alive = True

        # usage: self.say(target, message)
        self.say = client.send_privmsg

        # usage: self.joinChannel(channel_name)
        self.join_channel = client.join_channel

        # usage: self.partChannel(channel_name, reason = "")
        self.leave_channel = client.leave_channel

    def sleep(self, seconds: float) -> None:
        """
        Sleeps for seconds unless not self.alive.
        """
        start = time.monotonic()
        while time.monotonic() < start + seconds and self.alive:
            time.sleep(1)

    def kill(self) -> None:
        self.alive = False

    # Implement methods below in the subclass to subscribe to events.

    def on_channel_message(
        self, user: User, channel_name: str, message: str
    ) -> None:
        """
        Called when a channel message is received.
        """

    def on_private_message(self, user: User, message: str) -> None:
        """
        Called when a private message is received.
        """

    def on_join(self, user: User, channel_name: str) -> None:
        """
        Called when a user joins a channel.
        """

    def on_part(self, user: User, channel_name: str) -> None:
        """
        Called when a user parts a channel.
        """

    def on_quit(self, user: User) -> None:
        """
        Called when a user quits the network.
        """

    def on_connect(self) -> None:
        """
        Called when bot has connected to the network.
        """

    def on_topic(self, user: User, channel_name: str, topic: str) -> None:
        """
        Called when topic has changed on a channel.
        """

    @staticmethod
    def parse_urls(string: str) -> List[Any]:
        return re.findall(r"(https?://\S+)", string)
