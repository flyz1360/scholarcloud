#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from thuproxy.models import *
from thuproxy.alipay_api import *
import datetime
import logging
import uuid
import urllib.request

def register(request):
    errors = []
    auth.logout(request)
    if request.method == 'POST':
        if request.POST.get('username', '') and request.POST.get('password', ''):
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            if User.objects.filter(username=username).count() == 0:
                new_user = User.objects.create_user(username=username, password=password)

                if request.POST.get('email'):
                    email = request.POST.get('email', '')
                    new_user.email = email
                # duser = DUser(user=new_user)
                new_user.save()
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

@login_required(login_url="/login/")
def alipay_apply(request):
    userLoginSuccess = request.user.is_authenticated()
    # duser = DUser.objects.get(user=request.user)
    # pageName = "homepage"
    proxyaccount = ProxyAccount.objects.get(user=request.user)

    return render_to_response('alipay_apply.html', locals(), context_instance=RequestContext(request))

@login_required(login_url="/login/")
def alipay_submit(request):
    userLoginSuccess = request.user.is_authenticated()
    # duser = DUser.objects.get(user=request.user)
    # user = duser.user
    user  = request.user
    print (user.email)
    # pageName = "homepage"
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    money = request.POST['money']
    # try:
    if True:
        pay = Pay(out_trade_no = uuid.uuid1().hex,user=user,total_fee = money,status = 'U')
        pay.save()
        params = {
            'out_trade_no':pay.out_trade_no,
            'subject':u'加速学术云',
            'body':u'代理包月费',
            'total_fee':str(money)}
        total_fee = pay.total_fee
        alipay = Alipay(notifyurl="http://www.thucloud.com/alipay/callback",
                 returnurl="http://www.thucloud.com/alipay/success",
                 showurl="http://www.thucloud.com/alipay/success")
        params.update(alipay.conf)
        sign = alipay.buildSign(params)
        return render_to_response('alipay_order.html',locals())
    # except:
    #     return HttpResponse('生成帐单错误')
    return render_to_response('alipay_submit.html', locals(), context_instance=RequestContext(request))

@csrf_exempt
def alipay_callback(request):
    params = request.POST.dict()
    print ("call back params")
    print (params)
    alipay = Alipay()
    sign=None
    if 'sign' in params:
        sign=params['sign']
    locSign=alipay.buildSign(params)

    if sign==None or locSign!=sign:
        return HttpResponse("fail")

    print ("sign is ok")
    if params['trade_status']!='TRADE_FINISHED' and  params['trade_status']!='TRADE_SUCCESS':
        return HttpResponse("fail")
    else:
        print ("trade status ok")
        print ("Verify the request is call by alipay.com....")
        url = verifyURL['https'] + "&partner=%s&notify_id=%s"%(alipay.conf['partner'],params['notify_id'])
        print (url)
        response=urllib.request.urlopen(url)
        html=response.read()

        print ("aliypay.com return: %s" % html)
        if html== b'true':
            print ('result is true')
            #try:
            if True:
                out_trade_no = params['out_trade_no']
                trade_no = params['trade_no']
                buyer_id = params['buyer_id']
                buyer_email = params['buyer_email']
                total_fee = params['total_fee']
                pay = Pay.objects.get(out_trade_no = out_trade_no)
                if pay.status == 'S':
                    return HttpResponse("success")
                pay.status = 'S'
                pay.trade_no = trade_no
                pay.buyer_id = buyer_id
                pay.buyer_email = buyer_email
                pay.total_fee = float(total_fee)
                pay.save()
                print ('payuser',pay.user)
                #user = User.objects.get(id = pay.user)
                proxyaccount = ProxyAccount.objects.get(user=pay.user)
                print ('proxyaccount',proxyaccount)
                print ('pay total fee',pay.total_fee)
                if(pay.total_fee == 0.1):
                    print ('type 1 account')
                    proxyaccount.type = 1
                    proxyaccount.traffic = 100*1000
                elif(pay.total_fee == 5):
                    proxyaccount.type = 2
                    proxyaccount.traffic = 1000*1000
                elif(pay.total_fee == 10):
                    proxyaccount.type = 3
                    proxyaccount.traffic = 10*1000*1000
                elif(pay.total_fee == 20):
                    proxyaccount.type = 4
                    proxyaccount.traffic = 25*1000*1000
                elif(pay.total_fee == 50):
                    proxyaccount.type = 5
                    proxyaccount.traffic = 100*1000*1000
                 # if(proxyaccount.expired_date == None):
                if True:
                    today = datetime.datetime.now()
                    expired_date  = today + datetime.timedelta(30)
                    print (today.strftime('%Y-%m-%d %H:%M:%S'))
                    print (expired_date.strftime('%Y-%m-%d %H:%M:%S'))
                    proxyaccount.paydate = today#.strftime('%Y-%m-%d %H:%M:%S')
                    proxyaccount.expired_date = expired_date#.strftime('%Y-%m-%d %H:%M:%S') 
                print (proxyaccount)
                proxyaccount.save()
            #except:
                #pass
            return HttpResponse("success")
            
        return HttpResponse("fail")


@login_required(login_url="/login/")
def alipay_success(request):
    userLoginSuccess = request.user.is_authenticated()
    # duser = DUser.objects.get(user=request.user)
    # pageName = "homepage"
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    return render_to_response('alipay_success.html', locals(), context_instance=RequestContext(request))
