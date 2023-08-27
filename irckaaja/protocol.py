from dataclasses import dataclass, field
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


class Message:
    pass


@dataclass
class PrivateMessage(Message):
    source: User
    message: str


@dataclass
class ChannelMessage(Message):
    source: User
    message: str
    channel: str


@dataclass
class JoinMessage(Message):
    user: User
    channel: str


@dataclass
class PartMessage(Message):
    user: User
    channel: str


@dataclass
class QuitMessage(Message):
    user: User
    message: Optional[str]


@dataclass
class TopicMessage(Message):
    user: User
    channel: str
    topic: str


@dataclass
class TopicReplyMessage(Message):
    nick: str
    channel: str
    topic: str


@dataclass
class PingMessage(Message):
    message: str


@dataclass
class PongMessage(Message):
    message: str


@dataclass
class UsersMessage(Message):
    channel: str
    users: List[str]


@dataclass
class UsersEndMessage(Message):
    channel: str


@dataclass
class EndOfMotdMessage(Message):
    message: str


@dataclass
class CTCPVersionMessage(Message):
    user: User


@dataclass
class CTCPPingMessage(Message):
    user: User
    id: str
    time: str


@dataclass
class CTCPTimeMessage(Message):
    user: User


@dataclass
class CTCPDCCMessage:
    user: User


@dataclass
class ParsedMessage:
    type: MessageType
    message: Optional[Message] = None

    raw_message: Optional[str] = None
    prefix: Optional[str] = None
    command: Optional[str] = None
    params: List[str] = field(default_factory=list)


def stripping_partition(s: str) -> Tuple[str, str]:
    """
    <SPACE>    ::= ' ' { ' ' }
    """
    before, _, rest = s.partition(" ")
    return before, rest.lstrip(" ")


def parse_full_mask(mask: str) -> User:
    """
    <prefix>   ::= <servername> | <nick> [ '!' <user> ] [ '@' <host> ]
    """

    if "!" in mask:
        nick, _, _ = mask.partition("!")
        return User(nick=nick, full_mask=mask)
    if "@" in mask:
        nick, _, _ = mask.partition("@")
        return User(nick=nick, full_mask=mask)

    return User(nick=mask, full_mask=mask)


@dataclass
class Atoms:
    prefix: str
    command: str
    params: List[str]

    @classmethod
    def parse_params(cls, params_raw: str) -> List[str]:
        """
        <params>   ::= <SPACE> [ ':' <trailing> | <middle> <params> ]
        <middle>   ::= <Any *non-empty* sequence of octets not including SPACE
                    or NUL or CR or LF, the first of which may not be ':'>
        <trailing> ::= <Any, possibly *empty*, sequence of octets not including
                        NUL or CR or LF>
        """
        params = []
        rest = params_raw
        while rest != "":
            if rest.startswith(":"):
                # trailing i.e. last param
                params.append(rest[1:])
                break
            param, rest = stripping_partition(rest)
            params.append(param)
        return params

    @classmethod
    def from_message(cls, message: str) -> "Atoms":
        """
        From https://datatracker.ietf.org/doc/html/rfc1459#section-2.3.1

        <message>  ::= [':' <prefix> <SPACE> ] <command> <params> <crlf>
        <prefix>   ::= <servername> | <nick> [ '!' <user> ] [ '@' <host> ]
        <command>  ::= <letter> { <letter> } | <number> <number> <number>
        <SPACE>    ::= ' ' { ' ' }
        <params>   ::= <SPACE> [ ':' <trailing> | <middle> <params> ]

        <middle>   ::= <Any *non-empty* sequence of octets not including SPACE
                    or NUL or CR or LF, the first of which may not be ':'>
        <trailing> ::= <Any, possibly *empty*, sequence of octets not including
                        NUL or CR or LF>

        <crlf>     ::= CR LF
        """
        rest = message

        prefix = ""
        if rest.startswith(":"):
            prefix, rest = stripping_partition(rest)
            prefix = prefix[1:]

        command, params_raw = stripping_partition(rest)
        params = cls.parse_params(params_raw)

        return Atoms(prefix=prefix, command=command, params=params)


