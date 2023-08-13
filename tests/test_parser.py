import unittest

from irckaaja.protocol import MessageParser, MessageType


class TestParser(unittest.TestCase):
    def test_private_message(self) -> None:
        private_msg = ":juke!juke@example.org PRIVMSG irckaaja :lol"
        parser = MessageParser()
        parsed = parser._check_for_privmsg(private_msg)
        assert parsed

        assert parsed.type == MessageType.PRIVATE_MESSAGE
        assert parsed.private_message
        assert parsed.private_message.source.nick == "juke"
        assert parsed.private_message.message == "lol"

    def test_channel_message(self) -> None:
        channel_msg = ":juke!~Jukkis@example.org PRIVMSG #testidevi :asdfadsf"
        parser = MessageParser()
        parsed = parser._check_for_privmsg(channel_msg)
        assert parsed
        assert parsed.type == MessageType.CHANNEL_MESSAGE
        msg = parsed.channel_message
        assert msg
        assert msg.source.nick == "juke"
        assert msg.message == "asdfadsf"
        assert msg.channel == "#testidevi"

    def test_ctcp(self) -> None:
        message = "\x01VERSION\x01"
        parser = MessageParser()
        assert parser._check_for_ctcp(message)

    def test_users_message(self) -> None:
        message = (
            ":irc.cs.hut.fi 353 nettitutkabot @ #channelname :yournick @juke"
        )
        parser = MessageParser()
        parsed = parser._check_for_users(message)
        assert parsed
        assert parsed.type == MessageType.USERS
        msg = parsed.users_message
        assert msg
        assert msg.channel == "#channelname"
        assert msg.users == ["yournick", "@juke"]

    def test_users_end_message(self) -> None:
        message = (
            ":irc.cs.hut.fi 366 nettitutkabot @ #channelname :yournick @juke"
        )
        parser = MessageParser()
        parsed = parser._check_for_users_end(message)
        assert parsed
        assert parsed.type == MessageType.END_OF_USERS
        msg = parsed.users_end_message
        assert msg
        assert msg.channel == "#channelname"

    def test_join_message(self) -> None:
        message1 = ":nick1!webchat@123123123.example.net JOIN :#channel"
        message2 = ":nick2!~Nick2@c-123-123-123-123.net JOIN !channel"
        parser = MessageParser()

        parsed = parser._check_for_join(message1)
        assert parsed
        assert parsed.type == MessageType.JOIN
        msg = parsed.join_message
        assert msg
        assert msg.user.nick == "nick1"
        assert msg.channel == "#channel"

        parsed = parser._check_for_join(message2)
        assert parsed
        assert parsed.type == MessageType.JOIN
        msg = parsed.join_message
        assert msg
        assert msg.user.nick == "nick2"
        assert msg.channel == "!channel"

    def test_part_message(self) -> None:
        message = ":nick!~Nick@asdf.fi PART #channeltv"
        parser = MessageParser()
        parsed = parser._check_for_part(message)
        assert parsed
        assert parsed.type == MessageType.PART
        msg = parsed.part_message
        assert msg
        assert msg.user.nick == "nick"
        assert msg.channel == "#channeltv"

    def test_quit_message(self) -> None:
        message = ":nick!~Nick@asdf.fi QUIT :Signed off"
        parser = MessageParser()
        parsed = parser._check_for_quit(message)
        assert parsed
        assert parsed.type == MessageType.QUIT
        msg = parsed.quit_message
        assert msg
        assert msg.user.nick == "nick"

    def test_parse_messages(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
