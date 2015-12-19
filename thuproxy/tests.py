#coding=utf-8
import socket

address = ('166.111.80.96', 4127)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(address)
data = 'addport@'+'10003'+'\n'
sock.send(data.encode())
sock.close()
