# -*- coding: UTF-8 -*-

'''
embed.py 
(c) Point.im, 2015
Модуль содержит процедуры для получения при помощи oEmbed и/или прочих 
форматов данных для внедрения содержимого сторонних сервисов (e. g. DeviantArt, 
Twitter, SoundCloud).
'''

import urllib, json, oauth2 as oauth, json

try:
    import re2 as re
except ImportError:
    import re

#try:
#    import settings
#except ImportError:
#    pass

# Арц, надо это в settings.py запихнуть, наверное
# я не понял, в какой для core
CONSUMER_KEY = "EMCxcCtYcss4aDYRAOWZ6eIUg"
CONSUMER_SECRET = "5kPeCjj4YJwV6ficWxAQNWA88vXuI2nzL4mgdn5CDsQrw5VdBl"
ACCESS_KEY = "132107638-uloTUyV4E7eGAlByiknW83i1CRkNz95NjuoUYMcb"
ACCESS_SECRET = "JiVjMRXfb2btyqOXQd5Acl1wLQKIr5cYSDvqqbfaFh6le"

def GetTwitter(twi_id):
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    access_token = oauth.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
    client = oauth.Client(consumer, access_token)
    tweet = "https://api.twitter.com/1.1/statuses/oembed.json?id=%s&hide_media=1" % twi_id
    print tweet
    response, data = client.request(tweet)
    data = json.loads(data)
    if 'errors' in data:
        return
    else:
        return "<![CDATA[\n"+data['html']+"\n]]>"




if __name__ == '__main__':
    print GetTwitter(329651129988288514)
