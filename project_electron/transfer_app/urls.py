from django.conf.urls import url
from transfer_app.views import MainView
from orgs.views import *

urlpatterns = [
    url(r'^$', 	MainView.as_view(), name='app_home'),

    url(r'^orgs/add/$', OrganizationCreateView.as_view(), name='orgs-add'),
    url(r'^orgs/(?P<pk>\d+)/$', OrganizationDetailView.as_view(), name='orgs-detail'),
    url(r'^orgs/$', 	OrganizationListView.as_view(), name='orgs-list'),
    url(r'^orgs/(?P<pk>\d+)/edit/$', OrganizationEditView.as_view(), name='orgs-edit'),

    url(r'^users/$', UsersListView.as_view(), name='users-list'),
    url(r'^users/add/$', UsersCreateView.as_view(), name='users-add'),
    url(r'^users/(?P<pk>\d+)/$', UsersEditView.as_view(), name='users-edit'),
]
