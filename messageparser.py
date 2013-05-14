import re

class MessageType(object):
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
    UNKNOWN = 13

class ParsedMessage(object):
    def __init__(self, type_, **kw):
        self.type = type_
        self.params = kw

class MessageParser(object):
    """
    Class handles irc messages and notifies server_connection
    about them.
    """

    def _checkForPrivmsg(self, message):
        ":juke!~Jukkis@kosh.hut.fi PRIVMSG #testidevi :asdfadsf :D"
        privmsg_pattern = re.compile(r'''   # full host mask (1)
                    ^:((.*?)                # nick (2)
                    \!(.*?)                # username (3)
                    @(.*?))\s                # hostname (4)
                    PRIVMSG\s                # message type
                    (([\#|\!].*?)|(.*?))\s    # channel (5)(6) or nick (5)
                    :(.*.?)                # message (8)
                    ''', re.X)

        privmsg = privmsg_pattern.match(message)
        if not privmsg:
            return False

        try:
            params = {}
            type_ = None
            params['source'] = privmsg.group(2)
            params['full_mask'] = privmsg.group(1)
            params['message'] = privmsg.group(8)

            # channel
            if privmsg.group(5) == privmsg.group(6):
                params['channel'] = privmsg.group(5)
                type_ = MessageType.CHANNEL_MESSAGE
            # private
            else:
                type_ = MessageType.PRIVATE_MESSAGE
        except AttributeError:
            pass

        return ParsedMessage(type_, **params)

    def _checkForNickInUse(self, message):
        ":port80b.se.quakenet.org 433 * irckaaja :Nickname is already in use."

    def _checkForUsers(self, message):
        ":irc.cs.hut.fi 353 nettitutkabot @ #channlename :yournick @juke"
        users_pattern = re.compile(r'''
                     ^:.*?\s            # server
                     353\s              # users code
                     .*?\s              # hostname
                     [=|\@]\s
                     ([\#|\!].*?)\s     # channel (1)
                     :(.*)              # users (2)
                     ''', re.X)

        match = users_pattern.match(message)
        if not match:
            return

        channel = match.group(1)
        userlist = match.group(2).split(" ")
        return ParsedMessage(MessageType.USERS, channel_name=channel, user_list=userlist)

    def _checkForUsersEnd(self, message):
        users_pattern = re.compile(r'''
                     ^:.*?\s            # server
                     366\s                # users end code
                     .*?\s                # hostname
                     ([\#|\!].*?)\s        # channel (1)
                     :(.*)                # message (2)
                     ''', re.X)

        match = users_pattern.match(message)
        if not match:
            return

        channel = match.group(1)

        return ParsedMessage(MessageType.END_OF_USERS, channel_name=channel)

    def _checkForPing(self, message):
        if not message.startswith("PING"):
            return

        _, _, message = message.partition(" :")
        return ParsedMessage(MessageType.PING, message=message)

    def _checkForEndOfMotd(self, message):
        motd_pattern = re.compile(r'''
                                    ^:          # start and :
                                    .*?\s      # server hostname
                                    376\s      # MODE for end of motd message
                                    ''', re.X)

        if not motd_pattern.match(message):
            return

        return ParsedMessage(MessageType.END_OF_MOTD, message=message)

    def _checkForQuit(self, message):
        ":Blackrobe!~Blackrobe@c-76-118-165-126.hsd1.ma.comcast.net QUIT :Signed off"
        quit_pattern = re.compile(r'''             # fullmask (1)
                                 ^:((.*?)        # nick (2)
                                 \!(.*?)        # username (3)
                                 @(.*?))\s        # hostname (4)
                                 QUIT\s            # message type
                                 :(.*.?)        # message (5)
                                 ''', re.X)

        match = quit_pattern.match(message)
        if not match:
            return

        nick = match.group(2)
        full_mask = match.group(1)
        return ParsedMessage(MessageType.QUIT, nick=nick, full_mask=full_mask)

    def _checkForPart(self, message):
        ":godlRmue!~Olog@lekvam.no PART #day9tv"
        part_pattern = re.compile(r'''             # fullmask (1)
                                 ^:((.*?)        # nick (2)
                                 \!(.*?)        # username (3)
                                 @(.*?))\s        # hostname (4)
                                 PART\s            # message type
                                 ([\#|\!].*.?)    # channel (5)
                                 ''', re.X)

        match = part_pattern.match(message)
        if not match:
            return

        full_mask = match.group(1)
        nick = match.group(2)
        channel_name = match.group(5)

        return ParsedMessage(MessageType.PART, nick=nick, channel_name=channel_name, full_mask=full_mask)

    def _checkForJoin(self, message):
        #message = ":Blackrobe!~Blackrobe@c-76-118-165-126.hsd1.ma.comcast.net JOIN #day9tv"
        ":imsopure!webchat@p50803C58.dip.t-dialin.net JOIN :#joindota"
        join_pattern = re.compile(r'''                     # fullmask (1)
                                 ^:((.*?)                # nick (2)
                                 \!(.*?)                 # username (3)
                                 @(.*?))\s                 # hostname (4)
                                 JOIN\s:?                # message type
                                 ([\#|\!].*.?)             # channel (5)
                                 ''', re.X)

        match = join_pattern.match(message)
        if not match:
            return

        full_mask = match.group(1)
        nick = match.group(2)
        channel_name = match.group(5)

        return ParsedMessage(MessageType.JOIN, nick=nick, full_mask=full_mask, channel_name=channel_name)

    def _checkForTopicReply(self, message):
        ":dreamhack.se.quakenet.org 332 irckaaja #testidevi2 :asd"
        topic_reply_pattern = re.compile(r'''
                                         ^:.*?\s            # server
                                         332\s                # topic reply code
                                         (.*?)\s            # nick (1)
                                         ([\#|\!].*?)\s        # channel (2)
                                         :(.*)                # topic (3)
                                         ''', re.X)

        match = topic_reply_pattern.match(message)
        if not match:
            return

        nick = match.group(1)
        channel_name = match.group(2)
        topic = match.group(3)

        return ParsedMessage(MessageType.TOPIC_REPLY, nick=nick, channel_name=channel_name, topic=topic)

    def _checkForTopic(self, message):
        ":juke!~Jukkis@kosh.hut.fi TOPIC #testidevi2 :lol"
        topic_pattern = re.compile(r'''                 # fullmask (1)
                                 ^:((.*?)                # nick (2)
                                 \!(.*?)                 # username (3)
                                 @(.*?))\s                 # hostname (4)
                                 TOPIC\s:?                # message type
                                 ([\#|\!].*.?)\s        # channel (5)
                                 :(.*.?)                # topic (6)
                                 ''', re.X)
        match = topic_pattern.match(message)
        if not match:
            return

        full_mask = match.group(1)
        nick = match.group(2)
        channel_name = match.group(5)
        topic = match.group(6)

        return ParsedMessage(MessageType.TOPIC, nick=nick, full_mask=full_mask, channel_name=channel_name, topic=topic)

    def parse(self, message):
        """
        Tries to figure out what the message is.
        """
        checkers = [self._checkForEndOfMotd, self._checkForJoin, self._checkForPing,
                    self._checkForPrivmsg, self._checkForUsers, self._checkForUsersEnd,
                    self._checkForJoin, self._checkForPart, self._checkForQuit,
                    self._checkForTopic, self._checkForTopicReply]

        for checker in checkers:
            parsed_message = checker(message)
            if parsed_message:
                return parsed_message

        return ParsedMessage(MessageType.UNKNOWN, message=message)
        """
        if self._checkForEndOfMotd(message): return

        ret = self._checkForPing(message)
        if self._checkForPing(message): return

        if self._checkForPrivmsg(message): return

        if self._checkForUsers(message): return
        if self._checkForUsersEnd(message): return

        if self._checkForJoin(message): return
        if self._checkForPart(message): return
        if self._checkForQuit(message): return

        if self._checkForTopic(message): return
        if self._checkForTopicReply(message): return

        #if self.checkForError(message) : return

        self._sc.unknownMessageReceived(message)
        """
#p = MessageParser(None)
#p.checkForJoin(None)
