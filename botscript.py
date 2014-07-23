import time
import re


class BotScript(object):
    """
    "Abstract" script class. Should be inherited by script classes.
    See HelloWorld in scripts.helloworld.py for example.
    """

    def __init__(self, server_connection, config):
        self.server_connection = server_connection
        self.config = config
        self.alive = True

        # usage: self.say(target, message)
        self.say = server_connection.PRIVMSG

        # usage: self.joinChannel(channel_name)
        self.join_channel = server_connection.JOIN

        #usage: self.partChannel(channel_name, reason = "")
        self.part_channel = server_connection.PART


    def sleep(self, seconds):
        """
        Sleeps for seconds unless not self.alive.
        """
        start = time.time()
        while time.time() < start + seconds and self.alive:
            time.sleep(1)

    def kill(self):
        self.alive = False


    # Methods below can be implemented in your script class if you like.
    # That way you can subscribe to those messages.
    def on_channel_message(self, nick, target, message, full_mask):
        """
        Called when a channel message is received.
        """
        pass

    def on_private_message(self, nick, message, full_mask):
        """
        Called when a private message is received.
        """
        pass

    def on_join(self, nick, channel_name, full_mask):
        """
        Called when a user joins a channel.
        """
        pass

    def on_part(self, nick, channel_name, full_mask):
        """
        Called when a user parts a channel.
        """
        pass

    def on_quit(self, nick, full_mask):
        """
        Called when a user quits the network.
        """
        pass

    def on_connect(self):
        """
        Called when bot has connected to the network.
        """
        pass

    def on_topic(self, nick, channelname, topic, full_mask):
        """
        Called when topic has changed on a channel.
        """
        pass

    @staticmethod
    def parse_urls(string):
        return re.findall(r'(https?://\S+)', string)
