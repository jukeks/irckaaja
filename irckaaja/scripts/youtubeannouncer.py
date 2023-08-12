__author__ = "juke"
import re
import urllib
from typing import Any
from xml.dom import minidom

from irckaaja.botscript import BotScript

APIURL = "http://gdata.youtube.com/feeds/api/videos/"


class YoutubeAnnouncer(BotScript):
    def on_channel_message(
        self, nick: str, target: str, message: str, full_mask: str
    ) -> None:
        ids = self._parse_ids(message)

        if ids:
            for id in ids:
                title = self._query_title(id)
                if title:
                    self.say(target, "** " + title + " **")

    @staticmethod
    def _parse_ids(message: str) -> list[str]:
        urls = BotScript.parse_urls(message)
        if not urls:
            return []
        ids = []
        for url in urls:
            match = re.match(
                re.compile(
                    r"""https?://
                        (youtu\.be/|www\.youtube\.com/watch\?v=)
                        (\S*?)($|\?\S*$)
                         """,
                    re.X,
                ),
                url,
            )

            if match:
                ids.append(match.group(2))
        return ids

    @staticmethod
    def _query_title(id: str) -> Any:
        xml = urllib.request.urlopen(APIURL + id).read()
        return (
            minidom.parseString(xml)
            .getElementsByTagName("title")[0]
            .childNodes[0]
            .nodeValue
        )
