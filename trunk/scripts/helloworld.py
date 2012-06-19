from botscript import BotScript

class HelloWorld(BotScript):
	def onChannelMessage(self, nick, channelname, message, fullmask):
		if message.startswith("moi"):
			self.PRIVMSG(channelname, "mutsis sano moi, " + nick)
			return