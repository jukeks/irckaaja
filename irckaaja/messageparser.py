import re


class MessageType:
    PRIVATE_MESSAGE = 0
    JOIN = 1
    PART = 2
    PING = 3
    QUIT = 4
    TOPIC = 5
    END_OF_MOTD = 6
    NICK_IN_USE = 7
    TOPIC = 8
    TOPIC_REPLY = 9
    USERS = 10
    END_OF_USERS = 11
    CHANNEL_MESSAGE = 12
    CTCP_VERSION = 13
    CTCP_PING = 14
    CTCP_TIME = 15
    CTCP_DCC = 16
    UNKNOWN = 255


class ParsedMessage:
    def __init__(self, type_, **kw):
        self.type = type_
        self.params = kw


class MessageParser:
    """
    Class handles irc messages and notifies server_connection
    about them.
    """

    def _check_for_ctcp(self, message):
        ":juke!juke@jukk.is PRIVMSG irckaaja :\x01VERSION\x01"
        try:
            return ord(message[0]) == 1 and ord(message[-1]) == 1
        except ValueError:
            pass

    def _check_for_privmsg(self, message):
        ":juke!~Jukkis@kosh.hut.fi PRIVMSG #testidevi :asdfadsf :D"
        privmsg_pattern = re.compile(
            r"""   # full host mask (1)
                    ^:((.*?)                # nick (2)
                    \!(.*?)                # username (3)
                    @(.*?))\s                # hostname (4)
                    PRIVMSG\s                # message type
                    (([\#|\!].*?)|(.*?))\s    # channel (5)(6) or nick (5)
                    :(.*.?)                # message (8)
                    """,
            re.X,
        )

        privmsg = privmsg_pattern.match(message)
        if not privmsg:
            return False

        params = {}
        type_ = None
        try:
            params["source"] = privmsg.group(2)
            params["full_mask"] = privmsg.group(1)
            params["message"] = privmsg.group(8)

            # channel
            if privmsg.group(5) == privmsg.group(6):
                params["channel_name"] = privmsg.group(5)
                type_ = MessageType.CHANNEL_MESSAGE
            # private
            else:
                type_ = MessageType.PRIVATE_MESSAGE
        except AttributeError:
            return

        if self._check_for_ctcp(params["message"]):
            return self._parse_ctcp_message(params)

        return ParsedMessage(type_, **params)

    def _parse_ctcp_message(self, params):
        message = params["message"]

        if message == "\x01VERSION\x01":
            return ParsedMessage(MessageType.CTCP_VERSION, **params)

        elif message.startswith("\x01PING"):
            try:
                _, params["time"], params["id"] = message.replace("\x01", "").split(" ")
                return ParsedMessage(MessageType.CTCP_PING, **params)
            except ValueError:
                return MessageType.UNKNOWN

        elif message.startswith("\x01TIME\x01"):
            return ParsedMessage(MessageType.CTCP_TIME, **params)

        elif message.startswith("\x01DCC"):
            return ParsedMessage(MessageType.CTCP_DCC, **params)

        else:
            return MessageType.UNKNOWN

    def _checkForNickInUse(self, message):
        ":port80b.se.quakenet.org 433 * irckaaja :Nickname is already in use."

    def _check_for_users(self, message):
        ":irc.cs.hut.fi 353 nettitutkabot @ #channlename :yournick @juke"
        users_pattern = re.compile(
            r"""
                     ^:.*?\s            # server
                     353\s              # users code
                     .*?\s              # hostname
                     [=|\@]\s
                     ([\#|\!].*?)\s     # channel (1)
                     :(.*)              # users (2)
                     """,
            re.X,
        )

        match = users_pattern.match(message)
        if not match:
            return

        channel = match.group(1)
        userlist = match.group(2).split(" ")
        return ParsedMessage(MessageType.USERS, channel_name=channel, user_list=userlist)

    def _check_for_users_end(self, message):
        users_pattern = re.compile(
            r"""
                     ^:.*?\s            # server
                     366\s                # users end code
                     .*?\s                # hostname
                     ([\#|\!].*?)\s        # channel (1)
                     :(.*)                # message (2)
                     """,
            re.X,
        )

        match = users_pattern.match(message)
        if not match:
            return

        channel = match.group(1)

        return ParsedMessage(MessageType.END_OF_USERS, channel_name=channel)

    def _check_for_ping(self, message):
        if not message.startswith("PING"):
            return

        _, _, message = message.partition(" :")
        return ParsedMessage(MessageType.PING, message=message)

    def _check_for_end_of_motd(self, message):
        motd_pattern = re.compile(
            r"""
                                    ^:          # start and :
                                    .*?\s      # server hostname
                                    376\s      # MODE for end of motd message
                                    """,
            re.X,
        )

        if not motd_pattern.match(message):
            return

        return ParsedMessage(MessageType.END_OF_MOTD, message=message)

    def _check_for_quit(self, message):
        ":Blackrobe!~Blackrobe@c-76-118-165-126.hsd1.ma.comcast.net QUIT :Signed off"
        quit_pattern = re.compile(
            r"""             # fullmask (1)
                                 ^:((.*?)        # nick (2)
                                 \!(.*?)        # username (3)
                                 @(.*?))\s        # hostname (4)
                                 QUIT\s            # message type
                                 :(.*.?)        # message (5)
                                 """,
            re.X,
        )

        match = quit_pattern.match(message)
        if not match:
            return

        nick = match.group(2)
        full_mask = match.group(1)
        return ParsedMessage(MessageType.QUIT, nick=nick, full_mask=full_mask)

    def _check_for_part(self, message):
        ":godlRmue!~Olog@lekvam.no PART #day9tv"
        part_pattern = re.compile(
            r"""             # fullmask (1)
                                 ^:((.*?)        # nick (2)
                                 \!(.*?)        # username (3)
                                 @(.*?))\s        # hostname (4)
                                 PART\s            # message type
                                 ([\#|\!].*.?)    # channel (5)
                                 """,
            re.X,
        )

        match = part_pattern.match(message)
        if not match:
            return

        full_mask = match.group(1)
        nick = match.group(2)
        channel_name = match.group(5)

        return ParsedMessage(MessageType.PART, nick=nick, channel_name=channel_name, full_mask=full_mask)

    def _check_for_join(self, message):
        # message = ":Blackrobe!~Blackrobe@c-76-118-165-126.hsd1.ma.comcast.net JOIN #day9tv"
        ":imsopure!webchat@p50803C58.dip.t-dialin.net JOIN :#joindota"
        join_pattern = re.compile(
            r"""                     # fullmask (1)
                                 ^:((.*?)                # nick (2)
                                 \!(.*?)                 # username (3)
                                 @(.*?))\s                 # hostname (4)
                                 JOIN\s:?                # message type
                                 ([\#|\!].*.?)             # channel (5)
                                 """,
            re.X,
        )

        match = join_pattern.match(message)
        if not match:
            return

        full_mask = match.group(1)
        nick = match.group(2)
        channel_name = match.group(5)

        return ParsedMessage(MessageType.JOIN, nick=nick, full_mask=full_mask, channel_name=channel_name)

    def _check_for_topic_reply(self, message):
        ":dreamhack.se.quakenet.org 332 irckaaja #testidevi2 :asd"
        topic_reply_pattern = re.compile(
            r"""
                                         ^:.*?\s            # server
                                         332\s                # topic reply code
                                         (.*?)\s            # nick (1)
                                         ([\#|\!].*?)\s        # channel (2)
                                         :(.*)                # topic (3)
                                         """,
            re.X,
        )

        match = topic_reply_pattern.match(message)
        if not match:
            return

        nick = match.group(1)
        channel_name = match.group(2)
        topic = match.group(3)

        return ParsedMessage(MessageType.TOPIC_REPLY, nick=nick, channel_name=channel_name, topic=topic)

    def _check_for_topic(self, message):
        ":juke!~Jukkis@kosh.hut.fi TOPIC #testidevi2 :lol"
        topic_pattern = re.compile(
            r"""                 # fullmask (1)
                                 ^:((.*?)                # nick (2)
                                 \!(.*?)                 # username (3)
                                 @(.*?))\s                 # hostname (4)
                                 TOPIC\s:?                # message type
                                 ([\#|\!].*.?)\s        # channel (5)
                                 :(.*.?)                # topic (6)
                                 """,
            re.X,
        )
        match = topic_pattern.match(message)
        if not match:
            return

        full_mask = match.group(1)
        nick = match.group(2)
        channel_name = match.group(5)
        topic = match.group(6)

        return ParsedMessage(
            MessageType.TOPIC,
            nick=nick,
            full_mask=full_mask,
            channel_name=channel_name,
            topic=topic,
        )

    def _parse_message(self, message):
        """
        Tries to figure out what the message is.
        """
        checkers = [
            self._check_for_end_of_motd,
            self._check_for_join,
            self._check_for_ping,
            self._check_for_privmsg,
            self._check_for_users,
            self._check_for_users_end,
            self._check_for_part,
            self._check_for_quit,
            self._check_for_topic,
            self._check_for_topic_reply,
        ]

        for checker in checkers:
            parsed_message = checker(message)
            if parsed_message:
                return parsed_message

        return ParsedMessage(MessageType.UNKNOWN, message=message)

    def parse_buffer(self, buff):
        """
        Parses buffer to ParsedMessages.
        Returns list of ParsedMessages and remainder of buff.
        """
        parsed_messages = []
        while "\r\n" in buff:
            message, _, buff = buff.partition("\r\n")
            parsed = self._parse_message(message)
            parsed_messages.append(parsed)

        return parsed_messages, buff
