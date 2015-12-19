#coding=utf-8
from thuproxy.models import *
from thuproxy.alipay_api import *
import datetime
import uuid
import urllib.request
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext

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
    user = request.user
    print (user.email)
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    m = request.POST['money']
    money = float(m)/100
    pay_type = request.POST['type']
    month = request.POST['month']
    try:
        pay = Pay(out_trade_no=uuid.uuid1().hex, user=user, total_fee=money, type=int(pay_type), month=int(month), status='U')
        pay.save()
        params = {
            'out_trade_no':pay.out_trade_no,
            'subject':u'清云加速',
            'body':u'流量购买费用',
            'total_fee':str(money)}
        total_fee = pay.total_fee
        alipay = Alipay(notifyurl="http://scholar.thucloud.com/alipay/callback",
                 returnurl="http://scholar.thucloud.com/alipay/success",
                 showurl="http://scholar.thucloud.com/alipay/success")
        params.update(alipay.conf)
        sign = alipay.buildSign(params)
        return render_to_response('alipay_order.html',locals())
    except:
        return HttpResponse('生成帐单错误')

    return render_to_response('alipay_submit.html', locals(), context_instance=RequestContext(request))

@csrf_exempt
def alipay_callback(request):
    params = request.POST.dict()
    print("call back params")
    print(params)
    alipay = Alipay()
    sign = None
    if 'sign' in params:
        sign = params['sign']
    locSign = alipay.buildSign(params)

    if sign is None or locSign != sign:
        return HttpResponse("fail")

    print ("sign is ok")
    if params['trade_status']!='TRADE_FINISHED' and  params['trade_status']!='TRADE_SUCCESS':
        return HttpResponse("fail")
    else:
        print("trade status ok")
        print("Verify the request is call by alipay.com....")
        url = verifyURL['https'] + "&partner=%s&notify_id=%s"%(alipay.conf['partner'],params['notify_id'])
        print(url)
        response = urllib.request.urlopen(url)
        html = response.read()

        print("aliypay.com return: %s" % html)
        if html == b'true':
            print('result is true')
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
                proxyaccount = ProxyAccount.objects.get(user=pay.user)
                print ('proxyaccount',proxyaccount)
                print ('pay total fee',pay.total_fee)
                month = pay.month
                pay_type = pay.type
                if pay_type == 1:
                    account_type = int(float(total_fee)*100)/int(month)
                    print("accounttype"+account_type)
                    if account_type not in {1,2,3,4,5}:
                        return HttpResponse("fail")
                    else:
                        print("success:"+pay_type+" month"+month)
                        proxyaccount.type = account_type
                        today = datetime.datetime.now()
                        if proxyaccount.expired_date is not None:
                            print("add month")
                            expired_date = proxyaccount.expired_date + datetime.timedelta(30*int(month))
                        else:
                            print("init month")
                            expired_date = today + datetime.timedelta(30*int(month))
                        if proxyaccount.paydate is not None:
                            print("init paydate")
                            proxyaccount.paydate = today
                        proxyaccount.expired_date = expired_date
                else:
                    return HttpResponse("fail")

                if True:
                    today = datetime.datetime.now()
                    expired_date  = today + datetime.timedelta(30)
                    proxyaccount.paydate = today
                    proxyaccount.expired_date = expired_date
                print(proxyaccount)
                proxyaccount.save()
            return HttpResponse("success")

        return HttpResponse("fail")


@login_required(login_url="/login/")
def alipay_success(request):
    userLoginSuccess = request.user.is_authenticated()
    # duser = DUser.objects.get(user=request.user)
    # pageName = "homepage"
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    return render_to_response('alipay_success.html', locals(), context_instance=RequestContext(request))



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

