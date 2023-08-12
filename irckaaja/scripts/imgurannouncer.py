import json
import re

import httplib

from irckaaja.botscript import BotScript

CLIENT_ID = '75c435ce216d1f2'

APIHOST = 'api.imgur.com'
IMAGEAPI = '/3/image/'
ALBUMAPI = '/3/album/'
GALLERYIMAGEAPI = '/3/gallery/image/'

class ImgurAnnouncer(BotScript):
    def on_channel_message(self, nick, target, message, full_mask):
        titles = ImgurAnnouncer._get_titles(message)
        if titles:
            for title in titles:
                self.say(target, "** " + title + " **")

    @staticmethod
    def _get_titles(message):
        gallery_img = "http://imgur.com/gallery/"
        album = "http://imgur.com/a/"
        img = "http://imgur.com/"

        urls = BotScript.parse_urls(message)
        if not urls:
            return
        titles = []
        for url in urls:
            id = url.split("/")[-1]
            title = None
            if url.startswith(gallery_img):
                title = ImgurAnnouncer._query_gallery_image_caption(id)
            elif url.startswith(album):
                title = ImgurAnnouncer._query_album_caption(id)
            elif url.startswith(img):
                title = ImgurAnnouncer._query_image_caption(id)

            if title:
                titles.append(title)
        return titles

    @staticmethod
    def _query_api(api, id):
        try:
            h = httplib.HTTPSConnection(APIHOST)
            headers = {"Authorization": "Client-ID " + CLIENT_ID}
            h.request("GET", api + id, headers=headers)
            resp = h.getresponse()

            resp = resp.read()
            resp = json.loads(resp)
            h.close()

            return resp['data']['title']
        except:
            return None

    @staticmethod
    def _query_gallery_image_caption(id):
        return ImgurAnnouncer._query_api(GALLERYIMAGEAPI, id)

    @staticmethod
    def _query_image_caption(id):
        return ImgurAnnouncer._query_api(IMAGEAPI, id)

    @staticmethod
    def _query_album_caption(id):
        return ImgurAnnouncer._query_api(ALBUMAPI, id)

if __name__ == '__main__':
    print ImgurAnnouncer._get_titles('http://imgur.com/gallery/nctxEnV http://imgur.com/gallery/uV3b1 http://imgur.com/a/uV3b1' )
