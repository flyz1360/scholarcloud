from django.http import HttpResponse, HttpResponseRedirect
import datetime
from django.shortcuts import render_to_response, RequestContext
from thuproxy.models import *

__author__ = 'lz'


def hello(request):
    now = datetime.datetime.now()
    html = "<html><body>it is now %s.</body></html>" % now
    return HttpResponse(html)


def homepage(request):
    return render_to_response('index.html')


def register(request):
    errors = []
    if request.method == 'POST':
        if not request.POST.get('username', ''):
            errors.append('Enter a username.')
        if not request.POST.get('password', ''):
            errors.append('Enter a password.')
        if request.POST.get('email') and '@' not in request.POST['email']:
            errors.append('Enter a valid e-mail address.')
        if not errors:
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            email = request.POST.get('email', '')

            proxyaccount = ProxyAccount(username=username,
                                        type=0,
                                        month=0,
                                        port=0,)
            proxyaccount.save()

            user = User(username=username,
                        password=password,
                        email=email,
                        )
            user.save()
            return HttpResponseRedirect('/')
    return render_to_response('register.html', {
        'errors': errors,
        'username': request.POST.get('username', ''),
        'password': request.POST.get('password', ''),
        'email': request.POST.get('email', ''),
    },
     context_instance=RequestContext(request))


def login(request):
    if request.method == 'GET':
        if request.GET['username'] and request.GET['password']:
            username = request.GET['username']
            password = request.GET['password']

            user = User.objects.get(username=username)
            proxyaccount = ProxyAccount.objects.get(username=username)
            if user.password == password:
                return render_to_response('homepage.html', locals())
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
def contact(request):
    errors = []
    if request.method == 'POST':
        if not request.POST.get('subject', ''):
            errors.append('Enter a subject.')
        if not request.POST.get('message', ''):
            errors.append('Enter a message.')
        if request.POST.get('email') and '@' not in request.POST['email']:
            errors.append('Enter a valid e-mail address.')
        if not errors:

            return HttpResponseRedirect('/contact/thanks/')
    return render_to_response('contact_form.html', {
        'errors': errors,
        'subject': request.POST.get('subject', ''),
        'message': request.POST.get('message', ''),
        'email': request.POST.get('email', ''),
    },
     context_instance=RequestContext(request))
