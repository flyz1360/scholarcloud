#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from thuproxy.models import *
from django.contrib.auth.decorators import login_required

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
    pageName = "homepage"
    proxyaccount = ProxyAccount.objects.get(user=request.user)
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
            if dcode == '12345':
                proxyaccount = ProxyAccount.objects.get(user=request.user)
                proxyaccount.type = 1
                proxyaccount.month = 1
                proxyaccount.save()
                return render_to_response('homepage.html', locals(), context_instance=RequestContext(request))
            elif dcode == '23456':
                proxyaccount = ProxyAccount.objects.get(user=request.user)
                proxyaccount.type = 2
                proxyaccount.month = 12
                proxyaccount.save()
                return render_to_response('homepage.html', locals(), context_instance=RequestContext(request))
            else:
                error = True
                return render_to_response('dcode.html', locals(), context_instance=RequestContext(request))
    return HttpResponseRedirect('/dcode')

