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

        self.reader_thread = None
        self.parser = MessageParser()
        self._init_callback_table()
        self.socket = None

        self.channel_list = []

        self.modules_config = modules_config
        self.dynamic_modules = [DynamicModule(self, m, c) for m, c in modules_config.items()]

        self._lastPing = time.time()

    def _init_callback_table(self):
        self.receive_callbacks = {
            MessageType.PRIVATE_MESSAGE: self.privateMessageReceived,
            MessageType.JOIN: self.joinReceived,
            MessageType.PART: self.partReceived,
            MessageType.PING: self.pingReceived,
            MessageType.QUIT: self.quitReceived,
            MessageType.TOPIC: self.topicReceived,
            MessageType.END_OF_MOTD: self.motdReceived,
            #MessageType.NICK_IN_USE: self.ni,
            MessageType.TOPIC_REPLY: self.topicReplyReceived,
            MessageType.USERS: self.usersReceived,
            MessageType.END_OF_USERS: self.usersEndReceived,
            MessageType.CHANNEL_MESSAGE: self.channelMessageReceived,
            MessageType.UNKNOWN: self.unknownMessageReceived,
        }

    def connect(self):
        """
        Tries to connect to irc server.
        """
        self.reader_thread = Thread(target=self._connectionLoop)
        self.reader_thread.start()

    def _connect(self):
        while self.alive:
            try:
                if self.socket:
                    self.socket.close()

                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.hostname, self.port))

                self.NICK(self.nick)
                self.USER(self.username, self.realname)

                self._lastPing = time.time()

                break

            except Exception as e:
                self._printLine(str(e) + " " + self.hostname)
                self._printLine("Trying again in 30 seconds.")
                self.sleep(30)

    def _connectionLoop(self):
        while self.alive:
            self._connect()
            self._read()

            self._printLine("Trying again in 60 seconds.")
            self.sleep(60)

    def _write(self, message):
        """
        Prints and writes message to server.
        """
        self._printLine(message[:-1])
        self.socket.send(message)

    def _check_ping_time(self):
        return time.time() - self._lastPing < ServerConnection.PING_INTERVAL_THRESHOLD

    def _read(self):
        """
        Reads and handles messages.
        """
        self.socket.settimeout(1.0)
        buff = ""
        while self.alive and self._check_ping_time():
            try:
                tmp = self.socket.recv(4096)
            except socket.timeout as e:
                continue
            except socket.error as e:
                self._printLine(str(e))
                break

            except KeyboardInterrupt:
                self.kill()
                return

            if not self.alive:
                break

            if not tmp:
                break

            buff += tmp
            buff = self._checkForMessagesAndReturnRemaining(buff)

        self.socket.close()
        self._printLine("Connection closed.")
        self.connected = False


    def _checkForMessagesAndReturnRemaining(self, buff):
        """
        Checks if buff contains any messages. If so, it parses and
        handles them and returns the remaining bytes.
        """
        while buff.find("\r\n") != -1:
            head, _, buff = buff.partition("\r\n")
            parsed = self.parser.parse(head)
            self.receive_callbacks[parsed.type](**parsed.params)

        return buff

    def _printLine(self, message):
        """
        Prints message with timestamp.
        """
        print time.strftime("%H:%M:%S") + " |" + self.networkname + "| " + message

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

    def _onConnect(self):
        """
        Called when connected to the network.
        """
        self.PING(self.hostname)
        self.joinChannels()

        for dm in self.dynamic_modules:
            try:
                dm.instance.onConnect()
            except Exception as e:
                print e

    def joinChannels(self):
        """
        Joins channels specified in self.joinlist
        """
        for channel in self.joinlist:
            self.JOIN(channel)

    def kill(self):
        """
        Called when the thread is wanted dead.
        """
        self._printLine(self.networkname + " dying.")
        self.alive = False
        for m in self.dynamic_modules:
            m.instance.kill()

    def privateMessageReceived(self, **kw):
        """
        Called when a private message has been received. Prints it
        and calls onPrivateMessage() on DynamicModule instances.
        """
        source = kw['source']
        message = kw['message']
        full_mask = kw['full_mask']
        self._printLine("PRIVATE" + " <" + source + "> " + message)

        for dm in self.dynamic_modules:
            try:
                dm.instance.onPrivateMessage(source, message, full_mask)
            except Exception as e:
                print e

    def channelMessageReceived(self, **kw):
        """
        Called when a PRIVMSG to a channel has been received. Prints it
        and calls onChannelMessage() on DynamicModule instances.
        """

        source = kw['source']
        message = kw['message']
        full_mask = kw['full_mask']
        channel = kw['channel']

        self._printLine(channel + " <" + source + "> " + message)

        for dm in self.dynamic_modules:
            try:
                dm.instance.onChannelMessage(source, channel, message, full_mask)
            except Exception as e:
                print e

    def pingReceived(self, **kw):
        """
        Called when PING message has been received.
        """

        self._lastPing = time.time()
        message = kw['message']
        self.PONG(message)

    def motdReceived(self, **kw):
        """
        Called when the end of MOTD message
        has been received.
        """
        message = kw['message']

        self._printLine(message)
        if not self.connected:
            self.connected = True
            self._onConnect()

    def findChannelByName(self, channel_name):
        """
        Returns a channel instance from channel_list
        matching channel_name parameter or None.
        """
        for channel in self.channel_list:
            if channel.name == channel_name:
                return channel

    def addChannel(self, name, user_list):
        """
        Adds a channel to networks channel list.
        """
        if self.findChannelByName(name):
            return

        channel = IrcChannel(name, user_list)
        self.channel_list.append(channel)

    def usersReceived(self, **kw):
        """
        Called when USERS message is received. Notifies
        channel instance of the users.
        """

        channel_name = kw['channel_name']
        user_list = kw['user_list']

        channel = self.findChannelByName(channel_name)
        if not channel:
            self.addChannel(channel_name, user_list)
            return

        channel.usersMessage(user_list)

    def usersEndReceived(self, **kw):
        """
        Called when USERS message's end has been received.
        Notifies the channel instance.
        """

        channel_name = kw['channel_name']

        channel = self.findChannelByName(channel_name)
        if not channel:
            # TODO FIX
            print "REPORT THIS: usersEndReceived, channel not found"
            return

        channel.usersMessageEnd()
        self._printLine("USERS OF " + channel_name)
        self._printLine(" ".join(channel.userlist))

    def quitReceived(self, **kw):
        """
        Called when a QUIT message has been received. Calls
        onQuit() on DynamicModules
        """

        nick = kw['nick']
        full_mask = kw['full_mask']

        for channel in self.channel_list:
            channel.removeUser(nick)

        self._printLine(nick + " has quit.")

        for dm in self.dynamic_modules:
            try:
                dm.instance.onQuit(nick, full_mask)
            except Exception as e:
                print e

    def partReceived(self, **kw):
        """
        Called when a PART message has been received. Calls
        onPart() on DynamicModules
        """

        nick = kw['nick']
        channel_name = kw['channel_name']
        full_mask = kw['full_mask']

        channel = self.findChannelByName(channel_name)
        if not channel:
            return

        channel.removeUser(nick)

        self._printLine(nick + " has part " + channel_name)

        for dm in self.dynamic_modules:
            try:
                dm.instance.onPart(nick, channel_name, full_mask)
            except Exception as e:
                print e

    def joinReceived(self, **kw):
        """
        Called when a JOIN message has been received. Calls
        onJoin() on DynamicModules
        """

        nick = kw['nick']
        channel_name = kw['channel_name']
        full_mask = kw['full_mask']

        channel = self.findChannelByName(channel_name)
        if channel:
            channel.addUser(nick)

        self._printLine(nick + " has joined " + channel_name)
        for dm in self.dynamic_modules:
            try:
                dm.instance.onJoin(nick, channel_name, full_mask)
            except Exception as e:
                print e

    def topicReceived(self, **kw):
        """
        Called when topic is changed on a channel. Calls onTopic()
        on DynamicModules
        """

        nick = kw['nick']
        channel_name = kw['channel_name']
        full_mask = kw['full_mask']
        topic = kw['topic']

        channel = self.findChannelByName(channel_name)
        if channel:
            channel.topic = topic

        self._printLine(nick + " changed the topic of " + channel_name + " to: " + topic)
        for dm in self.dynamic_modules:
            try:
                dm.instance.onTopic(nick, channel_name, topic, full_mask)
            except Exception as e:
                print e

    def topicReplyReceived(self, **kw):
        """
        Called when server responds to client's /topic or server informs
        of the topic on joined channel.
        """

        channel_name = kw['channel_name']
        topic = kw['topic']

        channel = self.findChannelByName(channel_name)
        if channel:
            channel.topic = topic

        self._printLine("Topic in " + channel_name + ": " + topic)


    def unknownMessageReceived(self, **kw):
        self._printLine(kw['message'])

    def sleep(self, seconds):
        """
        Sleeps for seconds unless not self.alive.
        """
        start = time.time()
        while time.time() < start + seconds and self.alive:
            time.sleep(1)
