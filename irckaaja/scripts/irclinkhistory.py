__author__ = 'juke'
# -*- coding: utf-8 -*-


from irckaaja.botscript import BotScript
import shove
import re
import time
import urlparse


class IrcLinkHistory(BotScript):
    def __init__(self, server_connection, config):
        BotScript.__init__(self, server_connection, config)

        self.store_path = config['store_path']

        self.channels = [config['channels']] if isinstance(config['channels'], "".__class__) else config['channels']
        self.dbs = {}
        for channel in self.channels:
            self.dbs[channel] = shove.Shove("bsddb://" + self.store_path + "/" + channel + ".db")


    def _getDiffString(self, t1, t2):
        diff = t1 - t2

        if diff < 60:
            return "%d sekuntia" % diff
        elif diff < 60 * 60:
            minutes = diff / 60.0
            seconds = (minutes - int(minutes)) * 60
            return "%d minuuttia, %d sekuntia" % (minutes, seconds)
        elif diff < 60 * 60 * 24:
            hours = diff / (60.0 * 60)
            minutes = (hours - int(hours)) * 60
            seconds = (minutes - int(minutes)) * 60
            return "%d tuntia, %d minuuttia, %d sekuntia" % (hours, minutes, seconds)
        elif diff < 60 * 60 * 24 * 365:
            days = diff / (60.0 * 60 * 24)
            hours = (days - int(days)) * 24
            minutes = (hours - int(hours)) * 60
            seconds = (minutes - int(minutes)) * 60
            return "%d päivää, %d tuntia, %d minuuttia, %d sekuntia" % (days, hours, minutes, seconds)
        else:
            years = diff / (60.0 * 60 * 24 * 365)
            days = (years - int(years)) * 365
            hours = (days - int(days)) * 24
            minutes = (hours - int(hours)) * 60
            seconds = (minutes - int(minutes)) * 60
            return "%d vuotta, %d päivää, %d tuntia, %d minuuttia, %d sekuntia" % (years, days, hours, minutes, seconds)

    def on_channel_message(self, nick, channel_name, message, full_mask):
        urls = self.parse_urls(message)

        if not urls:
            return
        try:
            db = self.dbs[channel_name]
        except KeyError:
            return

        for url in urls:
            url = url.strip()
            history_tuple = db.get(url)
            if not history_tuple:
                db[url] = (time.time(), nick, message)
                db.sync()
            else:
                old_time, old_nick, old_message = history_tuple
                self.say(channel_name, "wanha! jo " + self._getDiffString(time.time(), old_time))
                self.say(channel_name, '< ' + old_nick + '> ' + old_message + '')
