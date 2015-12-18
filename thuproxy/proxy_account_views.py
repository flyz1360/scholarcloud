#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.contrib.auth.decorators import login_required
from thuproxy.models import *
import datetime
import uuid


def create_pac(proxyaccount):
    template_pac = open("./static/myproxy.pac", "r+")
    d = template_pac.read()
    pac_no = uuid.uuid1()
    proxyaccount.pac_no = pac_no;
    proxyaccount.save()
    d = d.replace("4128", str(proxyaccount.port))
    user_pac = open('/test/'+str(pac_no)+'.pac', 'w+')
    user_pac.write(d)
    user_pac.close()


@login_required(login_url="/login/")
def homepage(request):
    userLoginSuccess = request.user.is_authenticated()
    # duser = DUser.objects.get(user=request.user)
    user = request.user
    pageName = "homepage"
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    if proxyaccount.paydate is not None and proxyaccount.pac_no is None:
        create_pac(proxyaccount)
    if(proxyaccount.expired_date != None):
        if(datetime.datetime.now().date() <= proxyaccount.expired_date):
            print ('ok')
            proxyaccount.remainTime = proxyaccount.expired_date - datetime.datetime.now().date()
            proxyaccount.remainTime = str(proxyaccount.remainTime).replace('days, 0:00:00','天')
        else:
            proxyaccount.remainTime = None
    else:
        proxyaccount.remainTime = None
    return render_to_response('homepage.html', locals(), context_instance=RequestContext(request))

