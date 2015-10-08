# -*- coding: UTF-8 -*-
# 
# embed.py 
# (c) Point.im, 2015
# Модуль содержит процедуры для получения при помощи oEmbed и/или прочих 
# форматов данных для внедрения содержимого сторонних сервисов (e. g. DeviantArt, 
# Twitter, SoundCloud).

import json
from requests_oauthlib import OAuth1Session

# Арц, надо это в settings.py запихнуть, наверное
# я не понял, в какой для core
CONSUMER_KEY = "EMCxcCtYcss4aDYRAOWZ6eIUg"
CONSUMER_SECRET = "5kPeCjj4YJwV6ficWxAQNWA88vXuI2nzL4mgdn5CDsQrw5VdBl"
ACCESS_KEY = "132107638-uloTUyV4E7eGAlByiknW83i1CRkNz95NjuoUYMcb"
ACCESS_SECRET = "JiVjMRXfb2btyqOXQd5Acl1wLQKIr5cYSDvqqbfaFh6le"

client_id = CONSUMER_KEY
client_secret = CONSUMER_SECRET

def GetTwitter(twi_id):
    twitter = OAuth1Session(CONSUMER_KEY,
                            client_secret=CONSUMER_SECRET,
                            resource_owner_key=ACCESS_KEY,
                            resource_owner_secret=ACCESS_SECRET)
    tweet_url = "https://api.twitter.com/1.1/statuses/oembed.json?id=%s&hide_media=1" % twi_id
    print tweet_url
    data = json.loads(twitter.get(tweet_url).text)

    if 'errors' in data:
        return
    else:
        return "<![CDATA[\n"+data['html']+"\n]]>"


if __name__ == '__main__':
    print GetTwitter(329651129988288514)