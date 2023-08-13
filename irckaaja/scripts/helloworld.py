from irckaaja.botscript import BotScript, User


class HelloWorld(BotScript):
    """
    A simple script class. Only responds to messages starting "hello"
    in every joined channel.
    """

    def on_channel_message(
        self, user: User, channel_name: str, message: str
    ) -> None:
        if message.startswith("hello"):
            self.say(channel_name, "hello, " + user.nick)
            return
