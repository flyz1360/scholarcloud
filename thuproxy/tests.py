#encoding=utf-8
import socket
from urllib import request

result = {}
try:
    address = ('166.111.80.96', 4127)
    socket.setdefaulttimeout(30)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    data = 'getIP@'+str(18625)+'\n'
    sock.send(data.encode())
    message = sock.recv(1024)
    message = message.decode('utf-8')
    tmp = message.split('@')
    result['address'] = tmp[0]
    b = tmp[1]
    b = request.unquote(b)
    result['city'] = tmp[1]
    sock.close()
except socket.error as e:
    print(e)
