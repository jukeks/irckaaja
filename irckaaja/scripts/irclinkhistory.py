import dbm
import time
from typing import Any, Dict, Tuple

from irckaaja.botscript import BotScript, User
from irckaaja.client import IrcClient
from irckaaja.scripts.urls import parse_urls


def serialize(ts: float, nick: str, message: str) -> bytes:
    return ",".join([str(int(ts)), nick, message]).encode()


def deserialize(b: bytes) -> Tuple[float, str, str]:
    ts, nick, message = b.decode().split(",", 2)
    return float(ts), nick, message


class IrcLinkHistory(BotScript):
    def __init__(self, client: IrcClient, config: Dict[str, Any]) -> None:
        BotScript.__init__(self, client, config)

        self.store_path = config["store_path"] or "./"

        self.channels = (
            [config["channels"]]
            if isinstance(config["channels"], str)
            else config["channels"]
        )
        self.dbs: Dict[str, dbm._Database] = {}

        for channel in self.channels:
            assert channel, "Channel name must be non empty"
            self.dbs[channel] = dbm.open(self.store_path + "/" + channel, "c")

    def _get_diff_string(self, t1: float, t2: float) -> str:
        diff = t1 - t2

        if diff < 60:
            return "%d seconds" % diff
        elif diff < 60 * 60:
            minutes = diff / 60.0
            seconds = (minutes - int(minutes)) * 60
            return "%d minutes, %d seconds" % (minutes, seconds)
        elif diff < 60 * 60 * 24:
            hours = diff / (60.0 * 60)
            minutes = (hours - int(hours)) * 60
            seconds = (minutes - int(minutes)) * 60
            return "%d hours, %d minutes, %d seconds" % (
                hours,
                minutes,
                seconds,
            )
        elif diff < 60 * 60 * 24 * 365:
            days = diff / (60.0 * 60 * 24)
            hours = (days - int(days)) * 24
            minutes = (hours - int(hours)) * 60
            seconds = (minutes - int(minutes)) * 60
            return "%d days, %d hours, %d minutes, %d seconds" % (
                days,
                hours,
                minutes,
                seconds,
            )
        else:
            years = diff / (60.0 * 60 * 24 * 365)
            days = (years - int(years)) * 365
            hours = (days - int(days)) * 24
            minutes = (hours - int(hours)) * 60
            seconds = (minutes - int(minutes)) * 60
            return "%d years, %d days, %d hours, %d minutes, %d seconds" % (
                years,
                days,
                hours,
                minutes,
                seconds,
            )

    def on_channel_message(
        self,
        user: User,
        channel_name: str,
        message: str,
    ) -> None:
        urls = parse_urls(message)

        if not urls:
            return
        try:
            db = self.dbs[channel_name]
        except KeyError:
            return

        for url in urls:
            url = url.strip()
            history_tuple_raw = db.get(url)
            if not history_tuple_raw:
                db[url] = serialize(time.time(), user.nick, message)
            else:
                old_time, old_nick, old_message = deserialize(history_tuple_raw)
                self.say(
                    channel_name,
                    "previously seen "
                    + self._get_diff_string(time.time(), old_time)
                    + " ago",
                )
                self.say(
                    channel_name, "< " + old_nick + "> " + old_message + ""
                )
