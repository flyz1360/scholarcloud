"""djangowebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import *
from django.contrib import admin


urlpatterns = patterns('thuproxy.base_views',
                       ('^$', 'index'),
                       ('^show_login/$', 'show_login'),
                       ('^guide/$', 'guide'),
                       ('^account_types/$', 'account_types'),
                       (r'^admin/', include(admin.site.urls)))

urlpatterns += patterns('thuproxy.user_views',
                        ('^register/$', 'register'),
                        ('^login/$', 'login'),
                        ('^logout/$', 'user_logout'),
                        ('^validateUserName/$', 'validate_username')
                        )

urlpatterns += patterns('thuproxy.pay_views',
                        (r'^alipay/apply/(.+)$', 'alipay_apply'),
                        (r'^alipay/submit$', 'alipay_create_orders'),
                        # (r'^alipay/submit$', 'alipay_test'),
                        (r'^alipay/repay/(.+)$', 'alipay_repay_orders'),
                        (r'^alipay/callback$', 'alipay_callback'),
                        (r'^alipay/success$', 'alipay_success'),
                        (r'^alipay/cancel/(.+)$', 'alipay_cancel')
                        )

urlpatterns += patterns('thuproxy.proxy_account_views',
                        (r'^homepage/$', 'homepage'),
                        (r'^ip_history/$', 'ip_history'),
                        (r'^flow_history/$', 'show_flows'),
                        ('^getFlow_json/$', 'get_flow_json'),
                        (r'^script_lz/(.+)/$', 'script_lz'),
                        (r'^orders/$', 'show_orders'),
                        (r'^account/downgrade$', 'downgrade'),
                        )
