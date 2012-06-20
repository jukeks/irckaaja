import sys

class DynamicModule:
	'''
	This class holds Python scripts. 
	'''
	def __init__(self, server_connection, modulename):
		'''
		Initialises and calls load().
		
		server_connection: connection to the network in which the module is related
		modulename: name of the module
		classvar: script class
		instance: instance of classvar
		'''
		self.server_connection = server_connection
		self.modulename = modulename
		self.module = None
		self.classvar = None
		self.instance = None
		
		self.load()
		
	def reloadModule(self):
		'''
		Reloads the module, the class and overwrites the instance.
		'''
		reload(self.module)
		self.classvar = getattr(self.module, self.modulename)
		self.instance = self.classvar(self.server_connection)

	
	def load(self):
		'''
		Tries to load a class in a module in the scripts folder.
		Module should be named <ClassName>.lower().
		'''
		self.module = __import__('scripts.' + self.modulename.lower(), globals(), 
								locals(), [self.modulename], -1)
		self.classvar = getattr(self.module, self.modulename)
		self.instance = self.classvar(self.server_connection)
