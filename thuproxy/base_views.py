#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from thuproxy.models import *
from django.contrib.auth.decorators import login_required
import datetime

__author__ = 'lz'


def index(request):
    userLoginSuccess = request.user.is_authenticated()
    if userLoginSuccess is True:
        user = request.user
    else:
        user = None
    pageName = "index"
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))


def guide(request):
    userLoginSuccess = request.user.is_authenticated()
    user = request.user
    pageName = "guide"
    return render_to_response('guide.html', locals(), context_instance=RequestContext(request))

def accoutTypes(request):
    userLoginSuccess = request.user.is_authenticated()
    user = request.user
    pageName = "accoutTypes"
    return render_to_response('accoutTypes.html', locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def homepage(request):
    userLoginSuccess = request.user.is_authenticated()
    # duser = DUser.objects.get(user=request.user)
    user = request.user
    pageName = "homepage"
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    print ('proxy account expired date')
    print (proxyaccount.expired_date)    
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


@login_required(login_url="/login/")
def pay(request):
    userLoginSuccess = request.user.is_authenticated()
    return render_to_response('pay.html', locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def dcode(request):
    userLoginSuccess = request.user.is_authenticated()
    return render_to_response('dcode.html', locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def inputDcode(request):
    userLoginSuccess = request.user.is_authenticated()
    error = False
    if request.method == 'POST':
        if request.POST.get('dcode', ''):
            dcode = request.POST['dcode']
            if dcode == '123456':
                proxyaccount = ProxyAccount.objects.get(user=request.user)
                proxyaccount.type = 1
                today = datetime.datetime.now()
                expired_date  = today + datetime.timedelta(30)
                proxyaccount.paydate = today
                proxyaccount.expired_date = expired_date
                proxyaccount.save()
                return HttpResponseRedirect('/homepage')
            else:
                error = True
                return render_to_response('dcode.html', locals(), context_instance=RequestContext(request))
    return HttpResponseRedirect('/dcode')

