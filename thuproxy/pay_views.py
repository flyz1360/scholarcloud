#coding=utf-8
from thuproxy.models import *
from thuproxy.alipay_api import *
from thuproxy.proxy_account_views import *
import datetime
import uuid
import urllib.request
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext

@login_required(login_url="/login/")
def alipay_apply(request, pay_type):
    userLoginSuccess = request.user.is_authenticated()
    user = request.user
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    pay_list = Pay.objects.filter(user_id=user.id,status='U')
    if len(pay_list) != 0:
        request.session["error"] = "need_repay"
        return HttpResponseRedirect('/homepage')
    if pay_type == 'first':
        if proxyaccount.expired_date != None:
            request.session["error"] = "first_pay"
            return HttpResponseRedirect('/homepage')
        return render_to_response('alipay_create_order_first.html', locals(), context_instance=RequestContext(request))
    elif pay_type == 'upgrade':
        if proxyaccount.type == 50:
            request.session["error"] = "upgrade"
            return HttpResponseRedirect('/homepage')
        if datetime.datetime.now().date() <= proxyaccount.expired_date:
            remain_time = proxyaccount.expired_date - datetime.datetime.now().date()
            proxyaccount.remain_time = int(remain_time.days)
        return render_to_response('alipay_create_order_upgrade.html', locals(), context_instance=RequestContext(request))
    elif pay_type == 'continue':
        return render_to_response('alipay_create_order_continue.html', locals(), context_instance=RequestContext(request))
    else:
        return HttpResponse('充值请求错误')


