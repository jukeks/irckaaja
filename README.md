# Irckaaja

[![Python application](https://github.com/jukeks/irckaaja/actions/workflows/ci.yml/badge.svg)](https://github.com/jukeks/irckaaja/actions/workflows/ci.yml)

A scriptable IRC bot with a Python interface.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Scripts](#scripts)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## Installation

irckaaja requires Python 3.9 or newer. The package is available on [PyPI](https://pypi.org/project/irckaaja/)
and can be installed with pip

```bash
pip install irckaaja
```

## Usage
```bash
python -m irckaaja.irckaaja -c config.ini
```

## Scripts

To build your own scripts, subclass `irckaaja.botscript.BotScript`. Currently
subscribable events are

```python
    def on_channel_message(
        self, user: User, channel_name: str, message: str
    ) -> None:
        """
        Called when a channel message is received.
        """

    def on_private_message(self, user: User, message: str) -> None:
        """
        Called when a private message is received.
        """

    def on_join(self, user: User, channel_name: str) -> None:
        """
        Called when a user joins a channel.
        """

    def on_part(self, user: User, channel_name: str) -> None:
        """
        Called when a user parts a channel.
        """

    def on_quit(self, user: User) -> None:
        """
        Called when a user quits the network.
        """

    def on_connect(self) -> None:
        """
        Called when bot has connected to the network.
        """

    def on_topic(self, user: User, channel_name: str, topic: str) -> None:
        """
        Called when topic has changed on a channel.
        """
```

A simple greeter bot would look like this.

```python
from irckaaja.botscript import BotScript, User


class HelloWorld(BotScript):
    """
    A simple script class. Only responds to messages starting "hello"
    in every joined channel.
    """

    def on_channel_message(
        self, user: User, channel_name: str, message: str
    ) -> None:
        if message.startswith("hello"):
            self.say(channel_name, "hello, " + user.nick)
            return
```

The modules should be present in the `irckaaja.scripts` package and named as the
lowercase of the class name found in the module. E.g. script called `Greeter`
should be placed to `irckaaja.scripts.greeter.Greeter`.

Loading of modules is controlled by the `[modules]` section of the configuration
 file:

```ini
[modules]
    [[Greeter]]
        arbitrary_configuration = "passed to script as a dict[str, Any]"
```

### Configuration

Example configuration:

```ini
[servers]
    [[QuakeNet]] # also alias for the network
        hostname = se.quakenet.org
        port = 6667 # if port is no defined, default is 6667
        channels = "#example1", "#example2"
        # use_tls: true # if not defined, default is false
        # ca_path: "path" # use to trust additional CAs
    #[[IRCNet]]
    #    hostname = irc.cs.hut.fi

[bot]
    nick = irckaaja
    altnick = irckaaja_ # if not provided, nick + "_"
    realname = Irkkaa Nörttien Kanssa
    username = irckaaja
    owner = "nick!user@example.com"

[modules]
    [[HelloWorld]]
```


## Screenshots

![Connection output](doc/output.png "Connection output")

## Contributing

Drop a pull request if you have something you'd want to incorporate.

## License

See [Licence.txt](LICENCE.txt).
