from configobj import ConfigObj

CONFIGFILENAME = "config.ini"

class Config:
	def __init__(self, configfilename = CONFIGFILENAME):
		self.filename = configfilename
		self.config = ConfigObj(self.filename, list_values=True)
	
	def servers(self):
		return self.config['servers']
	
	def modules(self):
		return self.bot()['modules']
	
	def channels(self, servername):
		return self.config['servers'][servername].get('channels', [])
	
	def bot(self):
		return self.config['bot']
	