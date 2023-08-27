from unittest.mock import Mock

from irckaaja.client import IrcClient
from irckaaja.dynamicmodule import DynamicModule


def test_new_instance_is_created() -> None:
    client = Mock(spec=IrcClient)
    dm = DynamicModule(config={}, connection=client, module_name="HelloWorld")
    setattr(dm.instance, "new_var", 1)
    dm.reload_module()
    assert getattr(dm.instance, "new_var", None) is None
