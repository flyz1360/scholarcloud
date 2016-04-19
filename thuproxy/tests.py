#encoding=utf-8
import urllib
import urllib.request
import json
import sys

try:
    url = 'http://int.dpool.sina.com.cn/iplookup/iplookup.php?'
    url_values = urllib.parse.urlencode({'format':'js-8', 'ip':'106.37.225.179'})
    full_url = url+url_values
    # print(full_url)
    ip_data = urllib.request.urlopen(full_url).read()
    ip_data_unicode = ip_data.decode('unicode_escape')
    ip_data_unicode = ip_data_unicode[21:len(ip_data_unicode)-1]
    print(ip_data_unicode)
    result = json.loads(ip_data_unicode)
    print(result)
    print(result['city'])
except Exception as e:
    print(e)
