import re


class MessageParser(object):
    '''
    Class handles irc messages and notifies server_connection
    about them.
    '''

    def __init__(self, server_connection):
        self._sc = server_connection

    def _checkForPrivmsg(self, message):
        ":juke!~Jukkis@kosh.hut.fi PRIVMSG #testidevi :asdfadsf :D"
        privmsg_pattern = re.compile(r'''   # full host mask (1)
					 ^:((.*?)				# nick (2)
					 \!(.*?)				# username (3)
					 @(.*?))\s				# hostname (4)
					 PRIVMSG\s				# message type
					 (([\#|\!].*?)|(.*?))\s	# channel (5)(6) or nick (5)
					 :(.*.?)				# message (8)
					 ''', re.X)

        privmsg = privmsg_pattern.match(message)
        if not privmsg: return False

        try:
            source = privmsg.group(2)
            fullmask = privmsg.group(1)
            msg = privmsg.group(8)

            # channel
            if privmsg.group(5) == privmsg.group(6):
                target = privmsg.group(5)
                self._sc.channelMessageReceived(source, target, msg, fullmask)
            # private
            else:
                self._sc.privateMessageReceived(source, msg, fullmask)
        except AttributeError:
            pass

        return True

    def _checkForNickInUse(self, message):
        ":port80b.se.quakenet.org 433 * irckaaja :Nickname is already in use."

    def _checkForUsers(self, message):
        ":irc.cs.hut.fi 353 nettitutkabot @ #channlename :yournick @juke"
        users_pattern = re.compile(r'''
					 ^:.*?\s			# server
					 353\s				# users code
					 .*?\s				# hostname
					 [=|\@]\s
					 ([\#|\!].*?)\s		# channel (1)
					 :(.*)				# users (2)
					 ''', re.X)

        match = users_pattern.match(message)
        if not match: return False

        channel = match.group(1)
        userlist = match.group(2).split(" ")
        self._sc.usersReceived(channel, userlist)
        return True

    def _checkForUsersEnd(self, message):
        users_pattern = re.compile(r'''
					 ^:.*?\s			# server
					 366\s				# users end code
					 .*?\s				# hostname
					 ([\#|\!].*?)\s		# channel (1)
					 :(.*)				# message (2)
					 ''', re.X)

        match = users_pattern.match(message)
        if not match: return False

        channel = match.group(1)

        self._sc.usersEndReceived(channel)
        return True

    def _checkForPing(self, message):
        if not message.startswith("PING"):
            return False

        _, _, message = message.partition(" :")
        self._sc.pingReceived(message)
        return True

    def _checkForEndOfMotd(self, message):
        motd_pattern = re.compile(r'''
									^:		  # start and :
									.*?\s	  # server hostname
									376\s	  # MODE for end of motd message
									''', re.X)

        if not motd_pattern.match(message):
            return False

        self._sc.motdReceived(message)
        return True

    def _checkForQuit(self, message):
        ":Blackrobe!~Blackrobe@c-76-118-165-126.hsd1.ma.comcast.net QUIT :Signed off"
        quit_pattern = re.compile(r''' 			# fullmask (1)
								 ^:((.*?)		# nick (2)
								 \!(.*?)		# username (3)
								 @(.*?))\s		# hostname (4)
								 QUIT\s			# message type
								 :(.*.?)		# message (5)
								 ''', re.X)

        match = quit_pattern.match(message)
        if not match: return False

        name = match.group(2)
        fullmask = match.group(1)
        self._sc.quitReceived(name, fullmask)
        return True

    def _checkForPart(self, message):
        ":godlRmue!~Olog@lekvam.no PART #day9tv"
        part_pattern = re.compile(r''' 			# fullmask (1)
								 ^:((.*?)		# nick (2)
								 \!(.*?)		# username (3)
								 @(.*?))\s		# hostname (4)
								 PART\s			# message type
								 ([\#|\!].*.?)	# channel (5)
								 ''', re.X)

        match = part_pattern.match(message)
        if not match: return False

        fullmask = match.group(1)
        name = match.group(2)
        channel = match.group(5)

        self._sc.partReceived(name, channel, fullmask)
        return True

    def _checkForJoin(self, message):
        #message = ":Blackrobe!~Blackrobe@c-76-118-165-126.hsd1.ma.comcast.net JOIN #day9tv"
        ":imsopure!webchat@p50803C58.dip.t-dialin.net JOIN :#joindota"
        join_pattern = re.compile(r''' 					# fullmask (1)
								 ^:((.*?)				# nick (2)
								 \!(.*?)			 	# username (3)
								 @(.*?))\s			 	# hostname (4)
								 JOIN\s:?			    # message type
								 ([\#|\!].*.?)		 	# channel (5)
								 ''', re.X)

        match = join_pattern.match(message)
        if not match: return False

        fullmask = match.group(1)
        name = match.group(2)
        channel = match.group(5)

        self._sc.joinReceived(name, channel, fullmask)
        return True

    def _checkForTopicReply(self, message):
        ":dreamhack.se.quakenet.org 332 irckaaja #testidevi2 :asd"
        topic_reply_pattern = re.compile(r'''
										 ^:.*?\s			# server
										 332\s				# topic reply code
										 (.*?)\s			# nick (1)
										 ([\#|\!].*?)\s		# channel (2)
										 :(.*)				# topic (3)
										 ''', re.X)

        match = topic_reply_pattern.match(message)
        if not match: return False

        nick = match.group(1)
        channelname = match.group(2)
        topic = match.group(3)

        self._sc.topicReplyReceived(nick, channelname, topic)
        return True

    def _checkForTopic(self, message):
        ":juke!~Jukkis@kosh.hut.fi TOPIC #testidevi2 :lol"
        topic_pattern = re.compile(r''' 				# fullmask (1)
								 ^:((.*?)				# nick (2)
								 \!(.*?)			 	# username (3)
								 @(.*?))\s			 	# hostname (4)
								 TOPIC\s:?			    # message type
								 ([\#|\!].*.?)\s		# channel (5)
								 :(.*.?)				# topic (6)
								 ''', re.X)
        match = topic_pattern.match(message)
        if not match: return False

        fullmask = match.group(1)
        nick = match.group(2)
        channelname = match.group(5)
        topic = match.group(6)

        self._sc.topicReceived(nick, channelname, topic, fullmask)
        return True

    def parse(self, message):
        '''
        Tries to figure out what the message is.
        '''
        if self._checkForEndOfMotd(message): return

        if self._checkForPing(message): return

        if self._checkForPrivmsg(message): return

        if self._checkForUsers(message): return
        if self._checkForUsersEnd(message): return

        if self._checkForJoin(message): return
        if self._checkForPart(message): return
        if self._checkForQuit(message): return

        if self._checkForTopic(message): return
        if self._checkForTopicReply(message): return

        #if self.checkForError(message) : return

        self._sc.unknownMessageReceived(message)

#p = MessageParser(None)
#p.checkForJoin(None)
