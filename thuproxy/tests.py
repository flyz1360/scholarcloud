#coding=utf-8
import pymysql
import socket
import httplib2


http_client = httplib2.HTTPConnectionWithTimeout('localhost', 8000, timeout=30)
http_client.request('GET', '/script_lz/update_flow/')
