#coding=utf-8
import time
import threading
from socket import *
import os


 
address = ('127.0.0.1', 8086)
s = socket.socket(AF_INET, SOCK_STREAM)
s.connect(address)
fn = './test.zip'
ff = os.path.normcase(fn)

try:
    f = open(fn, 'rb')
    BUFSIZE = 1024
    count = 0
    name = fn+'\r' # 前1k字节是为了给服务端发送文件名 一定要加上'\r',不然服务端就不能readline了
    for i in range(1, BUFSIZE - len(fn) -1):
        name += '?'

    s.send(name)
    s.se
    while True:
        print (BUFSIZE)
        fdata = f.read(BUFSIZE)
        if not fdata:
            print ('no data.')
            break
        s.send(fdata)
        count += 1
        if len(fdata) != BUFSIZE:
            print ('count:'+str(count))
            print (len(fdata))
        nRead = len(fdata)

    print ('send file finished.')
    f.close()
    s.close()
    print ('close socket')
except IOError:
    print ('open err')

