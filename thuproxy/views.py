#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
import datetime
from django.shortcuts import render_to_response, RequestContext
from thuproxy.models import *
from django.contrib import auth
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
                proxyaccount = ProxyAccount(user=new_user, type=0, month=0, port=0)
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
def homepage(request):
    userLoginSuccess = request.user.is_authenticated()
    duser = DUser.objects.get(user=request.user)
    pageName = "homepage"
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    return render_to_response('homepage.html', locals(), context_instance=RequestContext(request))

@login_required(login_url="/login/")
def cancel_checkout(request):
    return HttpResponseRedirect('/homepage')

@login_required(login_url="/login/")
def finish_checkout(request):
    return HttpResponseRedirect('/homepage')

@login_required(login_url="/login/")
def user_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


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

def ipn_listener(request):
    print request
    return HttpResponse('ok')

# def display_meta(request):
#     values = request.META.items()
#     #values.sort()
#     html = []
#     for k, v in values:
#         html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
#     return HttpResponse('<table>%s</table>' % '\n'.join(html))
#
#
# def search_form(request):
#     return render_to_response('search_form.html')
#
#
# def search(request):
#     error = False
#     if 'q' in request.GET:
#         q = request.GET['q']
#         if not q:
#             error = True
#         else:
#             books = Book.objects.filter(title__icontains=q)
#             return render_to_response('search_results.html',
#                 {'books': books, 'query': q})
#     return render_to_response('search_form.html',
#         {'error': error})
#
#