#coding=utf-8
import pymysql
import socket
import httplib2
import os
import shutil
import datetime
ACCOUNT_TRAFFIC_LIMIT = {1: 100, 5: 1000, 10: 10000, 20: 25000, 50: 100000}

try:
    conn=pymysql.connect(host='58.205.208.71',user='root',passwd='thuproxy',port=8779,charset='utf8')
    cur=conn.cursor()                              #获取一个游标对象
    cur.execute("USE thuproxy")
    cur.execute("SELECT * FROM thuproxy_proxyaccount")
    data=cur.fetchall()
    address = ('166.111.80.96', 4127)
    socket.setdefaulttimeout(20)
    for row in data:
        expired_date = row[4]
        today = datetime.date.today()
        at = row[2]
        traffic = row[6]
        if expired_date is None:
            continue
        if expired_date < today:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(address)
                data = 'close@'+str(row[5])+',2'+'\n'
                sock.send(data.encode())
                sock.close()
            except socket.error as e:
                print(e)
        elif ACCOUNT_TRAFFIC_LIMIT[at] < traffic:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(address)
                data = 'close@'+str(row[5])+',1'+'\n'
                sock.send(data.encode())
                sock.close()
            except socket.error as e:
                print(e)

    cur.close()
    conn.commit()
    conn.close()
except Exception as e:
    print(e)
