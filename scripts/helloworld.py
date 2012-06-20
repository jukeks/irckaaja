from botscript import BotScript

class HelloWorld(BotScript):
	'''
	A simple script class. Only responds to messages starting "moi"
	in every channel in a network.
	'''
	def onChannelMessage(self, nick, channelname, message, fullmask):
		if message.startswith("moi"):
			self.PRIVMSG(channelname, "mutsis sano moi, " + nick)
			return