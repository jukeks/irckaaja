from botscript import BotScript
from dynamicmodule import DynamicModule

class ModuleLoader(BotScript):
	def onPrivateMessage(self, source, message, fullmask):
		sc = self.server_connection		
		if fullmask != sc.owner:
			return
		
		try:
			if message.startswith("!load"):
				modulename = message.replace("!load ", "")
				for dm in sc.dynamicmodules:
					if dm.modulename == modulename:
						self.PRIVMSG(source, "module " + str(dm.classvar) + " already loaded")
						return
				
				dm = DynamicModule(sc, modulename)
				sc.dynamicmodules.append(dm)
				
				self.PRIVMSG(source, "loaded " + str(dm.classvar))
				return
				
			if message.startswith("!reload"):
				modulename = message.replace("!reload ", "")
				
				for dm in sc.dynamicmodules:
					if dm.modulename != modulename:
						continue
					
					dm.reloadModule()
					self.PRIVMSG(source, "reloaded " + str(dm.classvar))
					return
				
				self.PRIVMSG(source, "unable to find module with name " + modulename)
				return
					
			if message.startswith("!unload"):
				modulename = message.replace("!unload ", "")
				for dm in sc.dynamicmodules:
					if dm.modulename != modulename:
						continue
					
					sc.dynamicmodules.remove(dm)
					self.PRIVMSG(source, "unloaded  " + str(dm.classvar))
					del dm
					return
				
				self.PRIVMSG(source, "unable to find module with name " + modulename)
		except Exception as e:
			self.PRIVMSG(source, "error: " + str(e))
			