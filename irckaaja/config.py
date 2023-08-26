from dataclasses import dataclass
from typing import Any, Dict

from configobj import ConfigObj

CONFIG_FILENAME = "config.ini"


@dataclass
class ServerConfig:
    name: str
    hostname: str
    port: int
    channels: list[str]


@dataclass
class BotConfig:
    nick: str
    altnick: str
    realname: str
    username: str
    owner: str


@dataclass
class ScriptConfig:
    module_name: str
    config: Dict[str, Any]


class Config:
    """
    Wrapper for config.ini
    """

    def __init__(self, config_filename: str = CONFIG_FILENAME) -> None:
        self.filename = config_filename
        self.config = ConfigObj(
            self.filename, list_values=True, encoding="utf-8"
        )

    def servers(self) -> Dict[str, ServerConfig]:
        """
        Returns servers as a dictionary.
        """
        config = {}
        for alias, server in self.config["servers"].items():
            channels_raw = server.get("channels", [])
            if isinstance(channels_raw, str):
                channels = [channels_raw]
            else:
                channels = channels_raw

            config[alias] = ServerConfig(
                name=alias,
                hostname=server["hostname"],
                port=int(server.get("port", "6667")),
                channels=channels,
            )
        return config

    def modules(self) -> Dict[str, ScriptConfig]:
        """
        Returns a dictionary of modules defined in the
        conf to be loaded.
        """
        modules = {}
        for name, config in self.config["modules"].items():
            modules[name] = ScriptConfig(module_name=name, config=config)
        return modules

    def bot(self) -> BotConfig:
        """
        Returns bot dictionary.
        """
        config = self.config["bot"]
        return BotConfig(
            nick=config["nick"],
            altnick=config.get("altnick", config["nick"] + "_"),
            realname=config["realname"],
            username=config["username"],
            owner=config["owner"],
        )
