#coding=utf-8
import pymysql
import socket
import os

# os.system('iptables -F')

# file_names = os.listdir('/proxy/over_flow')
# for filename in file_names:
#     port = filename.split('.')[0]
#     os.system('iptables -A INPUT -p tcp --dport '+port+' -j DROP')

try:
    conn=pymysql.connect(host='58.205.208.71',user='root',passwd='thuproxy',port=8779,charset='utf8')
    cur=conn.cursor()                              #获取一个游标对象
    cur.execute("USE thuproxy")
    cur.execute("SELECT * FROM thuproxy_proxyaccount")
    data=cur.fetchall()

    for row in data:
        print(row[2])
        if row[2] != 0:
            print(row[5])
            os.system('/home/zy/script/iptables_add.sh ' + str(row[5]))
    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源
    os.system('iptables -A OUTPUT -p tcp --sport 4128 -j ACCEPT')
except  Exception as e:
    print(e)
