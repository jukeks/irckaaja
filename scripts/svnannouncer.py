import pysvn
import threading
import time

from botscript import BotScript

class SVNAnnouncer(BotScript, threading.Thread):
	def __init__(self, server_connection, config):
		BotScript.__init__(self, server_connection, config)
		threading.Thread.__init__(self)
		
		self.repository_path = self.config['repository_path']
		self.targets = self.config['targets']
		if not isinstance(self.targets, [].__class__):
			self.targets = [self.targets]
		
		self.svnclient = pysvn.Client()
		self.last_entry = self.svnclient.log(self.repository_path, limit = 1)[0]
		self.last_entry_time = self.last_entry.date
		
		self.start()
		
		
	def run(self):
		while self.alive:
			self.last_entry = self.svnclient.log(self.repository_path, limit = 1)[0]
			if self.last_entry.date != self.last_entry_time:
				self.last_entry_time = self.last_entry.date
				message = self.last_entry.author +" commited a change: " + self.last_entry.message
				for target in self.targets:
					self.PRIVMSG(target, message)
			
			BotScript.sleep(self, 60)