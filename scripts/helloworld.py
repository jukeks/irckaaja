from botscript import BotScript


class HelloWorld(BotScript):
    '''
    A simple script class. Only responds to messages starting "moi"
    in every channel in a network.
    '''

    def on_channel_message(self, nick, channel_name, message, full_mask):
        if message.startswith("moi"):
            self.say(channel_name, "mutsis sano moi, " + nick)
            return