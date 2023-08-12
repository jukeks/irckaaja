from irckaaja.botscript import BotScript
from irckaaja.dynamicmodule import DynamicModule


class ModuleLoader(BotScript):
    """
    A helper script for loading, reloading and unloading
    modules dynamically on runtime. Makes developing scripts
    much easier as the bot need to reconnect to irc network
    between changes.
    """

    def on_private_message(self, source, message, full_mask):
        # authenticating
        if full_mask != self.server_connection.owner:
            return

        # checking if we got a relevant message
        try:
            if self._try_load(source, message):
                return
            if self._try_reload(source, message):
                return
            if self._try_unload(source, message):
                return

        except Exception as e:
            self.say(source, "error: " + str(e))

    def _try_load(self, source, message):
        if not message.startswith("!load"):
            return False

        module_name = message.replace("!load ", "")

        # Not loading if it's already loaded
        for dm in self.server_connection.dynamic_modules:
            if dm.module_name == module_name:
                self.say(source, "module " + str(dm.classvar) + " already loaded")
                return True

        # Loading and appending to the list
        dm = DynamicModule(
            self.server_connection,
            module_name,
            self.server_connection.modules_config[module_name],
        )
        self.server_connection.dynamic_modules.append(dm)

        self.say(source, "loaded " + str(dm.classvar))
        return True

    def _try_reload(self, source, message):
        if not message.startswith("!reload"):
            return False

        module_name = message.replace("!reload ", "")

        # finding the module to reload
        for dm in self.server_connection.dynamic_modules:
            if dm.module_name != module_name:
                continue

            dm.reload_module()
            self.say(source, "reloaded " + str(dm.classvar))
            return True

        # didn't find it
        self.say(source, "unable to find module with name " + module_name)
        return True

    def _try_unload(self, source, message):
        if not message.startswith("!unload"):
            return False

        module_name = message.replace("!unload ", "")

        # finding the module in the list by name
        for dm in self.server_connection.dynamic_modules:
            if dm.module_name != module_name:
                continue

            # unloading
            self.server_connection.dynamic_modules.remove(dm)
            self.say(source, "unloaded  " + str(dm.classvar))
            del dm
            return True

        # module was not found
        self.say(source, "unable to find module with name " + module_name)
        return True
