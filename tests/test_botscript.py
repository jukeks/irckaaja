from typing import Tuple
from unittest.mock import Mock

from irckaaja.botscript import BotScript
from irckaaja.client import IrcClient
from irckaaja.config import BotConfig, ServerConfig
from irckaaja.connection import IrcConnection
from irckaaja.dynamicmodule import DynamicModule
from irckaaja.protocol import (
    ChannelMessage,
    EndOfMotdMessage,
    JoinMessage,
    MessageType,
    ParsedMessage,
    PartMessage,
    PrivateMessage,
    QuitMessage,
    TopicMessage,
    TopicReplyMessage,
    User,
    UsersEndMessage,
    UsersMessage,
)


def get_server_config() -> ServerConfig:
    return ServerConfig(
        name="123",
        hostname="example.org",
        port=6666,
        channels=[],
    )


def get_bot_config() -> BotConfig:
    return BotConfig(
        nick="tester",
        altnick="tester2",
        realname="Testy Tester",
        username="test",
        owner="developer",
    )


def get_user() -> User:
    return User(nick="user1", full_mask="user1@example.org")


def get_script_and_client() -> Tuple[Mock, IrcClient]:
    script = Mock(spec=BotScript)
    conn = Mock(spec=IrcConnection)

    client = IrcClient(
        server_config=get_server_config(),
        bot_config=get_bot_config(),
        modules_config={},
    )
    dm = DynamicModule(config={}, connection=client, module_name="HelloWorld")
    dm.instance = script
    client.dynamic_modules = [dm]
    client._connection = conn
    return script, client


def test_client_calls_script_on_private_message() -> None:
    script, client = get_script_and_client()
    client._handle_messages(
        [
            ParsedMessage(
                type=MessageType.PRIVATE_MESSAGE,
                private_message=PrivateMessage(
                    source=get_user(), message="Hello!"
                ),
            )
        ]
    )

    script.on_private_message.assert_called_once()


def test_client_calls_script_on_channel_message() -> None:
    script, client = get_script_and_client()
    client._handle_messages(
        [
            ParsedMessage(
                type=MessageType.CHANNEL_MESSAGE,
                channel_message=ChannelMessage(
                    source=get_user(), message="Hello!", channel="#testers"
                ),
            )
        ]
    )

    script.on_channel_message.assert_called_once()


def test_client_calls_script_on_join() -> None:
    script, client = get_script_and_client()
    client._handle_messages(
        [
            ParsedMessage(
                type=MessageType.JOIN,
                join_message=JoinMessage(user=get_user(), channel="#testers"),
            )
        ]
    )

    script.on_join.assert_called_once()


def test_client_calls_script_on_part() -> None:
    script, client = get_script_and_client()
    client._handle_messages(
        [
            ParsedMessage(
                type=MessageType.USERS,
                users_message=UsersMessage(
                    channel="#testers", users=["tester"]
                ),
            ),
            ParsedMessage(
                type=MessageType.END_OF_USERS,
                users_end_message=UsersEndMessage(channel="#testers"),
            ),
            ParsedMessage(
                type=MessageType.PART,
                part_message=PartMessage(user=get_user(), channel="#testers"),
            ),
        ]
    )

    script.on_part.assert_called_once()


def test_client_calls_script_on_quit() -> None:
    script, client = get_script_and_client()
    client._handle_messages(
        [
            ParsedMessage(
                type=MessageType.USERS,
                users_message=UsersMessage(
                    channel="#testers", users=["tester"]
                ),
            ),
            ParsedMessage(
                type=MessageType.END_OF_USERS,
                users_end_message=UsersEndMessage(channel="#testers"),
            ),
            ParsedMessage(
                type=MessageType.QUIT,
                quit_message=QuitMessage(user=get_user(), message="leaving"),
            ),
        ]
    )

    script.on_quit.assert_called_once()


def test_client_calls_script_on_connect() -> None:
    script, client = get_script_and_client()
    client._handle_messages(
        [
            ParsedMessage(
                type=MessageType.END_OF_MOTD,
                end_of_motd_message=EndOfMotdMessage(message="welcome"),
            )
        ]
    )

    script.on_connect.assert_called_once()


def test_client_calls_script_on_kill() -> None:
    script, client = get_script_and_client()
    client.kill()

    script.kill.assert_called_once()


def test_client_calls_script_on_topic() -> None:
    script, client = get_script_and_client()
    client._handle_messages(
        [
            ParsedMessage(
                type=MessageType.TOPIC,
                topic_message=TopicMessage(
                    user=get_user(), channel="#testers", topic="welcome"
                ),
            )
        ]
    )

    script.on_topic.assert_called_once()


def test_client_calls_script_on_topic_reply() -> None:
    script, client = get_script_and_client()
    client._handle_messages(
        [
            ParsedMessage(
                type=MessageType.TOPIC_REPLY,
                topic_reply_message=TopicReplyMessage(
                    nick=get_user().nick, channel="#testers", topic="welcome"
                ),
            )
        ]
    )

    script.on_topic.assert_called_once()
