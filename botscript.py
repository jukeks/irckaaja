import time

class BotScript:
	'''
	"Abstract" script class. Should be inherited by script classes.
	See HelloWorld in scripts.helloworld.py for example.
	'''
	def __init__(self, server_connection, config):
		self.server_connection = server_connection
		self.config = config
		self.alive = True
		
		# usage: self.PRIVMSG(target, message)
		self.PRIVMSG = server_connection.PRIVMSG
		
		# usage: self.JOIN(channelname)
		self.JOIN = server_connection.JOIN
		
		#usage: self.PART(channelname, reason = "")
		self.PART = server_connection.PART
	
	
	def sleep(self, seconds):
		'''
		Sleeps for seconds unless not self.alive.
		'''
		start = time.time()
		while time.time() < start + seconds and self.alive:
			time.sleep(1)
	
	def kill(self):
		self.alive = False
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
