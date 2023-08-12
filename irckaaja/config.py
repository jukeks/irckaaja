from configobj import ConfigObj

CONFIGFILENAME = "config.ini"


class Config:
    """
    Wrapper for config.ini
    """

    def __init__(self, configfilename=CONFIGFILENAME):
        self.filename = configfilename
        self.config = ConfigObj(self.filename, list_values=True, encoding="utf-8")

    def servers(self):
        """
        Returns servers as a dictionary.
        """
        return self.config["servers"]

    def modules(self):
        """
        Returns a dictionary of  modules defined in the
        conf to be loaded.
        """
        return self.config["modules"]

    def channels(self, servername):
        """
        Returns a list of channels to be joined
        on a network (server).
        """
        return self.config["servers"][servername].get("channels", [])

    def bot(self):
        """
        Returns bot dictionary.
        """
        return self.config["bot"]
