import sys

class DynamicModule:
	def __init__(self, server_connection, modulename):
		self.server_connection = server_connection
		self.modulename = modulename
		self.module = None
		self.classvar = None
		self.instance = None
		
		self.load()
		
	def reloadModule(self):
		reload(self.module)
		self.classvar = getattr(self.module, self.modulename)
		self.instance = self.classvar(self.server_connection)

	
	def load(self):
		self.module = __import__('scripts.' + self.modulename.lower(), globals(), 
								locals(), [self.modulename], -1)
		self.classvar = getattr(self.module, self.modulename)
		self.instance = self.classvar(self.server_connection)