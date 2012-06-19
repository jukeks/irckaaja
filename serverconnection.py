import socket
import time
from threading import Thread
from messageparser import MessageParser
from channel import IrcChannel

# Source: http://blog.initprogram.com/2010/10/14/a-quick-basic-primer-on-the-irc-protocol/


class ServerConnection:
	def __init__(self, hostname, port, nick, altnick, username, realname, owner, channels = None, server_alias = ""):
		self.alive = True
		self.connected = False
		self.hostname = hostname
		self.port = int(port)
		self.nick = nick
		self.altnick = altnick
		self.username = username
		self.realname = realname
		self.owner = owner
		print self.owner
		self.alias = server_alias if server_alias else hostname
		self.joinList = [] if not channels else channels
		
		self.readerThread = None
		self.parser = MessageParser(self)
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		self.channelList = []
		
		self.dynamicmodules = []
		
		
	def connect(self):
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
		self.socket.close()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.printLine("Trying again in 60 seconds.")
		self.sleep(60)
		self.connect()
	
	def write(self, message):
		self.printLine(message[:-1])
		self.socket.send(message)

	def read(self):
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
		while buff.find("\r\n") != -1:
			head, _, buff = buff.partition("\r\n")
			self.parser.parse(head)
		
		return buff

	def printLine(self, message):
		print time.strftime("%H:%M:%S") + " |" + self.alias + "| "  + message

	def NICK(self, nick):
		self.write("NICK " + nick + "\r\n")
	
	def USER(self, username, realname):
		self.write("USER " + username  +" 0 * :" + realname + "\r\n")
	
	def PONG(self, message):
		self.write("PONG :" + message + "\r\n")
	
	def JOIN(self, channel):
		self.write("JOIN :" +channel + "\r\n")
	
	def PART(self, channel, reason = ""):
		msg = "PART " + channel
		if reason:
			msg += " :" + reason
		self.write(msg + "\r\n")
	
	def PRIVMSG(self, target, message):
		self.write("PRIVMSG " + target + " :" + message + "\r\n")

	def PING(self, message):
		self.write("PING " + message + "\r\n")

	def onConnect(self):
		self.PING(self.hostname)
		self.joinChannels()
		
		for dm in self.dynamicmodules:
			try:
				dm.instance.onConnect()
			except:
				pass
		
	def joinChannels(self):
		for channel in self.joinList:
			self.JOIN(channel)
	
	def onPrivateMessage(self, source, message, fullmask):
		for dm in self.dynamicmodules:
			try:
				dm.instance.onPrivateMessage(source, message, fullmask)
			except:
				pass	
		
		
	def onChannelMessage(self, source, channel, message, fullmask):
		for dm in self.dynamicmodules:
			try:
				dm.instance.onChannelMessage(source, channel, message, fullmask)
			except:
				pass

	def kill(self):
		self.printLine(self.alias + " dying.")
		self.alive = False
		
	def privateMessageReceived(self, source, message, fullmask):
		self.printLine("PRIVATE" + " <" + source + "> " + message)
		self.onPrivateMessage(source, message, fullmask)
	
	def channelMessageReceived(self, source, channel, message, fullmask):
		self.printLine(channel + " <" + source + "> " + message)
		self.onChannelMessage(source, channel, message, fullmask)
	
	def pingReceived(self, message):
		self.PONG(message)
	
	def motdReceived(self, message):
		self.printLine(message)
		if not self.connected:
			self.connected = True
			self.onConnect()
	
	def findChannelByName(self, channelname):
		for channel in self.channelList:
			if channel.name == channelname:
				return channel
	
	def addChannel(self, name, userlist):
		if self.findChannelByName(name):
			return
		
		channel = IrcChannel(name, userlist)
		self.channelList.append(channel)	 
	
	def usersReceived(self, channelname, userlist):
		channel = self.findChannelByName(channelname)
		if not channel:
			self.addChannel(channelname, userlist)
			return
		
		channel.usersMessage(userlist)
	
	def usersEndReceived(self, channelname):
		channel = self.findChannelByName(channelname)
		channel.usersMessageEnd()
		self.printLine("USERS OF " + channelname)
		self.printLine(" ".join(channel.userlist))
		
	def quitReceived(self, nick, fullmask):
		for channel in self.channelList:
			channel.removeUser(nick)
			
		self.printLine(nick + " has quit.")
		
		for dm in self.dynamicmodules:
			try:
				dm.instance.onQuit(nick, fullmask)
			except:
				pass
	
	def partReceived(self, nick, channelname, fullmask):
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
		channel = self.findChannelByName(channelname)
		if not channel: return
		
		channel.addUser(nick)
		
		self.printLine(nick + " has joined " + channelname)
		for dm in self.dynamicmodules:
			try:
				dm.instance.onPrivateMessage(nick, channelname, fullmask)
			except:
				pass
	
	def unknownMessageReceived(self, message):
		self.printLine(message)

	def sleep(self, seconds):
		start = time.time()
		while time.time() < start + seconds and self.alive:
			time.sleep(1)