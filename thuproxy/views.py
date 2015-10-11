from django.http import HttpResponse, HttpResponseRedirect
import datetime
from django.shortcuts import render_to_response, RequestContext
from thuproxy.models import *
from django.contrib import auth
from django.contrib.auth.decorators import login_required

__author__ = 'lz'


def index(request):
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))


def register(request):
    errors = []
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

                proxyaccount = ProxyAccount(type=0, month=0, port=0)
                proxyaccount.save()
                duser.save()
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
    if request.method == 'POST':
        if request.POST['username'] and request.POST['password']:
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                request.session['user_id'] = user.id
                return HttpResponseRedirect('/homepage/')
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))


@login_required(login_url="/login/")
def homepage(request):
    return render_to_response('homepage.html', locals(), context_instance=RequestContext(request))


@login_required
def user_logout(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass
    auth.logout(request)
    return HttpResponseRedirect('/')

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