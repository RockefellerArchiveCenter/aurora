"""project_electron URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from rac_user.views import SplashView
from django.contrib.auth import views as auth_views
from appraise.views import AppraiseView
from accession.views import *

urlpatterns = [
    url(r'^admin/', 	admin.site.urls),
    url(r'^app/', 		include('transfer_app.urls')),
    url(r'^$',			SplashView.as_view()),
    url(r'^login/$',	auth_views.login, {'template_name': 'rac_user/login.html'}, name='login'),
    url(r'^logout/$', 	auth_views.logout, {'next_page': '/login'}, name='logout'),
]

urlpatterns += [
    url(r'^appraise/', 	AppraiseView.as_view(), name='appraise-main'),

]

urlpatterns += [
    url(r'^accession/', 	AccessionView.as_view(), name='accession-main'),
    url(r'^accession_record/', 	AccessionRecordView.as_view(), name='accession-record'),

]
