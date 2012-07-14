__author__ = 'juke'
# -*- coding: utf-8 -*-


from botscript import BotScript
import shove
import re
import time

class IrcLinkHistory(BotScript):
	def __init__(self, server_connection, config):
		BotScript.__init__(self, server_connection, config)

		self.store_path = config['store_path']

		self.channels = [config['channels']] if isinstance(config['channels'], "".__class__) else config['channels']
		self.dbs = {}
		for channel in self.channels:
			self.dbs[channel] = shove.Shove("bsddb://" + self.store_path + "/" + channel + ".db")


	def _getDiffString(self, t1, t2):
		diff = t1 - t2

		if diff < 60:
			return "%d sekuntia" %diff
		elif diff < 60*60:
			return "%d minuuttia" %(diff/60)
		elif diff < 60*60*24:
			return "%.2f tuntia" %(diff/float(60*60))
		else:
			return "%d päivää" %(diff/60*60*24)

	def onChannelMessage(self, nick, channel_name, message, full_mask):
		urls = re.findall(r'(https?://\S+)', message)

		if not urls:
			return
		try:
			db = self.dbs[channel_name]
		except KeyError:
			return

		for url in urls:
			timestamp = db.get(url)
			if not timestamp:
				db[url] = time.time()
			else:
				self.say(channel_name, "wanha! jo " + self._getDiffString(time.time(), timestamp))
