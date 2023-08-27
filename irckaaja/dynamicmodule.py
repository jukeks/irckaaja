import importlib
from typing import TYPE_CHECKING, Any, Dict, Optional

from irckaaja.botscript import BotScript

if TYPE_CHECKING:
    from irckaaja.client import IrcClient  # pragma: no cover


class DynamicModule:
    """
    Container for reloadable scripts.
    """

    def __init__(
        self,
        connection: "IrcClient",
        module_name: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialises and tries to load a class in a module in the scripts folder.
        Module should be named <ClassName>.lower().

        connection: connection to the network in which the module is
        related
        modulename: name of the module
        classvar: script class
        instance: instance of classvar
        """
        self.connection = connection
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
            self.connection, self.module_config
        )

    def reload_module(self) -> None:
        """
        Reloads the module, the class and overwrites the instance.
        """
        self.instance.kill()
        importlib.reload(self.module)
        self.classvar = getattr(self.module, self.module_name)
        self.instance = self.classvar(self.connection, self.module_config)
