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

def main():
	options = getOptions()
	conf = Config(options.configfile)
	modulelist = conf.modules()
	bot = conf.bot()
	serverlist = []
	
	for networkname, serverd in conf.servers().iteritems():
		joinlist = conf.channels(networkname)
		serverlist.append(
			ServerConnection(networkname, serverd, bot, 
							joinlist, modulelist))
	
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

if __name__ == '__main__':
	main()