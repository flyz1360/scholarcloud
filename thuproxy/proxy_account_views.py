#coding=utf-8
import django
django.setup()
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.contrib.auth.decorators import login_required
from thuproxy.models import *
import datetime
import json
import uuid
import socket
import random
import os
import httplib2
from uwsgidecorators import *
from django.utils import timezone
from urllib import request
import pytz
from django.utils import timezone
import urllib.request


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangowebsite.settings")
date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, datetime.datetime)
    or isinstance(obj, datetime.date)
    else None
)

# 流量限制
ACCOUNT_TRAFFIC_LIMIT = {1: 100, 5: 5000, 10: 10000, 20: 25000, 50: 100000}
CLOSE_REASON = {'over_flow': 1, 'expired': 2}


def script_lz(request, script_name):
    if script_name == 'create_pac':
        proxy_account_id = request.GET.get('pid')
        proxy_account = ProxyAccount.objects.get(id=proxy_account_id)
        if proxy_account:
            create_pac(proxy_account)
        else:
            return HttpResponse('failed')
    elif script_name == 'regen_pac':
        regen_pac()
    elif script_name == 'open_listen_port':
        port_num = request.GET.get('portNum')
        account_type = request.GET.get('accountType')
        open_listen_port(port_num, account_type)
    elif script_name == 'update_flow':
        update_flow(1)
    elif script_name == 'flush_flow':
        flush_flow(1)
    elif script_name == 'judge_expire':
        judge_expire(1)
    elif script_name == 'test':
        judge_expire(1)
    else:
        return HttpResponse('no such script')
    return HttpResponse('success')


def create_pac(proxy_account):
    template_pac_file = open("./static/myproxy.pac", "r+")
    pac_content = template_pac_file.read()
    pac_port_no = uuid.uuid1()
    print("**** create pac: pac_no", pac_port_no)
    proxy_account.pac_no = pac_port_no
    proxy_account.save()
    pac_content = pac_content.replace("4128", str(proxy_account.port))
    user_pac_file = open('/data/pac/'+str(pac_port_no)+'.pac', 'w+')
    user_pac_file.write(pac_content)
    user_pac_file.close()


# in case the pac files in server are lost
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


# open the port on proxy server
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


# reopen the port on proxy server, for cases such as 欠费后重新缴费
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


def downgrade_port(port_num, account_type):
    try:
        address = ('166.111.80.96', 4127)
        socket.setdefaulttimeout(30)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        data = 'downgrade@'+str(port_num)+','+str(account_type)+'\n'
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
    result = {}
    try:
        address = ('166.111.80.96', 4127)
        socket.setdefaulttimeout(30)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        data = 'getIP@'+str(port_num)+'\n'
        sock.send(data.encode())
        message = sock.recv(1024)
        message = message.decode('utf-8')
        tmp = message.split('@')
        result['address'] = tmp[0]
        result['city'] = urllib.request.unquote(tmp[1])
        sock.close()
    except socket.error as e:
        print(e)
    return result


def get_ip_address_list(port_num):
    ip_address_list = []
    try:
        address = ('166.111.80.96', 4127)
        socket.setdefaulttimeout(30)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        data = 'getIPList@'+str(port_num)+'\n'
        sock.send(data.encode())
        message = sock.recv(1024)
        raw_ips = message.decode('utf-8')
        ips = raw_ips.split(',')
        for ip in ips:
            if ip != '':
                tmp = ip.split('@')
                result = dict()
                result['address'] = tmp[0]
                result['time'] = tmp[1]
                result['city'] = urllib.request.unquote(tmp[2])
                ip_address_list.append(result)
        sock.close()
    except socket.error as e:
        print(e)
    return ip_address_list


def update_flow_cron():
    http_client = httplib2.HTTPConnectionWithTimeout('localhost', 8000, timeout=30)
    http_client.request('GET', '/script_lz/update_flow/')


@cron(58, -1, -1, -1, -1)
def update_flow(num):
    try:
        print(datetime.datetime.now())
        print('****update flow log')
        account_list = ProxyAccount.objects.filter(pac_no__isnull=False)
        if account_list is not None:
            address = ('166.111.80.96', 4127)
            socket.setdefaulttimeout(30)

            for account in account_list:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(address)
                    data = 'getflow@'+str(account.port)+'\n'
                    sock.send(data.encode())
                    message = sock.recv(1024)
                    traffic = float(message)
                    # todo 已经超过流量，超过100M设置惩罚
                    if float(account.traffic) > ACCOUNT_TRAFFIC_LIMIT[int(account.type)]:
                        if (float(account.traffic) - float(ACCOUNT_TRAFFIC_LIMIT[int(account.type)])) > 100.0:
                            if not os.path.exists('/data/over_traffic/'+str(account.port)):
                                f = open('/data/over_traffic/'+str(account.port), 'a')
                                f.write(str(account.port)+','+str(traffic)+','+str(account.traffic))
                                f.close()
                        continue

                    if traffic > float(account.traffic):
                        account.traffic = traffic
                    # 因为某些原因proxy server重启后导致脚本记录的流量小于用户当前流量
                    # 需要请求上一次脚本记录的流量值做delta更新
                    elif traffic < float(account.traffic):
                        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock1.connect(address)
                        data = 'preflow@'+str(account.port)+'\n'
                        sock1.send(data.encode())
                        message = sock1.recv(1024)
                        sock1.close()
                        traffic_pre = float(message)
                        print('pre flow '+str(traffic_pre))
                        if traffic >= traffic_pre:
                            account.traffic = float(account.traffic) + (traffic - traffic_pre)
                        else:
                            account.traffic = float(account.traffic) + traffic

                    # 超流量
                    if float(account.traffic) > ACCOUNT_TRAFFIC_LIMIT[int(account.type)]:
                        close_port(int(account.port), CLOSE_REASON['over_flow'])
                    # print('update '+str(accout.port)+' '+str(traffic)+' for '+str(accout.traffic))
                    account.save()
                    sock.close()

                    # 记录到数据库
                    now = timezone.now()
                    t = Traffic(user=account.user, traffic=account.traffic, time=now)
                    t.save()
                except Exception as e:
                    print('error', e)
    except Exception as e:
        print('error', e)


