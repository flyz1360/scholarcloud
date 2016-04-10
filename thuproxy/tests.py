#coding=utf-8
import urllib
import urllib.request
import json

url = 'http://int.dpool.sina.com.cn/iplookup/iplookup.php?'
url_values = urllib.parse.urlencode({'format':'js-8', 'ip':'166.111.80.96'})
full_url = url+url_values
ip_data = urllib.request.urlopen(full_url).read()
ip_data_unicode = ip_data.decode('utf-8')
ip_data_unicode = ip_data_unicode[21:len(ip_data_unicode)-1]
result = json.loads(ip_data_unicode, 'utf-8')
print(1)
