

class IrcChannel:
	'''
	Channel datastructure. Keeps track of users.
	'''
	def __init__(self, name, userlist):
		self.name = name
		self.userlist = userlist
		self.userlist_complete = True
		self.topic = ""
		
	def usersMessage(self, userlist):
		'''
		Usually received on join. Count of these
		messages depend on user count on the channel.
		'''
		if self.userlist_complete:
			self.userlist = userlist
			self.userlist_complete = False
		else:
			self.userlist += userlist
			
	def usersMessageEnd(self):
		'''
		When received, states that all users on channel
		have been listed and userlist is therefore complete.
		'''
		self.userlist_complete = True
		
	def removeUser(self, nick):
		'''
		Tries to remove a user from the channel.
		'''
		try:
			self.userlist.remove(nick)
		except ValueError:
			pass
	
	def addUser(self, nick):
		'''
		Adds user to channel if not already added.
		'''
		if not nick in self.userlist:
			self.userlist.append(nick)


		
	