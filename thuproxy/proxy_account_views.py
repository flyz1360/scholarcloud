#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.contrib.auth.decorators import login_required
from thuproxy.models import *
import datetime
import uuid
import  socket
import random


def create_pac(proxyaccount):
    template_pac = open("./static/myproxy.pac", "r+")
    d = template_pac.read()
    pac_no = uuid.uuid1()
    print ("pac_no", pac_no)
    proxyaccount.pac_no = pac_no;
    proxyaccount.save()
    # d = d.replace("4128", str(proxyaccount.port))
    # user_pac = open('/data/pac/'+str(pac_no)+'.pac', 'w+')
    # user_pac.write(d)
    # user_pac.close()


def regen_pac(request):
    template_pac = open("./static/myproxy.pac", "r+")
    d = template_pac.read()
    account_list = ProxyAccount.objects.filter(pac_no__isnull=False)
    print(len(account_list))
    for account in account_list:
        print ("pac_no", account.pac_no)
        d = d.replace("4128", str(account.port))
        user_pac = open('/data/pac/'+str(account.pac_no)+'.pac', 'w+')
        user_pac.write(d)
        user_pac.close()
    return HttpResponse('success')


def open_listen_port(port_num):
    try:
        address = ('166.111.80.96', 4127)
        print ("connecting")
        socket.setdefaulttimeout(30)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        data = 'addport@'+str(port_num)+'\n'
        sock.send(data.encode())
        sock.close()
    except socket.error as e:
        print(e)
    print ("connected")


def get_port_num():
    random_data = range(10001, 47000)
    while True:
        port_num = random.sample(random_data, 1)
        if ProxyAccount.objects.filter(port=port_num[0]).count() == 0:
            return port_num[0]


@login_required(login_url="/login/")
def homepage(request):
    userLoginSuccess = request.user.is_authenticated()
    # duser = DUser.objects.get(user=request.user)
    user = request.user
    pageName = "homepage"
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    if "error" in request.session:
        error = request.session['error']
        del request.session['error']
    if proxyaccount.expired_date is not None:
        if datetime.datetime.now().date() <= proxyaccount.expired_date:
            remain_time = proxyaccount.expired_date - datetime.datetime.now().date()
            proxyaccount.remain_time = int(remain_time.days)
        else:
            proxyaccount.remain_time = None
    else:
        proxyaccount.remain_time = None
    return render_to_response('homepage.html', locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def show_orders(request):
    userLoginSuccess = request.user.is_authenticated()
    pageName = "homepage"
    user = request.user
    pay_list = Pay.objects.filter(user_id=user.id)
    return render_to_response('show_orders.html', locals(), context_instance=RequestContext(request))

