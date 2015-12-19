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
    proxyaccount.pac_no = pac_no;
    proxyaccount.save()
    d = d.replace("4128", str(proxyaccount.port))
    user_pac = open('/data/pac/'+str(pac_no)+'.pac', 'w+')
    user_pac.write(d)
    user_pac.close()


def open_listen_port(port_num):
    address = ('166.111.80.96', 4127)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    data = 'addport@'+str(port_num)+'\n'
    sock.send(data.encode())
    sock.close()


def get_port_num():
    random_data = range(4130, 47000)
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

    # 付费完但没有生成pac文件和开通端口
    if proxyaccount.paydate is not None and proxyaccount.pac_no is None:
        create_pac(proxyaccount)
        open_listen_port(proxyaccount.port)

    if proxyaccount.expired_date is not None:
        if datetime.datetime.now().date() <= proxyaccount.expired_date:
            print('ok')
            proxyaccount.remainTime = proxyaccount.expired_date - datetime.datetime.now().date()
            proxyaccount.remainTime = str(proxyaccount.remainTime).replace('days, 0:00:00','天')
        else:
            proxyaccount.remainTime = None
    else:
        proxyaccount.remainTime = None
    return render_to_response('homepage.html', locals(), context_instance=RequestContext(request))

