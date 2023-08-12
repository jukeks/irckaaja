import re
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional, Tuple


class MessageType(IntEnum):
    PRIVATE_MESSAGE = 0
    JOIN = 1
    PART = 2
    PING = 3
    QUIT = 4
    TOPIC = 5
    END_OF_MOTD = 6
    NICK_IN_USE = 7
    TOPIC_REPLY = 9
    USERS = 10
    END_OF_USERS = 11
    CHANNEL_MESSAGE = 12
    CTCP_VERSION = 13
    CTCP_PING = 14
    CTCP_TIME = 15
    CTCP_DCC = 16
    UNKNOWN = 255


@dataclass
class User:
    nick: str
    full_mask: str


@dataclass
class PrivateMessage:
    source: User
    message: str


@dataclass
class ChannelMessage:
    source: User
    message: str
    channel: str


@dataclass
class JoinMessage:
    user: User
    channel: str


@dataclass
class PartMessage:
    user: User
    channel: str


@dataclass
class QuitMessage:
    user: User
    message: Optional[str]


@dataclass
class TopicMessage:
    user: User
    channel: str
    topic: str


@dataclass
class TopicReplyMessage:
    nick: str
    channel: str
    topic: str


@dataclass
class PingMessage:
    message: str


@dataclass
class PongMessage:
    message: str


@dataclass
class UsersMessage:
    channel: str
    users: List[str]


@dataclass
class UsersEndMessage:
    channel: str


@dataclass
class EndOfMotdMessage:
    message: str


@dataclass
class CTCPVersionMessage:
    user: User


@dataclass
class CTCPPingMessage:
    user: User
    id: str
    time: str


@dataclass
class CTCPTimeMessage:
    user: User


@dataclass
class CTCPDCCMessage:
    user: User


@dataclass
class ParsedMessage:
    type: MessageType

    private_message: Optional[PrivateMessage] = None
    channel_message: Optional[ChannelMessage] = None
    ping_message: Optional[PingMessage] = None
    pong_message: Optional[PongMessage] = None
    join_message: Optional[JoinMessage] = None
    part_message: Optional[PartMessage] = None
    quit_message: Optional[QuitMessage] = None
    topic_message: Optional[TopicMessage] = None
    topic_reply_message: Optional[TopicReplyMessage] = None
    users_message: Optional[UsersMessage] = None
    users_end_message: Optional[UsersEndMessage] = None
    end_of_motd_message: Optional[EndOfMotdMessage] = None
    ctcp_version_message: Optional[CTCPVersionMessage] = None
    ctcp_ping_message: Optional[CTCPPingMessage] = None
    ctcp_time_message: Optional[CTCPTimeMessage] = None
    ctcp_dcc_message: Optional[CTCPDCCMessage] = None

    raw_message: Optional[str] = None


