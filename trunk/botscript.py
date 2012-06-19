
class BotScript:
	def __init__(self, server_connection):
		self.server_connection = server_connection
		self.PRIVMSG = server_connection.PRIVMSG
		self.JOIN = server_connection.JOIN
		self.PART = server_connection.PART

	def onChannelMessage(self, nick, target, message, fullmask):
		pass
	
	def onPrivateMessage(self, nick, message, fullmask):
		pass
	
	def onJoin(self, nick, channelname, fullmask):
		pass
	
	def onPart(self, nick, channelname, fullmask):
		pass
	
	def onQuit(self, nick, fullmask):
		pass
	
	def onConnect(self):
		pass