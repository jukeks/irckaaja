from irckaaja.botscript import BotScript


class HelloWorld(BotScript):
    """
    A simple script class. Only responds to messages starting "moi"
    in every channel in a network.
    """

    def on_channel_message(
        self, nick: str, channel_name: str, message: str, full_mask: str
    ) -> None:
        if message.startswith("moi"):
            self.say(channel_name, "moi, " + nick)
            return
