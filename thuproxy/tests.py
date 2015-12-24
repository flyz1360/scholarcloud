#coding=utf-8
import socket

try:
    address = ('166.111.80.96', 4127)
    socket.setdefaulttimeout(20)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    data = 'addport@'+'10003'+'\n'
    sock.send(data.encode())
    sock.close()
except socket.error as e:
    print(e)
