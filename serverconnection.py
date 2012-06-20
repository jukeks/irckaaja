import socket
import time
from threading import Thread
from messageparser import MessageParser
from channel import IrcChannel
from dynamicmodule import DynamicModule

# Source: http://blog.initprogram.com/2010/10/14/a-quick-basic-primer-on-the-irc-protocol/


class ServerConnection:
	'''
	Class handling irc servers.
	'''
	#def __init__(self, hostname, port, nick, altnick, username, realname, owner, channels = None, server_alias = ""):
	def __init__(self, networkname, serverd, botd, joinlist, modulenames):
		self.alive = True
		self.connected = False
		self.hostname = serverd['hostname']
		self.port = int(serverd.get('port', "6667"))
		self.nick = botd['nick']
		self.altnick = botd.get('altnick', self.nick + "_")
		self.username = botd['username']
		self.realname = botd['realname']
		self.owner = botd['owner']
		print self.owner
		self.networkname = networkname
		
		self.joinlist = joinlist
		
		self.readerThread = None
		self.parser = MessageParser(self)
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		self.channelList = []
		
		self.dynamicmodules = [DynamicModule(self, m) for m in modulenames]
		
		
	def connect(self):
		'''
		Tries to connect to irc server.
		'''
		while self.alive:
			try:
				self.socket.connect((self.hostname, self.port))
				
				self.NICK(self.nick)
				self.USER(self.username, self.realname)
				
				if not self.readerThread:
					self.readerThread = Thread(target=self.read)
					self.readerThread.start()
				else:
					self.read()
				break
			except Exception as e:
				self.printLine(str(e) + " " + self.hostname)
				self.printLine("Trying again in 30 seconds.")
				self.sleep(30)
	
	def connectAgain(self):
		'''
		Initialises self.socket and tries reconnecting
		in 60 seconds.
		'''
		self.socket.close()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.printLine("Trying again in 60 seconds.")
		self.sleep(60)
		self.connect()
	
	def write(self, message):
		'''
		Prints and writes message to server.
		'''
		self.printLine(message[:-1])
		self.socket.send(message)

	def read(self):
		'''
		Reads and handles messages.
		'''
		self.socket.settimeout(1.0)
		buff = ""
		while self.alive:
			try:
				tmp = self.socket.recv(1024)
			except socket.timeout as e:
				continue
			except socket.error as e:
				self.printLine(str(e))
				self.connectAgain()
				return
			except KeyboardInterrupt:
				self.kill()
				
			if not self.alive:
				break
			
			if not tmp:
				self.printLine("Connection closed.")
				self.connectAgain()
				return

			buff += tmp
			buff = self.checkForMessagesAndReturnRemaining(buff)
			
		self.socket.close()
			
			
	def checkForMessagesAndReturnRemaining(self, buff):
		'''
		Checks if buff contains any messages. If so, it parses and
		handles them and returns the remaining bytes.
		'''
		while buff.find("\r\n") != -1:
			head, _, buff = buff.partition("\r\n")
			self.parser.parse(head)
		
		return buff

	def printLine(self, message):
		'''
		Prints message with timestamp.
		'''
		print time.strftime("%H:%M:%S") + " |" + self.networkname + "| "  + message

	def NICK(self, nick):
		'''
		Sets user's nick on server.
		'''
		self.write("NICK " + nick + "\r\n")
	
	def USER(self, username, realname):
		'''
		Sets username and realname to server on connect.
		'''
		self.write("USER " + username  +" 0 * :" + realname + "\r\n")
	
	def PONG(self, message):
		'''
		Reply to PING.
		'''
		self.write("PONG :" + message + "\r\n")
	
	def JOIN(self, channel):
		'''
		Joins a irc channel.
		'''
		self.write("JOIN :" +channel + "\r\n")
	
	def PART(self, channel, reason = ""):
		'''
		PARTs from a channel.
		'''
		msg = "PART " + channel
		if reason:
			msg += " :" + reason
		self.write(msg + "\r\n")
	
	def PRIVMSG(self, target, message):
		'''
		Sends PRIVMSG to target.
		'''
		self.write("PRIVMSG " + target + " :" + message + "\r\n")

	def PING(self, message):
		'''
		Sends PING to server.
		'''
		self.write("PING " + message + "\r\n")

	def onConnect(self):
		'''
		Called when connected to the network.
		'''
		self.PING(self.hostname)
		self.joinChannels()
		
		for dm in self.dynamicmodules:
			try:
				dm.instance.onConnect()
			except:
				pass
		
	def joinChannels(self):
		'''
		Joins channels specified in self.joinlist
		'''
		for channel in self.joinlist:
			self.JOIN(channel)

	def kill(self):
		'''
		Called when the thread is wanted dead.
		'''
		self.printLine(self.networkname + " dying.")
		self.alive = False
		
	def privateMessageReceived(self, source, message, fullmask):
		'''
		Called when a private message has been received. Prints it
		and calls onPrivateMessage() on DynamicModule instances.
		'''
		self.printLine("PRIVATE" + " <" + source + "> " + message)
		
		for dm in self.dynamicmodules:
			try:
				dm.instance.onPrivateMessage(source, message, fullmask)
			except:
				pass	
	
	def channelMessageReceived(self, source, channel, message, fullmask):
		'''
		Called when a PRIVMSG to a channel has been received. Prints it
		and calls onChannelMessage() on DynamicModule instances.
		'''
		self.printLine(channel + " <" + source + "> " + message)
		
		for dm in self.dynamicmodules:
			try:
				dm.instance.onChannelMessage(source, channel, message, fullmask)
			except:
				pass
	
	def pingReceived(self, message):
		'''
		Called when PING message has been received.
		'''
		self.PONG(message)
	
	def motdReceived(self, message):
		'''
		Called when the end of MOTD message
		has been received.
		'''
		self.printLine(message)
		if not self.connected:
			self.connected = True
			self.onConnect()
	
	def findChannelByName(self, channelname):
		'''
		Returns a channel instance from channellist
		matching channelname parameter or None.
		'''
		for channel in self.channelList:
			if channel.name == channelname:
				return channel
	
	def addChannel(self, name, userlist):
		'''
		Adds a channel to networks channel list.
		'''
		if self.findChannelByName(name):
			return
		
		channel = IrcChannel(name, userlist)
		self.channelList.append(channel)	 
	
	def usersReceived(self, channelname, userlist):
		'''
		Called when USERS message is received. Notifies 
		channel instance of the users.
		'''
		channel = self.findChannelByName(channelname)
		if not channel:
			self.addChannel(channelname, userlist)
			return
		
		channel.usersMessage(userlist)
	
	def usersEndReceived(self, channelname):
		'''
		Called when USERS message's end has been received.
		Notifies the channel instance.
		'''
		channel = self.findChannelByName(channelname)
		channel.usersMessageEnd()
		self.printLine("USERS OF " + channelname)
		self.printLine(" ".join(channel.userlist))
		
	def quitReceived(self, nick, fullmask):
		'''
		Called when a QUIT message has been received. Calls
		onQuit() on DynamicModules
		'''
		for channel in self.channelList:
			channel.removeUser(nick)
			
		self.printLine(nick + " has quit.")
		
		for dm in self.dynamicmodules:
			try:
				dm.instance.onQuit(nick, fullmask)
			except:
				pass
	
	def partReceived(self, nick, channelname, fullmask):
		'''
		Called when a PART message has been received. Calls
		onPart() on DynamicModules
		'''
		channel = self.findChannelByName(channelname)
		if not channel: return
		
		channel.removeUser(nick)
		
		self.printLine(nick + " has part " + channelname)
		
		for dm in self.dynamicmodules:
			try:
				dm.instance.onPart(nick, channelname, fullmask)
			except:
				pass
	
	def joinReceived(self, nick, channelname, fullmask):
		'''
		Called when a JOIN message has been received. Calls
		onJoin() on DynamicModules
		'''
		channel = self.findChannelByName(channelname)
		if not channel: return
		
		channel.addUser(nick)
		
		self.printLine(nick + " has joined " + channelname)
		for dm in self.dynamicmodules:
			try:
				dm.instance.onJoin(nick, channelname, fullmask)
			except:
				pass
	
	def unknownMessageReceived(self, message):
		self.printLine(message)

	def sleep(self, seconds):
		'''
		Sleeps for seconds unless not self.alive.
		'''
		start = time.time()
		while time.time() < start + seconds and self.alive:
			time.sleep(1)
