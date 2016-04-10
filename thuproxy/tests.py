#coding=utf-8
import urllib
import urllib.request
import json

url = 'http://pv.sohu.com/cityjson?'
url_values = urllib.parse.urlencode({'ie':'utf-8', 'ip':'122.31.32.1'})
full_url = url+url_values
ip_data = urllib.request.urlopen(full_url).read()
ip_data_unicode = ip_data.decode('utf-8')
ip_data_unicode = ip_data_unicode[19:len(ip_data_unicode)-1]
print(ip_data_unicode)
