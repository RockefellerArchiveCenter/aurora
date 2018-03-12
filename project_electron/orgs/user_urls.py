from django.conf.urls import url
from orgs.views import *

urlpatterns = [

    url(r'^$', UsersListView.as_view(), name='users-list'),
    url(r'^(?P<pk>\d+)/$', UsersDetailView.as_view(), name='users-detail'),
    url(r'^(?P<pk>\d+)/add/$', UsersCreateView.as_view(), name='users-add'),
    url(r'^(?P<pk>\d+)/edit/$', UsersEditView.as_view(), name='users-edit'),
    url(r'^change-password/$', UserPasswordChangeView.as_view(), name='password-change'),

]
