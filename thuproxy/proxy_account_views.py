#coding=utf-8
import django
django.setup()
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.contrib.auth.decorators import login_required
from thuproxy.models import *
import datetime
import time
import uuid
import socket
import random
import os
import httplib2
from uwsgidecorators import *


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangowebsite.settings")
ACCOUNT_TRAFFIC_LIMIT = {1: 100, 5: 1000, 10: 10000, 20: 25000, 50: 100000}
CLOSE_REASON = {'over_flow': 1, 'expired': 2}


def script_lz(request, script_name):
    if script_name == 'create_pac':
        proxyaccount_id = request.GET.get('pid')
        proxyaccount = ProxyAccount.objects.get(id=proxyaccount_id)
        if proxyaccount:
            create_pac(proxyaccount)
        else:
            return HttpResponse('failed')
    elif script_name == 'regen_pac':
        regen_pac()
    elif script_name == 'open_listen_port':
        port_num = request.GET.get('portNum')
        account_type = request.GET.get('accountType')
        open_listen_port(port_num, account_type)
    elif script_name == 'update_flow':
        # todo
        update_flow(1)
    elif script_name == 'flush_flow':
        flush_flow(1)
    elif script_name == 'judge_expire':
        judge_expire(1)
    elif script_name == 'test':
        judge_expire()
    else:
        return HttpResponse('no such script')
    return HttpResponse('success')


def create_pac(proxyaccount):
    template_pac = open("./static/myproxy.pac", "r+")
    d = template_pac.read()
    pac_no = uuid.uuid1()
    print("pac_no", pac_no)
    proxyaccount.pac_no = pac_no
    proxyaccount.save()
    d = d.replace("4128", str(proxyaccount.port))
    user_pac = open('/data/pac/'+str(pac_no)+'.pac', 'w+')
    user_pac.write(d)
    user_pac.close()


def regen_pac():
    account_list = ProxyAccount.objects.filter(pac_no__isnull=False)
    print(len(account_list))
    for account in account_list:
        print("pac_no", account.pac_no)
        d = open("./static/myproxy.pac", "r+").read()
        d = d.replace("4128", str(account.port))
        user_pac = open('/data/pac/'+str(account.pac_no)+'.pac', 'w+')
        user_pac.write(d)
        user_pac.close()


def open_listen_port(port_num, account_type):
    try:
        address = ('166.111.80.96', 4127)
        socket.setdefaulttimeout(30)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        data = 'addport@'+str(port_num)+','+str(account_type)+'\n'
        sock.send(data.encode())
        sock.close()
    except socket.error as e:
        print(e)


# java服务还在，只需删去iptables中根据端口号drop规则，不需流量、带宽等
def reopen_port(port_num):
    try:
        address = ('166.111.80.96', 4127)
        socket.setdefaulttimeout(30)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        data = 'reopen@'+str(port_num)+'\n'
        sock.send(data.encode())
        sock.close()
    except socket.error as e:
        print(e)


# 超过流量或者过期
def close_port(port_num, reason):
    try:
        address = ('166.111.80.96', 4127)
        socket.setdefaulttimeout(30)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        data = 'close@'+str(port_num)+','+str(reason)+'\n'
        sock.send(data.encode())
        sock.close()
    except socket.error as e:
        print(e)


def upgrade_port(port_num, account_type):
    try:
        address = ('166.111.80.96', 4127)
        socket.setdefaulttimeout(30)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        data = 'upgrade@'+str(port_num)+','+str(account_type)+'\n'
        sock.send(data.encode())
        sock.close()
    except socket.error as e:
        print(e)


def get_port_num():
    random_data = range(10001, 19999)
    while True:
        port_num = random.sample(random_data, 1)
        if ProxyAccount.objects.filter(port=port_num[0]).count() == 0:
            return port_num[0]


def get_ip_address(port_num):
    ip_address = None
    try:
        address = ('166.111.80.96', 4127)
        socket.setdefaulttimeout(30)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        data = 'getIP@'+str(port_num)+'\n'
        sock.send(data.encode())
        message = sock.recv(1024)
        ip_address = message.decode('utf-8')
        sock.close()
    except socket.error as e:
        print(e)
    return ip_address


# abandoned
def update_flow_cron():
    http_client = httplib2.HTTPConnectionWithTimeout('localhost', 8000, timeout=30)
    http_client.request('GET', '/script_lz/update_flow/')


