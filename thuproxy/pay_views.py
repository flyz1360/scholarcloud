#coding=utf-8
from thuproxy.alipay_api import *
from thuproxy.proxy_account_views import *
import datetime
import uuid
import urllib.request
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext

# 优惠比率
RATE = 0.6


# 根据支付类型选择策略
@login_required(login_url="/login/")
def alipay_apply(request, pay_type):
    is_user_login = request.user.is_authenticated()
    user = request.user
    proxy_account = ProxyAccount.objects.get(user=request.user)
    pay_list = Pay.objects.filter(user_id=user.id, status='U')
    if len(pay_list) != 0:
        request.session["error"] = "need_repay"
        return HttpResponseRedirect('/homepage')
    # 判断支付类型
    if pay_type == 'first':
        if proxy_account.expired_date is not None:
            request.session["error"] = "first_pay"
            return HttpResponseRedirect('/homepage')
        return render_to_response('alipay_create_order_first.html', locals(), context_instance=RequestContext(request))
    elif pay_type == 'upgrade':
        if proxy_account.type == 50:
            request.session["error"] = "upgrade"
            return HttpResponseRedirect('/homepage')
        if datetime.datetime.now().date() < proxy_account.expired_date:
            remain_time = proxy_account.expired_date - datetime.datetime.now().date()
            proxy_account.remain_time = int(remain_time.days)
        elif datetime.datetime.now().date() >= proxy_account.expired_date:
            request.session["error"] = "date"
            return HttpResponseRedirect('/homepage')
        return render_to_response('alipay_create_order_upgrade.html', locals(),
                                  context_instance=RequestContext(request))
    elif pay_type == 'downgrade':
        if proxy_account.type == 1:
            request.session["error"] = "downgrade"
            return HttpResponseRedirect('/homepage')
        remain_time = proxy_account.expired_date - datetime.datetime.now().date()
        proxy_account.remain_time = int(remain_time.days)
        return render_to_response('alipay_create_order_downgrade.html', locals(),
                                  context_instance=RequestContext(request))
    elif pay_type == 'continue':
        return render_to_response('alipay_create_order_continue.html', locals(),
                                  context_instance=RequestContext(request))
    else:
        return HttpResponse('充值请求错误')


# 生成订单
@login_required(login_url="/login/")
def alipay_create_orders(request):
    is_user_login = request.user.is_authenticated()
    user = request.user
    proxy_account = ProxyAccount.objects.get(user=request.user)
    m = request.POST['money']
    money = float(m) * RATE
    money = round(money, 2)
    pay_type = int(request.POST['pay_type'])
    today = timezone.now()
    try:
        # 升级的情况下，需要记录的是账号剩余天数而非需要付费的月数
        if pay_type == 3:
            day = request.POST['day']
            pay = Pay(out_trade_no=uuid.uuid1().hex, user=user, total_fee=money, type=int(pay_type),
                      month=int(day), status='U', create_date=today)
        else:
            month = request.POST['month']
            pay = Pay(out_trade_no=uuid.uuid1().hex, user=user, total_fee=money, type=int(pay_type),
                      month=int(month), status='U', create_date=today)

        pay.save()
        params = {'out_trade_no': pay.out_trade_no, 'subject': u'清云加速',
                  'body': u'流量购买费用', 'total_fee': str(money)}
        total_fee = pay.total_fee
        alipay = Alipay(notifyurl="http://scholar.thucloud.com/alipay/callback",
                        returnurl="http://scholar.thucloud.com/alipay/success",
                        showurl="http://scholar.thucloud.com/alipay/success")
        params.update(alipay.conf)
        sign = alipay.buildSign(params)
        return render_to_response('alipay_show_order.html', locals())
    except Exception as e:
        print(e)
        return HttpResponse('生成订单错误')


