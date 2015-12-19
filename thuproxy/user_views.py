#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from thuproxy.models import *
from thuproxy.proxy_account_views import get_port_num


def register(request):
    errors = []
    auth.logout(request)
    if request.method == 'POST':
        if request.POST.get('username', '') and request.POST.get('password', '') and request.POST.get('email', ''):
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            email = request.POST.get('email', '')
            if User.objects.filter(username=username).count() == 0:
                new_user = User.objects.create_user(username=username, password=password, email=email)

                new_user.save()
                proxy_account_list = ProxyAccount.objects.order_by("-port")
                if len(proxy_account_list) == 0:
                    proxyaccount = ProxyAccount(user=new_user, type=0, port=10001, traffic=0)
                else:
                    proxyaccount = ProxyAccount(user=new_user, type=0, port=get_port_num(), traffic=0)
                proxyaccount.save()
                request.session['username'] = username
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
    error = False
    if request.method == 'POST':
        if request.POST['username'] and request.POST['password']:
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return HttpResponseRedirect('/homepage/')
    error = True
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def user_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


def validate_username(request):
    user = User.objects.filter(username=request.GET.get('userName',''))
    if len(user) == 0:
        message = 'yes'
    else:
        message = 'no'
    return HttpResponse(message)