class MessageParser:
    """
    Class handles irc messages and notifies server_connection
    about them.
    """

    def _check_for_ctcp(self, message: str) -> bool:
        ":juke!juke@jukk.is PRIVMSG irckaaja :\x01VERSION\x01"
        try:
            return ord(message[0]) == 1 and ord(message[-1]) == 1
        except ValueError:
            return False

    def _check_for_privmsg(self, message: str) -> Optional[ParsedMessage]:
        ":juke!~Jukkis@kosh.hut.fi PRIVMSG #testidevi :asdfadsf :D"
        privmsg_pattern = re.compile(
            r"""   # full host mask (1)
                    ^:((.*?)               # nick (2)
                    \!(.*?)                # username (3)
                    @(.*?))\s              # hostname (4)
                    PRIVMSG\s              # message type
                    (([\#|\!].*?)|(.*?))\s # channel (5)(6) or nick (5)
                    :(.*.?)                # message (8)
                    """,
            re.X,
        )

        privmsg = privmsg_pattern.match(message)
        if not privmsg:
            return None

        try:
            source = privmsg.group(2)
            full_mask = privmsg.group(1)
            message = privmsg.group(8)

            user = User(source, full_mask)

            # channel
            if privmsg.group(5) == privmsg.group(6):
                channel = privmsg.group(5)
                return ParsedMessage(
                    type=MessageType.CHANNEL_MESSAGE,
                    channel_message=ChannelMessage(
                        source=user, message=message, channel=channel
                    ),
                )
            # private
            else:
                if self._check_for_ctcp(message):
                    return self._parse_ctcp_message(user, message)
                return ParsedMessage(
                    type=MessageType.PRIVATE_MESSAGE,
                    private_message=PrivateMessage(
                        source=user,
                        message=message,
                    ),
                )
        except AttributeError:
            pass

        return None

    def _parse_ctcp_message(self, user: User, message: str) -> ParsedMessage:
        if message == "\x01VERSION\x01":
            return ParsedMessage(
                MessageType.CTCP_VERSION,
                ctcp_version_message=CTCPVersionMessage(user=user),
            )

        elif message.startswith("\x01PING"):
            try:
                _, time, id = message.replace("\x01", "").split(" ")
                return ParsedMessage(
                    MessageType.CTCP_PING,
                    ctcp_ping_message=CTCPPingMessage(
                        user=user, id=id, time=time
                    ),
                )
            except ValueError:
                return ParsedMessage(MessageType.UNKNOWN, raw_message=message)

        elif message.startswith("\x01TIME\x01"):
            return ParsedMessage(
                MessageType.CTCP_TIME,
                ctcp_time_message=CTCPTimeMessage(user=user),
            )

        elif message.startswith("\x01DCC"):
            return ParsedMessage(
                MessageType.CTCP_DCC, ctcp_dcc_message=CTCPDCCMessage(user=user)
            )

        return ParsedMessage(MessageType.UNKNOWN, raw_message=message)

    def _checkForNickInUse(self, message: str) -> Optional[ParsedMessage]:
        ":port80b.se.quakenet.org 433 * irckaaja :Nickname is already in use."

    def _check_for_users(self, message: str) -> Optional[ParsedMessage]:
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
            return None

        channel = match.group(1)
        userlist = match.group(2).split(" ")
        return ParsedMessage(
            MessageType.USERS,
            users_message=UsersMessage(channel=channel, users=userlist),
        )

    def _check_for_users_end(self, message: str) -> Optional[ParsedMessage]:
        users_pattern = re.compile(
            r"""
                ^:.*?\s           # server
                366\s             # users end code
                .*?\s             # hostname
                ([\#|\!].*?)\s    # channel (1)
                :(.*)             # message (2)
                """,
            re.X,
        )

        match = users_pattern.match(message)
        if not match:
            return None

        channel = match.group(1)

        return ParsedMessage(
            MessageType.END_OF_USERS,
            users_end_message=UsersEndMessage(channel=channel),
        )

    def _check_for_ping(self, message: str) -> Optional[ParsedMessage]:
        if not message.startswith("PING"):
            return None

        _, _, message = message.partition(" :")
        return ParsedMessage(
            MessageType.PING, ping_message=PingMessage(message=message)
        )

    def _check_for_end_of_motd(self, message: str) -> Optional[ParsedMessage]:
        motd_pattern = re.compile(
            r"""
                ^:         # start and :
                .*?\s      # server hostname
                376\s      # MODE for end of motd message
                """,
            re.X,
        )

        if not motd_pattern.match(message):
            return None

        return ParsedMessage(
            MessageType.END_OF_MOTD,
            end_of_motd_message=EndOfMotdMessage(message=message),
        )

    def _check_for_quit(self, message: str) -> Optional[ParsedMessage]:
        ":user!~user@c-111-222-00-123.example.net QUIT :Signed off"
        quit_pattern = re.compile(
            r"""             # fullmask (1)
                ^:((.*?)     # nick (2)
                \!(.*?)      # username (3)
                @(.*?))\s    # hostname (4)
                QUIT\s       # message type
                :(.*.?)      # message (5)
                """,
            re.X,
        )

        match = quit_pattern.match(message)
        if not match:
            return None

        nick = match.group(2)
        full_mask = match.group(1)
        quit_message = match.group(5)
        user = User(nick=nick, full_mask=full_mask)
        return ParsedMessage(
            MessageType.QUIT,
            quit_message=QuitMessage(user=user, message=quit_message),
        )

    def _check_for_part(self, message: str) -> Optional[ParsedMessage]:
        ":user!~user@example.org PART #example"
        part_pattern = re.compile(
            r"""                  # fullmask (1)
                    ^:((.*?)      # nick (2)
                    \!(.*?)       # username (3)
                    @(.*?))\s     # hostname (4)
                    PART\s        # message type
                    ([\#|\!].*.?) # channel (5)
                    """,
            re.X,
        )

        match = part_pattern.match(message)
        if not match:
            return None

        full_mask = match.group(1)
        nick = match.group(2)
        user = User(nick=nick, full_mask=full_mask)
        channel_name = match.group(5)

        return ParsedMessage(
            MessageType.PART,
            part_message=PartMessage(
                user=user,
                channel=channel_name,
            ),
        )

    def _check_for_join(self, message: str) -> Optional[ParsedMessage]:
        ":user!user@example.org JOIN :#example"
        join_pattern = re.compile(
            r"""              # fullmask (1)
                ^:((.*?)      # nick (2)
                \!(.*?)       # username (3)
                @(.*?))\s     # hostname (4)
                JOIN\s:?      # message type
                ([\#|\!].*.?) # channel (5)
                """,
            re.X,
        )

        match = join_pattern.match(message)
        if not match:
            return None

        full_mask = match.group(1)
        nick = match.group(2)
        user = User(nick=nick, full_mask=full_mask)
        channel_name = match.group(5)

        return ParsedMessage(
            MessageType.JOIN,
            join_message=JoinMessage(user=user, channel=channel_name),
        )

    def _check_for_topic_reply(self, message: str) -> Optional[ParsedMessage]:
        ":dreamhack.se.quakenet.org 332 irckaaja #testidevi2 :asd"
        topic_reply_pattern = re.compile(
            r"""
                ^:.*?\s        # server
                332\s          # topic reply code
                (.*?)\s        # nick (1)
                ([\#|\!].*?)\s # channel (2)
                :(.*)          # topic (3)
                """,
            re.X,
        )

        match = topic_reply_pattern.match(message)
        if not match:
            return None

        nick = match.group(1)
        channel_name = match.group(2)
        topic = match.group(3)

        return ParsedMessage(
            MessageType.TOPIC_REPLY,
            topic_reply_message=TopicReplyMessage(
                nick=nick, channel=channel_name, topic=topic
            ),
        )

    def _check_for_topic(self, message: str) -> Optional[ParsedMessage]:
        ":user!~user@example.org TOPIC #example :lol"
        topic_pattern = re.compile(
            r"""                 # fullmask (1)
                ^:((.*?)         # nick (2)
                \!(.*?)          # username (3)
                @(.*?))\s        # hostname (4)
                TOPIC\s:?        # message type
                ([\#|\!].*.?)\s  # channel (5)
                :(.*.?)          # topic (6)
                """,
            re.X,
        )
        match = topic_pattern.match(message)
        if not match:
            return None

        full_mask = match.group(1)
        nick = match.group(2)
        user = User(nick=nick, full_mask=full_mask)
        channel_name = match.group(5)
        topic = match.group(6)

        return ParsedMessage(
            MessageType.TOPIC,
            topic_message=TopicMessage(
                user=user,
                topic=topic,
                channel=channel_name,
            ),
        )

    def _parse_message(self, message: str) -> Optional[ParsedMessage]:
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

        return ParsedMessage(MessageType.UNKNOWN, raw_message=message)

    def parse_buffer(self, buff: str) -> Tuple[List[ParsedMessage], str]:
        """
        Parses buffer to ParsedMessages.
        Returns list of ParsedMessages and remainder of buff.
        """
        parsed_messages = []
        while "\r\n" in buff:
            message, _, buff = buff.partition("\r\n")
            parsed = self._parse_message(message)
            if parsed is None:
                continue
            parsed_messages.append(parsed)

        return parsed_messages, buff
