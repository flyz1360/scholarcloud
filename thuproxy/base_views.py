#coding=utf-8
from django.shortcuts import render_to_response, RequestContext


def index(request):
    is_user_login = request.user.is_authenticated()
    if is_user_login is True:
        user = request.user
    else:
        user = None
    if 'username' in request.session:
        username = request.session['username']
    else:
        username = ''
    page_name = "index"
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))


def guide(request):
    is_user_login = request.user.is_authenticated()
    user = request.user
    page_name = "guide"
    return render_to_response('guide.html', locals(), context_instance=RequestContext(request))


def account_types(request):
    is_user_login = request.user.is_authenticated()
    user = request.user
    page_name = "account_types"
    return render_to_response('account_types.html', locals(), context_instance=RequestContext(request))

