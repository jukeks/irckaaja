from config import Config
from serverconnection import ServerConnection
from optparse import OptionParser
from time import sleep
from dynamicmodule import DynamicModule

def getOptions():
	parser = OptionParser()
	parser.add_option("-c", "--configfile", dest="configfile",
	                  help="Reads FILE as a configfile", metavar="FILE", default="config.ini")
	parser.add_option("-d", "--daemon",
					  action="store_true", dest="daemon", default = False,
	                  help="Runs as a daemon")
	
	options, _ = parser.parse_args()
	return options

options = getOptions()
c = Config(options.configfile)



bot = c.bot()
realname = bot['realname']
nick = bot['nick']
altnick = bot.get('altnick', nick+"_")
owner = bot['owner']

modulelist = c.modules()

serverlist = []
serverd = c.servers()
for k, v in serverd.iteritems():
	serveralias = k
	port = v.get('port', 6667)
	hostname = v.get('hostname')
	channellist = c.channels(serveralias)
	print owner
	sc = ServerConnection(hostname, port, nick, altnick, realname, realname, owner, channellist, serveralias)
	
	sc.dynamicmodules = [DynamicModule(sc, m) for m in modulelist]
	serverlist.append(sc)
	
	
for s in serverlist:
	s.connect()
	
while True:
	try:
		sleep(1.0)
	except KeyboardInterrupt:
		print ""
		for s in serverlist:
			s.kill()
		break