# 生成需要重新支付的订单
@login_required(login_url="/login/")
def alipay_repay_orders(request, pay_no):
    is_user_login = request.user.is_authenticated()
    user = request.user
    proxy_account = ProxyAccount.objects.get(user=request.user)
    try:
        pay_list = Pay.objects.filter(out_trade_no=pay_no)
        if len(pay_list) != 1:
            request.session["error"] = "repay"
            return HttpResponseRedirect('/homepage')
        else:
            pay = pay_list[0]
            params = {'out_trade_no': pay.out_trade_no, 'subject': u'清云加速',
                      'body': u'流量购买费用', 'total_fee': str(pay.total_fee)}
            total_fee = pay.total_fee
            alipay = Alipay(notifyurl="http://scholar.thucloud.com/alipay/callback",
                            returnurl="http://scholar.thucloud.com/alipay/success",
                            showurl="http://scholar.thucloud.com/alipay/success")
            params.update(alipay.conf)
            sign = alipay.buildSign(params)
            money = pay.total_fee
            return render_to_response('alipay_show_order.html', locals())
    except Exception as e:
        print(e)
        return HttpResponse('显示订单错误')


@csrf_exempt
def alipay_callback(request):
    try:
        print(datetime.datetime.now())
        print("call back start")
        params = request.POST.dict()
        if not isinstance(params, dict):
            print('error params not dict')
        alipay = Alipay()

        # 判断是否为有效返回
        sign = None
        if 'sign' in params:
            sign = params['sign']
        loc_sign = alipay.buildSign(params)
        if sign is None or loc_sign != sign:
            return HttpResponse("fail")
        print("sign is ok")

        # 判断交易状态是否有效，以免重复判断交易成功
        if params['trade_status'] != 'TRADE_FINISHED' and params['trade_status'] != 'TRADE_SUCCESS':
            print('trade status error')
            return HttpResponse("fail")
        else:
            print("trade status ok")
            print("url: ")
            url = verifyURL['https'] + "&partner=%s&notify_id=%s" % (alipay.conf['partner'], params['notify_id'])
            print(url)
            response = urllib.request.urlopen(url)
            html = response.read()
            print("aliypay.com return: %s" % html)

            # 支付宝返回有效信息
            if html == b'true':
                print('result is true')
                try:
                    out_trade_no = params['out_trade_no']
                    print('out trade no ', out_trade_no)
                    trade_no = params['trade_no']
                    print('trade no ', trade_no)
                    total_fee = params['total_fee']
                    pay = Pay.objects.get(out_trade_no=out_trade_no)

                    # todo: handle other error status
                    if pay is None:
                        return HttpResponse("无此订单，请重新下单")
                    if pay.status == 'S':
                        return HttpResponse("已经成功支付了")

                    print('user', pay.user)
                    proxy_account = ProxyAccount.objects.get(user=pay.user)
                    print('proxy_account', proxy_account)
                    print('pay total fee', pay.total_fee)

                    month = pay.month
                    pay_type = pay.type
                    real_fee = float(total_fee) / RATE
                    print('month', month)
                    print('pay type', pay_type)
                    print('real fee', real_fee)

                    # 初次缴费
                    if pay_type == 1:
                        account_type = int(real_fee)/int(month)
                        print("accounttype", account_type)
                        if account_type not in {1, 5, 10, 20, 50}:
                            return HttpResponse("accout_type_error")
                        else:
                            print("success:", account_type, " month", month)
                            proxy_account.type = account_type
                            today = datetime.datetime.now()
                            if proxy_account.expired_date is not None:
                                return HttpResponse("not init")
                            else:
                                print("init date")
                                expired_date = today + datetime.timedelta(30*int(month))
                            if proxy_account.paydate is None:
                                create_pac(proxy_account)
                                print("create_pac done")
                                open_listen_port(proxy_account.port, proxy_account.type)
                                print("open_listen_port done")
                                proxy_account.paydate = today
                            proxy_account.expired_date = expired_date
                    elif pay_type == 2:  # 续费
                        account_type = int(real_fee)/int(month)
                        print("accounttype", account_type)
                        if account_type != proxy_account.type or proxy_account.expired_date is None:
                            return HttpResponse("accout_type_error")
                        else:
                            print("success:", account_type, " month", month)
                            today = datetime.date.today()
                            print("add month")
                            if proxy_account.expired_date < today:  # 欠费啦
                                expired_date = today + datetime.timedelta(30*int(month))
                                reopen_port(proxy_account.port)
                            else:
                                expired_date = proxy_account.expired_date + datetime.timedelta(30*int(month))
                            proxy_account.expired_date = expired_date
                    elif pay_type == 3:  # 升级
                        today = datetime.date.today()
                        if proxy_account.expired_date < today:  # 欠费啦
                            return HttpResponse("fail")
                        upgrade_delta = (real_fee/month)*30
                        upgrade_delta = int(upgrade_delta+0.1)
                        print(upgrade_delta)
                        proxy_account.type += upgrade_delta
                        if proxy_account.type not in {1, 5, 10, 20, 50}:
                            return HttpResponse("accout_type_error")
                        if ACCOUNT_TRAFFIC_LIMIT[int(proxy_account.type)] > proxy_account.traffic:
                            reopen_port(proxy_account.port)
                        # 修改带宽和流量
                        upgrade_port(proxy_account.port, proxy_account.type)
                    else:
                        pay.status = 'F'
                        pay.save()
                        return HttpResponse("fail")

                    print("sava pay")
                    pay.status = 'S'
                    pay.trade_no = trade_no
                    pay.total_fee = real_fee
                    pay.save()
                    print("sava proxy_account")
                    proxy_account.save()

                    return HttpResponse("success")
                except Exception as e:
                    print(e)
        return HttpResponse("fail")
    except Exception as e:
        return HttpResponse("fail")
        print(e)


