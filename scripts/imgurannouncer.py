import re
import httplib
from botscript import BotScript

CLIENT_ID = '75c435ce216d1f2'

APIHOST = 'api.imgur.com'
IMAGEAPI = '/3/image/'
ALBUMAPI = '/3/album/'
GALLERYIMAGEAPI = '/3/gallery/image/'

class ImgurAnnouncer(BotScript):
    def onChannelMessage(self, nick, target, message, full_mask):
        ids = self._parse_ids(message)

        for id in ids:
            title = self._query_title(id)
            if title:
                self.say(target, "** " + title + " **")

    @staticmethod
    def _parse_ids(message):
        urls = BotScript.parse_urls(message)
        if not urls:
            return
        ids = []
        for url in urls:
            match = re.match(re.compile(r'''https?://
                        (youtu\.be/|www\.youtube\.com/watch\?v=)
                        (\S*?)($|\?\S*$)
                         ''', re.X),
                             url)

            if match:
                ids.append(match.group(2))
        return ids

    @staticmethod
    def _query_api(id):
        print "lol"

    @staticmethod
    def _query_gallery_image_caption(id):
        ImgurAnnouncer._query_api(id)

if __name__ == '__main__':
    ImgurAnnouncer._query_gallery_image_caption('qZmYt0C')
