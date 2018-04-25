"""Aurora URL Configuration

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
from bag_transfer.users.views import SplashView
from django.contrib.auth import views as auth_views
from bag_transfer.transfers.views import MainView

urlpatterns = [
    url(r'^admin/',             admin.site.urls),
    url(r'^app/$',              MainView.as_view(), name='app_home'),
    url(r'^app/transfers/',     include('bag_transfer.transfers.urls')),
    url(r'^app/orgs/',          include('bag_transfer.orgs.urls')),
    url(r'^app/users/',         include('bag_transfer.users.urls')),
    url(r'^app/accession/',     include('bag_transfer.accession.urls')),
    url(r'^app/appraise/',      include('bag_transfer.appraise.urls')),
    url(r'^app/rights/',        include('bag_transfer.rights.urls')),
    url(r'^$',                  SplashView.as_view()),
    url(r'^login/$',            auth_views.login, {'template_name': 'users/login.html'}, name='login'),
    url(r'^logout/$',           auth_views.logout, {'next_page': '/login'}, name='logout'),
    url(r'^api/',               include('bag_transfer.api.urls')),
]
