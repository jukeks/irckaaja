import pathlib

from irckaaja.config import BotConfig, Config, ScriptConfig, ServerConfig


def test_bot_config(tmp_path: pathlib.Path) -> None:
    conf = """
[bot]
    nick = irckaaja
    altnick = irckaaja_
    realname = Bot Real Name
    username = irckaaja
    owner = "nick!user@example.com"
    """

    p = tmp_path / "config.ini"
    p.write_text(conf)

    c = Config(config_filename=str(p))
    bot_config = c.bot()
    assert bot_config == BotConfig(
        nick="irckaaja",
        altnick="irckaaja_",
        realname="Bot Real Name",
        username="irckaaja",
        owner="nick!user@example.com",
    )


def test_server_config(tmp_path: pathlib.Path) -> None:
    conf = """
[servers]
    [[Server1]]
        hostname = hostname1
        port = 6667
        channels = "#testers"
    [[Server2]]
        hostname = hostname2
    """

    p = tmp_path / "config.ini"
    p.write_text(conf)

    c = Config(config_filename=str(p))
    servers = c.servers()
    s1 = servers["Server1"]
    assert s1 == ServerConfig(
        name="Server1",
        hostname="hostname1",
        port=6667,
        channels=["#testers"],
    )
    s2 = servers["Server2"]
    assert s2 == ServerConfig(
        name="Server2",
        hostname="hostname2",
        port=6667,
        channels=[],
    )


def test_script_config(tmp_path: pathlib.Path) -> None:
    conf = """
[modules]
    [[HelloWorld]]
        arbitrary = data
    """

    p = tmp_path / "config.ini"
    p.write_text(conf)

    c = Config(config_filename=str(p))
    modules = c.modules()
    hw = modules["HelloWorld"]
    assert hw == ScriptConfig(
        module_name="HelloWorld", config={"arbitrary": "data"}
    )
