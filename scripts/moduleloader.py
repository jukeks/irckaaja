from botscript import BotScript
from dynamicmodule import DynamicModule

class ModuleLoader(BotScript):
	'''
	A helper script for loading, reloading and unloading
	modules dynamically on runtime. Makes developing scripts
	much easier as the bot need to reconnect to irc network
	between changes. 
	'''
	def onPrivateMessage(self, source, message, fullmask):
		# authenticating
		if fullmask != self.server_connection.owner:
			return
		
		# checking if we got a relevant message
		try:
			if self.tryLoad(source, message): return
				
			if self.tryReload(source, message): return
					
			if self.tryUnload(source, message): return
		except Exception as e:
			self.PRIVMSG(source, "error: " + str(e))


	def tryLoad(self, source, message):
		if not message.startswith("!load"):
			return False
			
		modulename = message.replace("!load ", "")
		
		# Not loading if it's already loaded
		for dm in self.server_connection.dynamicmodules:
			if dm.modulename == modulename:
				self.PRIVMSG(source, "module " + str(dm.classvar) + " already loaded")
				return True
		
		# Loading and appending to the list
		dm = DynamicModule(self.server_connection, modulename)
		self.server_connection.dynamicmodules.append(dm)
			
		self.PRIVMSG(source, "loaded " + str(dm.classvar))
		return True	


	def tryReload(self, source, message):
		if not message.startswith("!reload"):
			return False
		
		modulename = message.replace("!reload ", "")
		
		# finding the module to reload
		for dm in self.server_connection.dynamicmodules:
			if dm.modulename != modulename:
				continue
			
			dm.reloadModule()
			self.PRIVMSG(source, "reloaded " + str(dm.classvar))
			return True
		
		
		# didn't find it
		self.PRIVMSG(source, "unable to find module with name " + modulename)
		return True
	
	
	def tryUnload(self, source, message):
		if not message.startswith("!unload"):
			return False
		
		modulename = message.replace("!unload ", "")
		
		# finding the module in the list by name
		for dm in self.server_connection.dynamicmodules:
			if dm.modulename != modulename:
				continue
			
			# unloading
			self.server_connection.dynamicmodules.remove(dm)
			self.PRIVMSG(source, "unloaded  " + str(dm.classvar))
			del dm
			return True
			
		# module was not found
		self.PRIVMSG(source, "unable to find module with name " + modulename)
		return True
	
