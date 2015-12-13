#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from thuproxy.models import *
from datetime import datetime
import time
import logging

def register(request):
    errors = []
    auth.logout(request)
    if request.method == 'POST':
        if request.POST.get('username', '') and request.POST.get('password', ''):
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            if User.objects.filter(username=username).count() == 0:
                new_user = User.objects.create_user(username=username, password=password)
                duser = DUser(user=new_user)
                if request.POST.get('email'):
                    email = request.POST.get('email', '')
                    duser.email = email
                duser.save()
                proxy_account_list = ProxyAccount.objects.order_by("-port")
                if len(proxy_account_list) == 0:
                    proxyaccount = ProxyAccount(user=new_user, type=0, port=10000, traffic=0)
                else:
                    proxyaccount = ProxyAccount(user=new_user, type=0, port=proxy_account_list[0].port+1, traffic=0)
                proxyaccount.save()
                return HttpResponseRedirect('/')
            else:
                errors.append('用户名已存在')
        else:
                errors.append('请填写完整')

    return render_to_response('register.html', {
        'errors': errors,
        'username': request.POST.get('username', ''),
        'password': request.POST.get('password', ''),
        'email': request.POST.get('email', ''),
    },
     context_instance=RequestContext(request))


def login(request):
    user = None
    if request.method == 'POST':
        if request.POST['username'] and request.POST['password']:
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return HttpResponseRedirect('/homepage/')
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def user_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