@cron(58, -1, -1, -1, -1)
def update_flow(num):
    try:
        print(datetime.datetime.now())
        print('log update flow')
        account_list = ProxyAccount.objects.filter(pac_no__isnull=False)
        if account_list is not None:
            address = ('166.111.80.96', 4127)
            socket.setdefaulttimeout(30)

            for accout in account_list:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(address)
                    data = 'getflow@'+str(accout.port)+'\n'
                    sock.send(data.encode())
                    message = sock.recv(1024)
                    traffic = float(message)
                    # todo 已经超过流量，超过100M设置惩罚
                    if float(accout.traffic) > ACCOUNT_TRAFFIC_LIMIT[int(accout.type)]:
                        if (float(accout.traffic) - float(ACCOUNT_TRAFFIC_LIMIT[int(accout.type)])) > 100.0:
                            if not os.path.exists('/data/over_traffic/'+str(accout.port)):
                                f = open('/data/over_traffic/'+str(accout.port), 'a')
                                f.write(str(accout.port)+','+str(traffic)+','+str(accout.traffic))
                                f.close()
                        continue

                    if traffic > float(accout.traffic):
                        accout.traffic = traffic
                    elif traffic < float(accout.traffic):
                        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock1.connect(address)
                        data = 'preflow@'+str(accout.port)+'\n'
                        sock1.send(data.encode())
                        message = sock1.recv(1024)
                        sock1.close()
                        traffic_pre = float(message)
                        print('pre flow '+str(traffic_pre))
                        if traffic >= traffic_pre:
                            accout.traffic = float(accout.traffic) + (traffic - traffic_pre)
                        else:
                            accout.traffic = float(accout.traffic) + traffic

                    # 超流量
                    if float(accout.traffic) > ACCOUNT_TRAFFIC_LIMIT[int(accout.type)]:
                        close_port(int(accout.port), CLOSE_REASON['over_flow'])
                    print('update '+str(accout.port)+' '+str(traffic)+' for '+str(accout.traffic))
                    accout.save()
                    sock.close()
                except Exception as e:
                    print('error', e)
    except Exception as e:
        print('error', e)


# abandoned
def flush_flow_cron():
    http_client = httplib2.HTTPConnectionWithTimeout('localhost', 8000, timeout=30)
    http_client.request('GET', '/script_lz/flush_flow/')


# todo 数据库中traffic清零同时reopen所有port（其实也可不用，那边iptables-F了）
@cron(1, 0, 1, -1, -1)
def flush_flow(num):
    account_list = ProxyAccount.objects.filter(pac_no__isnull=False)
    if account_list is not None:
        for account in account_list:
            account.traffic = 0
            account.save()


# abandoned
def judge_expire_cron():
    http_client = httplib2.HTTPConnectionWithTimeout('localhost', 8000, timeout=30)
    http_client.request('GET', '/script_lz/judge_expire/')


@cron(57, 23, -1, -1, -1)
def judge_expire(num):
    try:
        today = datetime.date.today()
        print(today)
        print('judge expire')
        account_list = ProxyAccount.objects.filter(expired_date=today)
        if account_list is not None:
            for account in account_list:
                close_port(account.port, CLOSE_REASON['expired'])
    except Exception as e:
        print(e)


@login_required(login_url="/login/")
def homepage(request):
    userLoginSuccess = request.user.is_authenticated()
    user = request.user
    pageName = "homepage"
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    if "error" in request.session:
        error = request.session['error']
        del request.session['error']

    # 是否付过费
    if proxyaccount.type != 0:
        if datetime.datetime.now().date() <= proxyaccount.expired_date:
            remain_time = proxyaccount.expired_date - datetime.datetime.now().date()
            proxyaccount.remain_time = int(remain_time.days)
        else:
            proxyaccount.remain_time = None

        proxyaccount.traffic_limit = ACCOUNT_TRAFFIC_LIMIT[int(proxyaccount.type)]
        proxyaccount.traffic = round(proxyaccount.traffic, 2)
        proxyaccount.ip_address = get_ip_address(proxyaccount.port)
    else:
        proxyaccount.remain_time = None
        proxyaccount.traffic = 0
        proxyaccount.ip_address = None

    return render_to_response('homepage.html', locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def show_orders(request):
    userLoginSuccess = request.user.is_authenticated()
    pageName = "homepage"
    user = request.user
    pay_list = Pay.objects.filter(user_id=user.id)
    return render_to_response('show_orders.html', locals(), context_instance=RequestContext(request))

