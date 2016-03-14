#coding=utf-8
import pymysql
import socket


try:
    conn=pymysql.connect(host='58.205.208.71',user='root',passwd='thuproxy',port=8779,charset='utf8')
    cur=conn.cursor()                              #获取一个游标对象
    cur.execute("USE thuproxy")
    cur.execute("SELECT * FROM thuproxy_proxyaccount")
    data=cur.fetchall()

    for row in data:
        print(row[5])
        print(type(row[4]))
        try:
            address = ('166.111.80.96', 4127)
            socket.setdefaulttimeout(20)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(address)
            data = 'addport@'+str(row[5])+'\n'
            sock.send(data.encode())
            sock.close()
        except socket.error as e:
            print(e)
    cur.close()                                    #关闭游标
    conn.commit()                                  #向数据库中提交任何未解决的事务，对不支持事务的数据库不进行任何操作
    conn.close()                                   #关闭到数据库的连接，释放数据库资源

except  Exception as e:
    print(e)

# address = ('166.111.80.96', 4126)
# socket.setdefaulttimeout(20)
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect(address)
# data = 'addport@'+str(32112)+'\n'
# sock.send(data.encode())
# sock.close()
