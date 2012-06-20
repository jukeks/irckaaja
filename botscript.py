
class BotScript:
	def __init__(self, server_connection):
		self.server_connection = server_connection
		
		# usage: self.PRIVMSG(target, message)
		self.PRIVMSG = server_connection.PRIVMSG
		
		# usage: self.JOIN(channelname)
		self.JOIN = server_connection.JOIN
		
		#usage: self.PART(channelname)
		self.PART = server_connection.PART
	
	
	# Methods below can be implemented in your script class if you like.
	# That way you can subscribe to those messages.
	def onChannelMessage(self, nick, target, message, fullmask):
		'''
		Is called when a channel message is received.
		'''
		pass
	
	def onPrivateMessage(self, nick, message, fullmask):
		'''
		Is called when a private message is received.
		'''
		pass
	
	def onJoin(self, nick, channelname, fullmask):
		'''
		Is called when a user joins a channel.
		'''
		pass
	
	def onPart(self, nick, channelname, fullmask):
		'''
		Is called when a user parts a channel.
		'''
		pass
	
	def onQuit(self, nick, fullmask):
		'''
		Is called when a user quits the network.
		'''
		pass
	
	def onConnect(self):
		'''
		Is called when bot has connected to the network.
		'''
		pass