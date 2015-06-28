# -*- coding: utf-8 -*-

"""
Получение и обработка данных об изображении DeviantArt при помощи oEmbed
========================================================================

(c) Point.im Project, 2015

Документация DeviantArt oEmbed <https://www.deviantart.com/developers/oembed>
"""

import urllib2
import json
from markdown.util import etree


class DeviantArtPreview:
    def __init__(self):
        self.DEVIANT_OEMBED_URL = "http://backend.deviantart.com/oembed?url="

    def deviant_preview(self, url):
        try:
            print '>>> url: ', url
            print '%s%s' % (self.DEVIANT_OEMBED_URL, url)
            response = urllib2.urlopen('%s%s' % (self.DEVIANT_OEMBED_URL, url))
            s = response.read()
            print "S: ",s
        except Exception,e:
            print 'e: ',e
            print '>>> Error?'
            wrap = etree.Element('div')
            a = etree.SubElement(wrap, 'a')
            a.set('href', url)
            return url 
        else:
            data = json.loads(s)
            wrap = etree.Element('div')
            wrap.set('class', 'clearfix')
            a = etree.SubElement(wrap, 'a')
            a.set('href', url)
            a.set('class', 'postimg')
            img = etree.SubElement(a, 'img')
            img.set('src', data['thumbnail_url'])
            img.set('alt', data['title']+" by "+data['author_name'])
            img.set('height', data['thumbnail_height_200h'])

            return wrap


if __name__ == "__main__":
    d = DeviantArtPreview()
    url = ('http://jasonchanart.deviantart.com/art/Maul-Splicer-542484356')
    d.deviant_preview(url)