@login_required(login_url="/login/")
def alipay_apply_temp(request):
    userLoginSuccess = request.user.is_authenticated()
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    return render_to_response('alipay_create_order_temp.html', locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def alipay_create_orders(request):
    userLoginSuccess = request.user.is_authenticated()
    user = request.user
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    # todo
    m = request.POST['money']
    money = float(m)/100
    pay_type = request.POST['pay_type']
    month = request.POST['month']
    today = datetime.datetime.now()
    print(money, pay_type)
    try:
        pay = Pay(out_trade_no=uuid.uuid1().hex, user=user, total_fee=money, type=int(pay_type), month=int(month), status='U', create_date=today)
        pay.save()
        params = {'out_trade_no':pay.out_trade_no, 'subject':u'清云加速', 'body':u'流量购买费用', 'total_fee':str(money)}
        total_fee = pay.total_fee
        alipay = Alipay(notifyurl="http://scholar.thucloud.com/alipay/callback",
                 returnurl="http://scholar.thucloud.com/alipay/success",
                 showurl="http://scholar.thucloud.com/alipay/success")
        params.update(alipay.conf)
        sign = alipay.buildSign(params)
        return render_to_response('alipay_order.html',locals())
    except Exception as e:
        print(e)
        return HttpResponse('生成订单错误')


@login_required(login_url="/login/")
def alipay_repay_orders(request, pay_no):
    userLoginSuccess = request.user.is_authenticated()
    user = request.user
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    try:
        pay_list = Pay.objects.filter(out_trade_no=pay_no)
        if len(pay_list) != 1:
            request.session["error"] = "repay"
            return HttpResponseRedirect('/homepage')
        else:
            pay = pay_list[0]
            params = {'out_trade_no':pay.out_trade_no, 'subject':u'清云加速', 'body':u'流量购买费用', 'total_fee':str(pay.total_fee)}
            total_fee = pay.total_fee
            alipay = Alipay(notifyurl="http://scholar.thucloud.com/alipay/callback",
                     returnurl="http://scholar.thucloud.com/alipay/success",
                     showurl="http://scholar.thucloud.com/alipay/success")
            params.update(alipay.conf)
            sign = alipay.buildSign(params)
            money = pay.total_fee
            return render_to_response('alipay_order.html',locals())
    except Exception as e:
        print(e)
        return HttpResponse('显示订单错误')


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
             # todo change iftrue to try
            if True:
                out_trade_no = params['out_trade_no']
                trade_no = params['trade_no']
                total_fee = params['total_fee']
                pay = Pay.objects.get(out_trade_no = out_trade_no)
                # todo all of return httpResponse
                if pay.status == 'S':
                    return HttpResponse("S")

                print ('payuser',pay.user)
                proxyaccount = ProxyAccount.objects.get(user=pay.user)
                print ('proxyaccount',proxyaccount)
                print ('pay total fee',pay.total_fee)
                month = pay.month
                pay_type = pay.type
                print ('paytype', pay_type)
                print ('month',month)
                # todo
                if float(total_fee) == 0.10:
                    real_fee = float(total_fee) * 10
                else:
                    real_fee = float(total_fee)*100
                print ('realfee',real_fee)

                if pay_type == 1:
                    account_type = int(real_fee)/int(month)
                    print("accounttype", account_type)
                    if account_type not in {1,5,10,20,50}:
                        return HttpResponse("accout_type_error")
                    else:
                        print("success:",account_type," month",month)
                        proxyaccount.type = account_type
                        today = datetime.datetime.now()
                        if proxyaccount.expired_date is not None:
                            return HttpResponse("not init")
                        else:
                            print("init date")
                            expired_date = today + datetime.timedelta(30*int(month))
                        if proxyaccount.paydate is None:
                            create_pac(proxyaccount)
                            print("create_pac done")
                            open_listen_port(proxyaccount.port, proxyaccount.type)
                            print("open_listen_port done")
                            proxyaccount.paydate = today
                        proxyaccount.expired_date = expired_date
                elif pay_type == 2:  # 续费
                    account_type = int(real_fee)/int(month)
                    print("accounttype", account_type)
                    if account_type != proxyaccount.type or proxyaccount.expired_date is None:
                        return HttpResponse("accout_type_error")
                    else:
                        print("success:",account_type," month",month)
                        today = datetime.date.today()
                        print("add month")
                        if proxyaccount.expired_date < today:  #  欠费啦
                            expired_date = today + datetime.timedelta(30*int(month))
                            reopen_port(proxyaccount.port)
                        else:
                            expired_date = proxyaccount.expired_date + datetime.timedelta(30*int(month))
                        proxyaccount.expired_date = expired_date
                elif pay_type == 3:
                    upgrade_delta = (real_fee/month)*30
                    upgrade_delta = int(upgrade_delta+0.1)
                    print(upgrade_delta)
                    proxyaccount.type += upgrade_delta
                    if proxyaccount.type not in {1,5,10,20,50}:
                        return HttpResponse("accout_type_error")
                else:
                    pay.status = 'F'
                    pay.save()
                    return HttpResponse("fail")

                print("sava pay")
                pay.status = 'S'
                pay.trade_no = trade_no
                pay.total_fee = real_fee
                pay.save()
                print("sava proxyaccount")
                proxyaccount.save()
            return HttpResponse("success")
        return HttpResponse("fail")


@login_required(login_url="/login/")
def alipay_success(request):
    userLoginSuccess = request.user.is_authenticated()
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


@login_required(login_url="/login/")
def alipay_cancel(request, pay_no):
    print(pay_no)
    pay = Pay.objects.filter(out_trade_no=pay_no)
    if len(pay) != 1:
        request.session["error"] = "cancel"
        return HttpResponseRedirect('/homepage')
    else:
        pay[0].status = 'C'
        pay[0].save()
        return HttpResponseRedirect('/homepage')


def alipay_test(request):
    pay_type = int(request.POST['pay_type'])
    month = int(request.POST['month'])
    total_fee = float(request.POST['money'])
    total_fee /= 100
    proxyaccount = ProxyAccount.objects.get(user=request.user)
    if float(total_fee) == 0.10:
        real_fee = float(total_fee) * 10
    else:
        real_fee = float(total_fee*100)
    print ('realfee',real_fee)

    if pay_type == 1:
        account_type = int(real_fee)/int(month)
        print("accounttype", account_type)
        if account_type not in {1,5,10,20,50}:
            return HttpResponse("accout_type_error")
        else:
            print("success:",account_type," month",month)
            proxyaccount.type = account_type
            today = datetime.datetime.now()
            if proxyaccount.expired_date is not None:
                print("add month")
                return HttpResponse("not init")
            else:
                print("init month")
                expired_date = today + datetime.timedelta(30*int(month))
            if proxyaccount.paydate is None:
                print("init paydate")
                create_pac(proxyaccount)
                print ("create_pac done")
                open_listen_port(proxyaccount.port)
                print ("open_listen_port done")
                proxyaccount.paydate = today
            proxyaccount.expired_date = expired_date
    elif pay_type == 2:
        account_type = int(real_fee)/int(month)
        print("accounttype", account_type)
        if account_type != proxyaccount.type or proxyaccount.expired_date is None:
            return HttpResponse("accout_type_error")
        else:
            print("success:",account_type," month",month)
            today = datetime.date.today()
            print("add month")
            if proxyaccount.expired_date < today:
                expired_date = today + datetime.timedelta(30*int(month))
            else:
                expired_date = proxyaccount.expired_date + datetime.timedelta(30*int(month))
            proxyaccount.expired_date = expired_date
    elif pay_type == 3:
        upgrade_delta = (real_fee/month)*30
        upgrade_delta = int(upgrade_delta+0.1)
        print(upgrade_delta)
        proxyaccount.type += upgrade_delta
        if proxyaccount.type not in {1,5,10,20,50}:
            return HttpResponse("accout_type_error")
    else:
        return HttpResponse("fail")
    print("sava proxyaccount")
    proxyaccount.save()
    return HttpResponseRedirect('/homepage')
