#encoding=utf-8
import urllib
import urllib.request
import json
import sys


if len(sys.argv) != 1:
    print('arg num error')
else:
    try:
        ip = '61.158.188.2'
        # url = 'http://int.dpool.sina.com.cn/iplookup/iplookup.php?'
        url = 'http://ip.taobao.com/service/getIpInfo.php?'
        url_values = urllib.parse.urlencode({'ip':ip})
        # url_values = urllib.parse.urlencode({'format':'js-8', 'ip':ip})
        full_url = url+url_values
        ip_data = urllib.request.urlopen(full_url).read()
        ip_data_unicode = ip_data.decode('unicode_escape')
        ip_data_unicode = ip_data_unicode[17:len(ip_data_unicode)-1]
        # print('中文')
        result = json.loads(ip_data_unicode, 'unicode_escape')
        print(result['city'].encode('utf-8'))
    except Exception as e:
        print(e)
