class DynamicModule:
    """
    This class holds Python scripts.
    """

    def __init__(self, server_connection, modulename, config=None):
        """
        Initialises and calls load().

        server_connection: connection to the network in which the module is related
        modulename: name of the module
        classvar: script class
        instance: instance of classvar
        """
        self.server_connection = server_connection
        self.module_name = modulename
        self.module = None
        self.classvar = None
        self.instance = None
        self.module_config = config
        self.load()

    def reload_module(self):
        """
        Reloads the module, the class and overwrites the instance.
        """
        self.instance.kill()
        reload(self.module)
        self.classvar = getattr(self.module, self.module_name)
        self.instance = self.classvar(self.server_connection, self.module_config)

    def load(self):
        """
        Tries to load a class in a module in the scripts folder.
        Module should be named <ClassName>.lower().
        """
        self.module = __import__(
            "scripts." + self.module_name.lower(),
            globals(),
            locals(),
            [self.module_name],
            -1,
        )
        self.classvar = getattr(self.module, self.module_name)
        self.instance = self.classvar(self.server_connection, self.module_config)
