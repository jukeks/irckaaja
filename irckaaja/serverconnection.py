import socket
import time
from threading import Thread
from messageparser import MessageParser, ParsedMessage, MessageType
from channel import IrcChannel
from dynamicmodule import DynamicModule

# Source: http://blog.initprogram.com/2010/10/14/a-quick-basic-primer-on-the-irc-protocol/


class ServerConnection(object):
    """
    Class handling irc servers.
    """
    PING_INTERVAL_THRESHOLD = 300  # 300 seconds

    def __init__(self, networkname, server_config, bot_config, joinlist, modules_config):
        self.alive = True
        self.connected = False
        self.hostname = server_config['hostname']
        self.port = int(server_config.get('port', "6667"))
        self.nick = bot_config['nick']
        self.altnick = bot_config.get('altnick', self.nick + "_")
        self.username = bot_config['username']
        self.realname = bot_config['realname']
        self.owner = bot_config['owner']
        self.networkname = networkname

        self.joinlist = joinlist

        self._reader_thread = None
        self._parser = MessageParser()
        self._init_callback_table()
        self._socket = None

        self._channel_list = []

        self._modules_config = modules_config
        self.dynamic_modules = [DynamicModule(self, m, c) for m, c in modules_config.items()]

        self._last_ping = time.time()

    def _init_callback_table(self):
        self._receive_callbacks = {
            MessageType.PRIVATE_MESSAGE: self._private_message_received,
            MessageType.JOIN: self._join_received,
            MessageType.PART: self._part_received,
            MessageType.PING: self._ping_received,
            MessageType.QUIT: self._quit_received,
            MessageType.TOPIC: self._topic_received,
            MessageType.END_OF_MOTD: self._motd_received,
            #MessageType.NICK_IN_USE: self.ni,
            MessageType.TOPIC_REPLY: self._topic_reply_received,
            MessageType.USERS: self._users_received,
            MessageType.END_OF_USERS: self._users_end_received,
            MessageType.CHANNEL_MESSAGE: self._channel_message_received,
            MessageType.UNKNOWN: self._unknown_message_received,
            MessageType.CTCP_TIME: self._ctcp_message_received,
            MessageType.CTCP_VERSION: self._ctcp_version_received,
            MessageType.CTCP_PING: self._ctcp_message_received,
            MessageType.CTCP_DCC: self._ctcp_message_received,
        }

    def connect(self):
        """
        Tries to connect to irc server.
        """
        self._reader_thread = Thread(target=self._connection_loop)
        self._reader_thread.start()

    def _connect(self):
        while self.alive:
            try:
                if self._socket:
                    self._socket.close()

                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.connect((self.hostname, self.port))

                self.NICK(self.nick)
                self.USER(self.username, self.realname)

                self._last_ping = time.time()

                break

            except Exception as e:
                self._print_line(str(e) + " " + self.hostname)
                self._print_line("Trying again in 30 seconds.")
                self._sleep(30)

    def _connection_loop(self):
        while self.alive:
            self._connect()
            self._read()

            if not self.alive:
                break

            self._print_line("Trying again in 60 seconds.")
            self._sleep(60)

    def _write(self, message):
        """
        Prints and writes message to server.
        """
        self._print_line(message[:-1])
        self._socket.send(bytearray(message, 'utf-8'))

    def _check_ping_time(self):
        return time.time() - self._last_ping < ServerConnection.PING_INTERVAL_THRESHOLD

    def _read(self):
        """
        Reads and handles messages.
        """
        self._socket.settimeout(1.0)
        buff = ""
        while self.alive and self._check_ping_time():
            try:
                tmp = self._socket.recv(4096)
            except socket.timeout as e:
                continue
            except socket.error as e:
                self._print_line(str(e))
                break
            except KeyboardInterrupt:
                self.kill()
                return

            if not self.alive:
                break

            if not tmp:
                break

            tmp = tmp.decode('utf-8')

            buff += tmp
            parsed_messages, remainder = self._parser.parse_buffer(buff)
            buff = remainder
            self._handle_messages(parsed_messages)

        self._socket.close()
        self._print_line("Connection closed.")
        self.connected = False

    def _handle_messages(self, messages):
        """
        Handles a list of messages
        """
        for message in messages:
            self._receive_callbacks[message.type](**message.params)

    def _print_line(self, message):
        """
        Prints message with timestamp.
        """
        print(time.strftime("%H:%M:%S") + " |" + self.networkname + "| " + message)

    def NICK(self, nick):
        """
        Sets user's nick on server.
        """
        self._write("NICK " + nick + "\r\n")

    def USER(self, username, realname):
        """
        Sets username and realname to server on connect.
        """
        self._write("USER " + username + " 0 * :" + realname + "\r\n")

    def PONG(self, message):
        """
        Reply to PING.
        """
        self._write("PONG :" + message + "\r\n")

    def JOIN(self, channel):
        """
        Joins a irc channel.
        """
        self._write("JOIN :" + channel + "\r\n")

    def PART(self, channel, reason=""):
        """
        PARTs from a channel.
        """
        msg = "PART " + channel
        if reason:
            msg += " :" + reason
        self._write(msg + "\r\n")

    def PRIVMSG(self, target, message):
        """
        Sends PRIVMSG to target.
        """
        self._write("PRIVMSG " + target + " :" + message + "\r\n")

    def PING(self, message):
        """
        Sends PING to server.
        """
        self._write("PING " + message + "\r\n")

    def CTCP(self, target, message):
        self.PRIVMSG(target, str("\x01" + message + "\x01"))

    def NOTICE(self, target, message):
        self._write("NOTICE " + target + " :" + message + "\r\n")

    def _on_connect(self):
        """
        Called when connected to the network.
        """
        self.PING(self.hostname)
        self._join_channels()

        for dm in self.dynamic_modules:
            try:
                dm.instance.on_connect()
            except Exception as e:
                print(e)

    def _join_channels(self):
        """
        Joins channels specified in self.joinlist
        """
        for channel in self.joinlist:
            self.JOIN(channel)

    def kill(self):
        """
        Called when the thread is wanted dead.
        """
        self.alive = False
        for m in self.dynamic_modules:
            m.instance.kill()

    def _private_message_received(self, **kw):
        """
        Called when a private message has been received. Prints it
        and calls on_private_message() on DynamicModule instances.
        """
        source = kw['source']
        message = kw['message']
        full_mask = kw['full_mask']
        self._print_line("PRIVATE" + " <" + source + "> " + message)

        for dm in self.dynamic_modules:
            try:
                dm.instance.on_private_message(source, message, full_mask)
            except Exception as e:
                print(e)

    def _channel_message_received(self, **kw):
        """
        Called when a PRIVMSG to a channel has been received. Prints it
        and calls on_channel_message() on DynamicModule instances.
        """

        source = kw['source']
        message = kw['message']
        full_mask = kw['full_mask']
        channel = kw['channel_name']

        self._print_line(channel + " <" + source + "> " + message)

        for dm in self.dynamic_modules:
            try:
                dm.instance.on_channel_message(source, channel, message, full_mask)
            except Exception as e:
                print(e)

    def _ping_received(self, **kw):
        """
        Called when PING message has been received.
        """

        self._last_ping = time.time()
        message = kw['message']
        self.PONG(message)

    def _motd_received(self, **kw):
        """
        Called when the end of MOTD message
        has been received.
        """
        message = kw['message']

        self._print_line(message)
        if not self.connected:
            self.connected = True
            self._on_connect()

    def _find_channel_by_name(self, channel_name):
        """
        Returns a channel instance from channel_list
        matching channel_name parameter or None.
        """
        for channel in self._channel_list:
            if channel.name == channel_name:
                return channel

    def _add_channel(self, name, user_list):
        """
        Adds a channel to networks channel list.
        """
        if self._find_channel_by_name(name):
            return

        channel = IrcChannel(name, user_list)
        self._channel_list.append(channel)

    def _users_received(self, **kw):
        """
        Called when USERS message is received. Notifies
        channel instance of the users.
        """

        channel_name = kw['channel_name']
        user_list = kw['user_list']

        channel = self._find_channel_by_name(channel_name)
        if not channel:
            self._add_channel(channel_name, user_list)
            return

        channel.users_message(user_list)

    def _users_end_received(self, **kw):
        """
        Called when USERS message's end has been received.
        Notifies the channel instance.
        """

        channel_name = kw['channel_name']

        channel = self._find_channel_by_name(channel_name)
        if not channel:
            # TODO FIX
            self._print_line("REPORT THIS: usersEndReceived, channel not found")
            return

        channel.users_message_end()
        self._print_line("USERS OF " + channel_name)
        self._print_line(" ".join(channel.userlist))

    def _quit_received(self, **kw):
        """
        Called when a QUIT message has been received. Calls
        on_quit() on DynamicModules
        """

        nick = kw['nick']
        full_mask = kw['full_mask']

        for channel in self._channel_list:
            channel.remove_user(nick)

        self._print_line(nick + " has quit.")

        for dm in self.dynamic_modules:
            try:
                dm.instance.on_quit(nick, full_mask)
            except Exception as e:
                print(e)

    def _part_received(self, **kw):
        """
        Called when a PART message has been received. Calls
        on_part() on DynamicModules
        """

        nick = kw['nick']
        channel_name = kw['channel_name']
        full_mask = kw['full_mask']

        channel = self._find_channel_by_name(channel_name)
        if not channel:
            return

        channel.remove_user(nick)

        self._print_line(nick + " has parted " + channel_name)

        for dm in self.dynamic_modules:
            try:
                dm.instance.on_part(nick, channel_name, full_mask)
            except Exception as e:
                print(e)

    def _join_received(self, **kw):
        """
        Called when a JOIN message has been received. Calls
        on_join() on DynamicModules
        """

        nick = kw['nick']
        channel_name = kw['channel_name']
        full_mask = kw['full_mask']

        channel = self._find_channel_by_name(channel_name)
        if channel:
            channel.add_user(nick)

        self._print_line(nick + " has joined " + channel_name)
        for dm in self.dynamic_modules:
            try:
                dm.instance.on_join(nick, channel_name, full_mask)
            except Exception as e:
                print(e)

    def _topic_received(self, **kw):
        """
        Called when topic is changed on a channel. Calls on_topic()
        on DynamicModules
        """

        nick = kw['nick']
        channel_name = kw['channel_name']
        full_mask = kw['full_mask']
        topic = kw['topic']

        channel = self._find_channel_by_name(channel_name)
        if channel:
            channel.topic = topic

        self._print_line(nick + " changed the topic of " + channel_name + " to: " + topic)
        for dm in self.dynamic_modules:
            try:
                dm.instance.on_topic(nick, channel_name, topic, full_mask)
            except Exception as e:
                print(e)

    def _topic_reply_received(self, **kw):
        """
        Called when server responds to client's /topic or server informs
        of the topic on joined channel.
        """

        channel_name = kw['channel_name']
        topic = kw['topic']

        channel = self._find_channel_by_name(channel_name)
        if channel:
            channel.topic = topic

        self._print_line("Topic in " + channel_name + ": " + topic)

    def _ctcp_message_received(self, **kw):
        self._print_line("CTCP: " + str(kw))

    def _ctcp_version_received(self, **kw):
        ":juke!juke@jukk.is NOTICE irckaaja :VERSION ?l? hakkeroi!"
        self.NOTICE(kw['source'], "\x01VERSION irckaaja 0.1.0\x01")

    def _unknown_message_received(self, **kw):
        self._print_line(kw['message'])

    def _sleep(self, seconds):
        """
        Sleeps for seconds unless not self.alive.
        """
        start = time.time()
        while time.time() < start + seconds and self.alive:
            time.sleep(1)
