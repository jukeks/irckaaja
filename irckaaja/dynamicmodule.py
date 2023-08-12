import importlib
from typing import TYPE_CHECKING, Any

from irckaaja.botscript import BotScript

if TYPE_CHECKING:
    from irckaaja.serverconnection import ServerConnection


class DynamicModule:
    """
    This class holds Python scripts.
    """

    def __init__(
        self,
        server_connection: "ServerConnection",
        module_name: str,
        config: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialises and tries to load a class in a module in the scripts folder.
        Module should be named <ClassName>.lower().

        server_connection: connection to the network in which the module is
        related
        modulename: name of the module
        classvar: script class
        instance: instance of classvar
        """
        self.server_connection = server_connection
        self.module_name = module_name
        self.module_config = config

        self.module = __import__(
            "irckaaja.scripts." + self.module_name.lower(),
            None,
            None,
            [self.module_name],
            0,
        )

        self.classvar = getattr(self.module, self.module_name)
        self.instance: BotScript = self.classvar(
            self.server_connection, self.module_config
        )

    def reload_module(self) -> None:
        """
        Reloads the module, the class and overwrites the instance.
        """
        if self.instance:
            self.instance.kill()
        importlib.reload(self.module)
        self.classvar = getattr(self.module, self.module_name)
        self.instance = self.classvar(
            self.server_connection, self.module_config
        )
