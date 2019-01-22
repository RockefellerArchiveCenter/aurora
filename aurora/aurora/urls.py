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
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from bag_transfer.users.views import SplashView
from bag_transfer.users.form import UserPasswordResetForm, UserPasswordResetConfirmForm
from django.contrib.auth import views as auth_views
from bag_transfer.transfers.views import MainView

urlpatterns = [
    url(r'^admin/',             admin.site.urls),
    url(r'^app/$',              MainView.as_view(), name='app_home'),
    url(r'^app/transfers/',     include('bag_transfer.transfers.urls', namespace='transfers')),
    url(r'^app/orgs/',          include('bag_transfer.orgs.urls', namespace='orgs')),
    url(r'^app/users/',         include('bag_transfer.users.urls', namespace='users')),
    url(r'^reset-password/$', auth_views.password_reset,
        {'password_reset_form': UserPasswordResetForm,
         'template_name': 'users/password_reset_form.html',
         'email_template_name': 'users/password_reset_email.html',
         'html_email_template_name': 'users/password_reset_email.html',
         'subject_template_name': 'users/password_reset_subject.txt'},
        name='password-reset'),
    url(r'^reset-password/done/$', auth_views.password_reset_done,
        {'template_name': 'users/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'password_reset_confirm_form': UserPasswordResetConfirmForm,
         'template_name': 'users/password_reset_confirm.html'},
        name='password-reset-confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete,
        {'template_name': 'users/password_reset_complete.html'},
        name='password-reset-complete'),
    url(r'^app/accession/',     include('bag_transfer.accession.urls', namespace='accession')),
    url(r'^app/appraise/',      include('bag_transfer.appraise.urls', namespace='appraise')),
    url(r'^app/rights/',        include('bag_transfer.rights.urls', namespace='rights')),
    url(r'^$',                  SplashView.as_view()),
    url(r'^login/$',            auth_views.login, {'template_name': 'users/login.html'}, name='login'),
    url(r'^logout/$',           auth_views.logout, {'next_page': '/login'}, name='logout'),
    url(r'^api/',               include('bag_transfer.api.urls')),
]