@login_required(login_url="/login/")
def alipay_success(request):
    is_user_login = request.user.is_authenticated()
    proxy_account = ProxyAccount.objects.get(user=request.user)
    return render_to_response('alipay_success.html', locals(), context_instance=RequestContext(request))


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
    total_fee *= RATE
    proxy_account = ProxyAccount.objects.get(user=request.user)
    real_fee = float(total_fee/RATE)
    print('realfee', real_fee)

    if pay_type == 1:
        account_type = int(real_fee)/int(month)
        print("accounttype", account_type)
        if account_type not in {1, 5, 10, 20, 50}:
            return HttpResponse("accout_type_error")
        else:
            print("success:", account_type, " month", month)
            proxy_account.type = account_type
            today = datetime.datetime.now()
            if proxy_account.expired_date is not None:
                print("add month")
                return HttpResponse("not init")
            else:
                print("init month")
                expired_date = today + datetime.timedelta(30*int(month))
            if proxy_account.paydate is None:
                print("init paydate")
                create_pac(proxy_account)
                print("create_pac done")
                open_listen_port(proxy_account.port, proxy_account.type)
                print("open_listen_port done")
                proxy_account.paydate = today
            proxy_account.expired_date = expired_date
    elif pay_type == 2:
        account_type = int(real_fee)/int(month)
        print("accounttype", account_type)
        if account_type != proxy_account.type or proxy_account.expired_date is None:
            return HttpResponse("accout_type_error")
        else:
            print("success:", account_type, " month", month)
            today = datetime.date.today()
            print("add month")
            if proxy_account.expired_date < today:
                expired_date = today + datetime.timedelta(30*int(month))
            else:
                expired_date = proxy_account.expired_date + datetime.timedelta(30*int(month))
            proxy_account.expired_date = expired_date
    elif pay_type == 3:
        upgrade_delta = (real_fee/month)*30
        upgrade_delta = int(upgrade_delta+0.1)
        print(upgrade_delta)
        proxy_account.type += upgrade_delta
        if proxy_account.type not in {1, 5, 10, 20, 50}:
            return HttpResponse("accout_type_error")
        reopen_port(proxy_account.port)
    else:
        return HttpResponse("fail")
    print("sava proxy_account")
    proxy_account.save()
    return HttpResponseRedirect('/homepage')
