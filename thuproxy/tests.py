#coding=utf-8
import socket
import os

# try:
#     address = ('166.111.80.96', 4127)
#     socket.setdefaulttimeout(20)
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.connect(address)
#     data = 'addport@'+'10003'+'\n'
#     sock.send(data.encode())
#     sock.close()
# except socket.error as e:
#     print(e)

pac_file_folder = './test/'
files = os.listdir(pac_file_folder)
for fs in files:
    f = open(pac_file_folder+fs, "r+")
    d = f.read()
    d = d.replace('"1-apple.com.tw"', '"1-apple.com.tw","tcfbank.com"')
    f.close()
    w = open(pac_file_folder+fs, 'w+')
    w.write(d)
    w.close()

# def alipay_test(request):
#     pay_type = int(request.POST['pay_type'])
#     month = int(request.POST['month'])
#     total_fee = float(request.POST['money'])
#     total_fee /= 100
#     proxyaccount = ProxyAccount.objects.get(user=request.user)
#     if float(total_fee) == 0.10:
#         real_fee = float(total_fee) * 10
#     else:
#         real_fee = float(total_fee*100)
#     print ('realfee',real_fee)
#
#     if pay_type == 1:
#         account_type = int(real_fee)/int(month)
#         print("accounttype", account_type)
#         if account_type not in {1,5,10,20,50}:
#             return HttpResponse("accout_type_error")
#         else:
#             print("success:",account_type," month",month)
#             proxyaccount.type = account_type
#             today = datetime.datetime.now()
#             if proxyaccount.expired_date is not None:
#                 print("add month")
#                 return HttpResponse("not init")
#             else:
#                 print("init month")
#                 expired_date = today + datetime.timedelta(30*int(month))
#             if proxyaccount.paydate is None:
#                 print("init paydate")
#                 create_pac(proxyaccount)
#                 print ("create_pac done")
#                 open_listen_port(proxyaccount.port)
#                 print ("open_listen_port done")
#                 proxyaccount.paydate = today
#             proxyaccount.expired_date = expired_date
#     elif pay_type == 2:
#         account_type = int(real_fee)/int(month)
#         print("accounttype", account_type)
#         if account_type != proxyaccount.type or proxyaccount.expired_date is None:
#             return HttpResponse("accout_type_error")
#         else:
#             print("success:",account_type," month",month)
#             today = datetime.date.today()
#             print("add month")
#             if proxyaccount.expired_date < today:
#                 expired_date = today + datetime.timedelta(30*int(month))
#             else:
#                 expired_date = proxyaccount.expired_date + datetime.timedelta(30*int(month))
#             proxyaccount.expired_date = expired_date
#     elif pay_type == 3:
#         upgrade_delta = (real_fee/month)*30
#         upgrade_delta = int(upgrade_delta+0.1)
#         print(upgrade_delta)
#         proxyaccount.type += upgrade_delta
#         if proxyaccount.type not in {1,5,10,20,50}:
#             return HttpResponse("accout_type_error")
#     else:
#         return HttpResponse("fail")
#     print("sava proxyaccount")
#     proxyaccount.save()
#     return HttpResponseRedirect('/homepage')

