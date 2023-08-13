from dataclasses import dataclass
from typing import Any, Dict, List

from configobj import ConfigObj

CONFIG_FILENAME = "config.ini"


@dataclass
class ServerConfig:
    name: str
    hostname: str
    port: int
    channels: list[str]


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
            channels_raw = server["channels"]
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

    def modules(self) -> Dict[str, Any]:
        """
        Returns a dictionary of  modules defined in the
        conf to be loaded.
        """
        return self.config["modules"]

    def channels(self, servername: str) -> List[str]:
        """
        Returns a list of channels to be joined
        on a network (server).
        """
        return self.config["servers"][servername].get("channels", [])

    def bot(self) -> Dict[str, Any]:
        """
        Returns bot dictionary.
        """
        return self.config["bot"]
