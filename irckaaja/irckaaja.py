from optparse import OptionParser, Values
from time import sleep

from irckaaja.client import IrcClient
from irckaaja.config import Config


def get_options() -> Values:
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


def main() -> None:
    options = get_options()
    conf = Config(options.configfile)
    modulesd = conf.modules()
    bot_info = conf.bot()
    connection_list = []

    for server_conf in conf.servers().values():
        connection_list.append(IrcClient(server_conf, bot_info, modulesd))

    for s in connection_list:
        s.connect()

    # Interrupts are only handled in the main thread in Python so...
    while True:
        try:
            sleep(1.0)
        except KeyboardInterrupt:
            for s in connection_list:
                s.kill()
            break


if __name__ == "__main__":
    main()
