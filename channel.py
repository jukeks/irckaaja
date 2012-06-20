

class IrcChannel:
	def __init__(self, name, userlist):
		self.name = name
		self.userlist = userlist
		self.userlist_complete = True
		
	def usersMessage(self, userlist):
		if self.userlist_complete:
			self.userlist = userlist
			self.userlist_complete = False
		else:
			self.userlist += userlist
			
	def usersMessageEnd(self):
		self.userlist_complete = True
		
	def removeUser(self, name):
		try:
			self.userlist.remove(name)
		except ValueError:
			pass
	
	def addUser(self, name):
		if not name in self.userlist:
			self.userlist.append(name)


		
	