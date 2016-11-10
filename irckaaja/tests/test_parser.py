import unittest

from irckaaja.messageparser import *


class TestParser(unittest.TestCase):
    def test_private_message(self):
        private_msg = ":juke!juke@jukk.is PRIVMSG irckaaja :lol"
        parser = MessageParser()
        parsed = parser._check_for_privmsg(private_msg)
        self.assertTrue(parsed, 'Message was not correctly parsed.')

        self.assertEqual(parsed.type, MessageType.PRIVATE_MESSAGE,
                         'Message was not recognized as PRIVATE_MESSAGE')

        self.assertEqual(parsed.params['source'], 'juke',
                         'Nick was not parsed from PRIVATE_MESSAGE')
        self.assertEqual(parsed.params['message'], 'lol',
                         'Message was not parsed from message')

    def test_channel_message(self):
        channel_msg = ":juke!~Jukkis@kosh.hut.fi PRIVMSG #testidevi :asdfadsf"
        parser = MessageParser()
        parsed = parser._check_for_privmsg(channel_msg)
        self.assertTrue(parsed, 'CHANNEL_MESSAGE was not correctly parsed.')

        self.assertEqual(parsed.type, MessageType.CHANNEL_MESSAGE,
                         'Message was not recognized as CHANNEL_MESSAGE')

        self.assertEqual(parsed.params['source'], 'juke',
                         'Nick was not parsed from message')
        self.assertEqual(parsed.params['message'], 'asdfadsf',
                         'Message was not parsed from message')
        self.assertEqual(parsed.params['channel_name'], '#testidevi',
                         'Channel name was not parsed from message.')

    def test_ctcp(self):
        message = '\x01VERSION\x01'
        parser = MessageParser()
        self.assertTrue(parser._check_for_ctcp(message))

    def test_users_message(self):
        message = (":irc.cs.hut.fi 353 nettitutkabot @ #channelname "
                   ":yournick @juke")

        parser = MessageParser()
        parsed = parser._check_for_users(message)
        self.assertTrue(parsed, 'USERS was not correctly parsed.')
        self.assertEqual(parsed.type, MessageType.USERS)
        self.assertEqual(parsed.params['channel_name'], '#channelname',
                         'Channel name was not parsed correctly')
        self.assertEqual(parsed.params['user_list'], ['yournick', '@juke'],
                         'Channel users were not parsed correctly')

    def test_users_end_message(self):
        message = (":irc.cs.hut.fi 366 nettitutkabot @ #channelname "
                   ":yournick @juke")

        parser = MessageParser()
        parsed = parser._check_for_users_end(message)
        self.assertTrue(parsed, 'End of users was not correctly parsed.')
        self.assertEqual(parsed.type, MessageType.END_OF_USERS)
        self.assertEqual(parsed.params['channel_name'], '#channelname',
                         'Channel name was not parsed correctly')

    def test_join_message(self):
        # some servers have : before channel
        message1 = ":nick1!webchat@123123123.example.net JOIN :#channel"
        message2 = ":nick2!~Nick2@c-123-123-123-123.net JOIN !channel"

        parser = MessageParser()
        parsed = parser._check_for_join(message1)
        self.assertTrue(parsed, 'Join was not correctly parsed.')
        self.assertTrue(parsed.type, MessageType.JOIN)
        self.assertEqual(parsed.params['nick'], 'nick1')
        self.assertEqual(parsed.params['channel_name'], '#channel')

        parsed = parser._check_for_join(message2)
        self.assertTrue(parsed, 'Join was not correctly parsed.')
        self.assertTrue(parsed.type, MessageType.JOIN)
        self.assertEqual(parsed.params['nick'], 'nick2')
        self.assertEqual(parsed.params['channel_name'], '!channel')

    def test_part_message(self):
        message = ":nick!~Nick@asdf.fi PART #channeltv"

        parser = MessageParser()
        parsed = parser._check_for_part(message)
        self.assertTrue(parsed, 'PART was not correctly parsed.')
        self.assertTrue(parsed.type, MessageType.PART)
        self.assertEqual(parsed.params['nick'], 'nick')
        self.assertEqual(parsed.params['channel_name'], '#channeltv')

    def test_quit_message(self):
        message = ":nick!~Nick@asdf.fi QUIT :Signed off"

        parser = MessageParser()
        parsed = parser._check_for_quit(message)
        self.assertTrue(parsed, 'QUIT was not correctly parsed.')
        self.assertTrue(parsed.type, MessageType.PART)
        self.assertEqual(parsed.params['nick'], 'nick')

    def test_parse_messages(self):
        buff = (
            ":nick!~Nick@asdf.fi PART #channeltv\r\n"
            ":nick!~Nick@asdf.fi QUIT :Signed off\r\n"
            ":nick1!webchat@123123123.example.net JOIN :#channel\r\n"
            ":irc.cs.hut.fi 353 nettitutkabot @ #channelname "
            ":yournick @juke\r\n"
            ":juke!juke@jukk.is PRIVMSG irckaaja :lol\r\n"
            "asdf"
        )

        parser = MessageParser()
        messages, remainder = parser.parse_buffer(buff)
        self.assertEqual(len(messages), 5)
        self.assertEqual(remainder, "asdf")

        parsed_types = [message.type for message in messages]
        expected_types = [MessageType.PART, MessageType.QUIT, MessageType.JOIN,
                          MessageType.USERS, MessageType.PRIVATE_MESSAGE]
        self.assertEqual(parsed_types, expected_types)

if __name__ == '__main__':
    unittest.main()