class MessageParser:
    def __init__(self) -> None:
        self.parsers = {
            "PRIVMSG": self.parse_privmsg,
            "JOIN": self.parse_join,
            "PART": self.parse_part,
            "PING": self.parse_ping,
            "QUIT": self.parse_quit,
            "353": self.parse_users,
            "366": self.parse_users_end,
            "376": self.parse_end_of_motd,
            "TOPIC": self.parse_topic,
            "332": self.parse_server_topic,
        }

    def parse_buffer(self, buff: str) -> Tuple[List[ParsedMessage], str]:
        """
        Parses buffer to ParsedMessages.
        Returns list of ParsedMessages and remainder of buff.
        """
        parsed_messages = []
        while "\r\n" in buff:
            message, _, buff = buff.partition("\r\n")
            parsed = self.parse_message(message)
            if parsed is None:
                continue
            parsed_messages.append(parsed)

        return parsed_messages, buff

    def parse_message(self, message: str) -> Optional[ParsedMessage]:
        atoms = Atoms.from_message(message)
        if atoms.command in self.parsers:
            return self.parsers[atoms.command](atoms.prefix, atoms.params)

        return ParsedMessage(
            MessageType.UNKNOWN,
            raw_message=message,
            prefix=atoms.prefix,
            command=atoms.command,
            params=atoms.params,
        )

    def parse_privmsg(
        self, source_full_mask: str, params: List[str]
    ) -> ParsedMessage:
        source = parse_full_mask(source_full_mask)
        target, message = params
        if target.startswith("#") or target.startswith("!"):
            return ParsedMessage(
                type=MessageType.CHANNEL_MESSAGE,
                message=ChannelMessage(
                    source=source,
                    channel=target,
                    message=message,
                ),
            )
        return ParsedMessage(
            type=MessageType.PRIVATE_MESSAGE,
            message=PrivateMessage(
                source=source,
                message=message,
            ),
        )

    def parse_join(self, full_mask: str, params: List[str]) -> ParsedMessage:
        channel = params[0]
        return ParsedMessage(
            type=MessageType.JOIN,
            message=JoinMessage(
                user=parse_full_mask(full_mask), channel=channel
            ),
        )

    def parse_part(self, full_mask: str, params: List[str]) -> ParsedMessage:
        channel = params[0]
        return ParsedMessage(
            type=MessageType.PART,
            message=PartMessage(
                user=parse_full_mask(full_mask), channel=channel
            ),
        )

    def parse_ping(self, _: str, params: List[str]) -> ParsedMessage:
        message = params[0]
        return ParsedMessage(
            type=MessageType.PING, message=PingMessage(message=message)
        )

    def parse_quit(self, full_mask: str, params: List[str]) -> ParsedMessage:
        user = parse_full_mask(full_mask)
        message = params[0]

        return ParsedMessage(
            type=MessageType.QUIT,
            message=QuitMessage(user=user, message=message),
        )

    def parse_users(self, _: str, params: List[str]) -> ParsedMessage:
        """
        :example.org 353 irckaaja @ #channelname :yournick @juke
        """
        _, _, channel, raw_user_list = params
        user_list = raw_user_list.split(" ")
        return ParsedMessage(
            type=MessageType.USERS,
            message=UsersMessage(channel=channel, users=user_list),
        )

    def parse_users_end(self, _: str, params: List[str]) -> ParsedMessage:
        """
        :example.org 366 irckaaja #channelname :End of /NAMES list.
        :another.example.org 366 irckaaja @ #channelname :End of /NAMES list.
        """
        if len(params) == 3:
            _, channel, _ = params
        else:
            _, _, channel, _ = params

        return ParsedMessage(
            type=MessageType.END_OF_USERS,
            message=UsersEndMessage(channel=channel),
        )

    def parse_end_of_motd(self, _: str, params: List[str]) -> ParsedMessage:
        """
        :example.org 376 irckaaja :End of /MOTD command.
        """
        message = params[0]
        return ParsedMessage(
            type=MessageType.END_OF_MOTD,
            message=EndOfMotdMessage(message=message),
        )

    def parse_topic(self, full_mask: str, params: List[str]) -> ParsedMessage:
        """
        :user!~user@example.org TOPIC #channelname :topic message
        """
        user = parse_full_mask(full_mask)
        channel, topic = params
        return ParsedMessage(
            type=MessageType.TOPIC,
            message=TopicMessage(
                user=user,
                channel=channel,
                topic=topic,
            ),
        )

    def parse_server_topic(self, _: str, params: List[str]) -> ParsedMessage:
        """
        :server.example.org 332 irckaaja #testchannel :let's test
        """
        nick, channel, topic = params
        return ParsedMessage(
            type=MessageType.TOPIC_REPLY,
            message=TopicReplyMessage(
                nick=nick,
                channel=channel,
                topic=topic,
            ),
        )