# 月初对所有账户的流量清零
def flush_flow_cron():
    http_client = httplib2.HTTPConnectionWithTimeout('localhost', 8000, timeout=30)
    http_client.request('GET', '/script_lz/flush_flow/')


@cron(1, 0, 1, -1, -1)
def flush_flow(num):
    account_list = ProxyAccount.objects.filter(pac_no__isnull=False)
    if account_list is not None:
        for account in account_list:
            account.traffic = 0
            account.save()


# 每天判断一次是否过期
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
    try:
        is_user_login = request.user.is_authenticated()
        user = request.user
        page_name = "homepage"
        proxy_account = ProxyAccount.objects.get(user=request.user)
        if "error" in request.session:
            error = request.session['error']
            del request.session['error']

        # 是否付过费
        if proxy_account.type != 0:
            if datetime.datetime.now().date() <= proxy_account.expired_date:
                remain_time = proxy_account.expired_date - datetime.datetime.now().date()
                proxy_account.remain_time = int(remain_time.days)
            else:
                proxy_account.remain_time = None

            proxy_account.traffic_limit = ACCOUNT_TRAFFIC_LIMIT[int(proxy_account.type)]
            proxy_account.traffic = round(proxy_account.traffic, 2)
            result = get_ip_address(proxy_account.port)
            proxy_account.ip_address = result['address']
            proxy_account.city = result['city']
        else:
            proxy_account.remain_time = None
            proxy_account.traffic = 0
            proxy_account.ip_address = None

        return render_to_response('homepage.html', locals(), context_instance=RequestContext(request))
    except Exception as e:
        print(e)
    return HttpResponse('failed')


@login_required(login_url="/login/")
def ip_history(request):
    is_user_login = request.user.is_authenticated()
    page_name = "homepage"
    proxy_account = ProxyAccount.objects.get(user=request.user)
    ip_list = get_ip_address_list(proxy_account.port)
    return render_to_response('ip_history.html', locals(), context_instance=RequestContext(request))


@login_required()
def get_flow_json(request):
    try:
        user_id = request.GET.get('userid')
        is_daily = int(request.GET.get('is_daily'))
        month = timezone.datetime.strptime(timezone.now().strftime('%Y-%m'), '%Y-%m')
        traffic_history = Traffic.objects.filter(user_id=user_id, time__gte=month)
        flow_result_json = list()
        tz = pytz.timezone('Asia/Shanghai')
        if is_daily == 1:
            traffic_acc = 0
            day = traffic_history[0].time.astimezone(tz).date()
            for traffic in traffic_history:
                if traffic is traffic_history[len(traffic_history)-1]:
                    flow_result_json.append({'time': traffic.time.astimezone(tz).date(),
                                             'traffic': traffic.traffic-traffic_acc})

                elif traffic.time.astimezone(tz).date() != day:
                    flow_result_json.append({'time': day, 'traffic': traffic.traffic-traffic_acc})
                    traffic_acc = traffic.traffic
                    day = traffic.time.astimezone(tz).date()
        elif is_daily == 0:
            for traffic in traffic_history:
                flow_result_json.append({'time': traffic.time.date(), 'traffic': traffic.traffic})

        date_handler = lambda obj: (
            obj.isoformat()
            if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date)
            else None
        )
        result = json.dumps(flow_result_json, default=date_handler)
        return HttpResponse(result, content_type="application/json")
    except Exception as e:
        print(e)
    return HttpResponse('failed')


@login_required(login_url="/login/")
def show_orders(request):
    is_user_login = request.user.is_authenticated()
    page_name = "homepage"
    user = request.user
    pay_list = Pay.objects.filter(user_id=user.id)
    return render_to_response('orders_list.html', locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def show_flows(request):
    is_user_login = request.user.is_authenticated()
    page_name = "homepage"
    user = request.user
    traffic_list = Traffic.objects.filter(user=user)
    return render_to_response('flow_history.html', locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def downgrade(request):
    is_user_login = request.user.is_authenticated()
    user = request.user
    proxy_account = ProxyAccount.objects.get(user=request.user)
    pay_type = request.POST['pay_type']
    downgrade_type = int(request.POST['type'])
    if downgrade_type not in {1, 5, 10, 20}:
        return HttpResponse("account_type_error")
    else:
        print("downgrade success: type ", downgrade_type)
        today = datetime.date.today()
        remain_day = proxy_account.expired_date - today
        extend_day = remain_day * (float(proxy_account.type) / float(downgrade_type))

        proxy_account.expired_date = today + datetime.timedelta(int(extend_day.days))
        proxy_account.type = downgrade_type
        proxy_account.save()
    downgrade_port(proxy_account.port, proxy_account.type)
    return render_to_response('downgrade_success.html', locals(), context_instance=RequestContext(request))
