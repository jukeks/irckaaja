from optparse import OptionParser
from time import sleep

from config import Config
from serverconnection import ServerConnection


def get_options():
    parser = OptionParser()
    parser.add_option(
        "-c",
        "--configfile",
        dest="configfile",
        help="Reads FILE as a configfile",
        metavar="FILE",
        default="config.ini",
    )

    options, _ = parser.parse_args()
    return options


def main():
    options = get_options()
    conf = Config(options.configfile)
    modulesd = conf.modules()
    bot_info = conf.bot()
    server_connection_list = []

    for network_name, server_conf in conf.servers().iteritems():
        join_list = conf.channels(network_name)
        server_connection_list.append(
            ServerConnection(network_name, server_conf, bot_info, join_list, modulesd)
        )

    for s in server_connection_list:
        s.connect()

    # Interrupts are only handled in the main thread in Python so...
    while True:
        try:
            sleep(1.0)
        except KeyboardInterrupt:
            for s in server_connection_list:
                s.kill()
            break


if __name__ == "__main__":
    main()
