# Irckaaja

A scriptable IRC bot with a Python interface.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
pip install irckaaja
```

## Usage
```bash
python -m irckaaja.irckaaja -c config.ini
```

### Configuration

Example configuration:

```ini
[servers]
	[[QuakeNet]] # also alias for the network
		hostname = se.quakenet.org
		port = 6667 # if port is no defined, default is 6667
		channels = "#example1", "#example2"
	#[[IRCNet]]
	#	hostname = irc.cs.hut.fi

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

