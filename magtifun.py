#!/usr/bin/env python
import urllib,urllib2,cookielib,sys

cookie_jar = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
urllib2.install_opener(opener)

url_1 = 'http://www.magtifun.ge/index.php?page=11&lang=ge'
values = dict(password='password', user='username', act='1')
data = urllib.urlencode(values)
req = urllib2.Request(url_1, data)
rsp = urllib2.urlopen(req)

url_2 = 'http://www.magtifun.ge/scripts/sms_send.php'
number = int(sys.argv[1])
values = dict(recipients=number, message_body=sys.argv[2])
data = urllib.urlencode(values)
req = urllib2.Request(url_2,data)
rsp = urllib2.urlopen(req)
