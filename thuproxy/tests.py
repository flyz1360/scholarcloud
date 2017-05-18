#coding=utf-8
import socket

try:
    address = ('166.111.80.96', 4129)
    socket.setdefaulttimeout(30)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    data = 'addport@'+str(20001)+','+str(50)+'\n'
    sock.send(data.encode())
    sock.close()
except socket.error as e:
    print(e)