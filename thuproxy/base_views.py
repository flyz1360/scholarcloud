#coding=utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from thuproxy.models import *
from django.contrib.auth.decorators import login_required
import datetime

__author__ = 'lz'


def index(request):
    userLoginSuccess = request.user.is_authenticated()
    if userLoginSuccess is True:
        user = request.user
    else:
        user = None
    if 'username' in request.session:
        username = request.session['username']
    else:
        username = ''
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

