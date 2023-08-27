from typing import cast

from parser_tests import data as parser_test_cases

from irckaaja.protocol import (
    Atoms,
    ChannelMessage,
    JoinMessage,
    MessageParser,
    MessageType,
    PartMessage,
    PrivateMessage,
    QuitMessage,
    UsersEndMessage,
    UsersMessage,
    parse_full_mask,
)


def test_private_message() -> None:
    private_msg = ":juke!juke@example.org PRIVMSG irckaaja :lol"
    parser = MessageParser()
    parsed = parser.parse_message(private_msg)
    assert parsed

    assert parsed.type == MessageType.PRIVATE_MESSAGE
    assert parsed.message
    msg = cast(PrivateMessage, parsed.message)
    assert msg.source.nick == "juke"
    assert msg.message == "lol"


def test_channel_message() -> None:
    channel_msg = ":juke!~Jukkis@example.org PRIVMSG #testchannel :asdfadsf"
    parser = MessageParser()
    parsed = parser.parse_message(channel_msg)
    assert parsed
    assert parsed.type == MessageType.CHANNEL_MESSAGE
    msg = cast(ChannelMessage, parsed.message)
    assert msg
    assert msg.source.nick == "juke"
    assert msg.message == "asdfadsf"
    assert msg.channel == "#testchannel"


def test_ctcp() -> None:
    message = "\x01VERSION\x01"
    parser = MessageParser()
    assert parser.parse_message(message)


def test_users_message() -> None:
    message = ":example.org 353 user @ #channelname :yournick @juke"
    parser = MessageParser()
    parsed = parser.parse_message(message)
    assert parsed
    assert parsed.type == MessageType.USERS
    msg = cast(UsersMessage, parsed.message)
    assert msg
    assert msg.channel == "#channelname"
    assert msg.users == ["yournick", "@juke"]


def test_users_end_message() -> None:
    message = ":example.org 366 user @ #channelname :End of /NAMES list."
    parser = MessageParser()
    parsed = parser.parse_message(message)
    assert parsed
    assert parsed.type == MessageType.END_OF_USERS
    msg = cast(UsersEndMessage, parsed.message)
    assert msg
    assert msg.channel == "#channelname"


def test_join_message() -> None:
    message1 = ":nick1!webchat@123123123.example.net JOIN :#channel"
    message2 = ":nick2!~Nick2@c-123-123-123-123.net JOIN !channel"
    parser = MessageParser()

    parsed = parser.parse_message(message1)
    assert parsed
    assert parsed.type == MessageType.JOIN
    msg = cast(JoinMessage, parsed.message)
    assert msg
    assert msg.user.nick == "nick1"
    assert msg.channel == "#channel"

    parsed = parser.parse_message(message2)
    assert parsed
    assert parsed.type == MessageType.JOIN
    msg = cast(JoinMessage, parsed.message)
    assert msg
    assert msg.user.nick == "nick2"
    assert msg.channel == "!channel"


def test_part_message() -> None:
    message = ":nick!~Nick@asdf.fi PART #channeltv"
    parser = MessageParser()
    parsed = parser.parse_message(message)
    assert parsed
    assert parsed.type == MessageType.PART
    msg = cast(PartMessage, parsed.message)
    assert msg
    assert msg.user.nick == "nick"
    assert msg.channel == "#channeltv"


def test_quit_message() -> None:
    message = ":nick!~Nick@asdf.fi QUIT :Signed off"
    parser = MessageParser()
    parsed = parser.parse_message(message)
    assert parsed
    assert parsed.type == MessageType.QUIT
    msg = cast(QuitMessage, parsed.message)
    assert msg
    assert msg.user.nick == "nick"


def test_parse_messages() -> None:
    buff = (
        ":nick!~Nick@asdf.fi PART #channeltv\r\n"
        ":nick!~Nick@asdf.fi QUIT :Signed off\r\n"
        ":nick1!webchat@123123123.example.net JOIN :#channel\r\n"
        ":example.org 353 nettitutkabot @ #channelname :yournick @juke\r\n"
        ":juke!juke@jukk.is PRIVMSG irckaaja :lol\r\n"
        "asdf"
    )
    parser = MessageParser()
    messages, remainder = parser.parse_buffer(buff)
    assert len(messages) == 5
    assert remainder == "asdf"
    parsed_types = [message.type for message in messages]
    expected_types = [
        MessageType.PART,
        MessageType.QUIT,
        MessageType.JOIN,
        MessageType.USERS,
        MessageType.PRIVATE_MESSAGE,
    ]
    assert parsed_types == expected_types


def test_atom_parsing_cases() -> None:
    cases = parser_test_cases.msg_split["tests"]
    for case in cases:
        if case["input"].startswith("@"):
            # tags not yet supported
            continue

        parsed = Atoms.from_message(case["input"])
        expected = case["atoms"]
        assert parsed.command == expected["verb"], case["input"]
        assert parsed.params == expected.get("params", []), case["input"]


def test_userhost_parsing_cases() -> None:
    cases = parser_test_cases.userhost_split["tests"]
    for case in cases:
        parsed = parse_full_mask(case["source"])
        expected = case["atoms"]
        assert parsed.nick == expected.get("nick", ""), case["source"]

    assert True
