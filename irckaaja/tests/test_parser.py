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

if __name__ == '__main__':
    unittest.main()
