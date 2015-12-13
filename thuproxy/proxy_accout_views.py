#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.contrib.auth.decorators import login_required

def create_pac(request):
    template_pac = open("/static/myproxy.pac", "r+")
    d = template_pac.read()
    d = d.replace("4128", "new")
    user_pac = open('re.txt', 'w+')
    user_pac.write(d)
    user_pac.close()
