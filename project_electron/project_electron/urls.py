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
from transfer_app.views import MainView

urlpatterns = [
    url(r'^admin/',             admin.site.urls),
    url(r'^app/$',              MainView.as_view(), name='app_home'),
    url(r'^app/transfers/',     include('transfer_app.urls')),
    url(r'^app/orgs/',          include('orgs.urls')),
    url(r'^app/users/',         include('orgs.user_urls')),
    url(r'^app/password/',      include('rac_user.urls')),
    url(r'^app/accession/',     include('orgs.accession.urls')),
    url(r'^app/appraise/',      include('orgs.appraise.urls')),
    url(r'^app/rights/',        include('orgs.rights.urls')),
    url(r'^$',                  SplashView.as_view()),
    url(r'^login/$',            auth_views.login, {'template_name': 'rac_user/login.html'}, name='login'),
    url(r'^logout/$',           auth_views.logout, {'next_page': '/login'}, name='logout'),
    url(r'^api/',               include('orgs.api.urls')),
]
