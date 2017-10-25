from django.conf.urls import url
from transfer_app.views import MainView
from orgs.views import *
from orgs.gviews import *
from rac_user.views import *

urlpatterns = [
    url(r'^$', 	MainView.as_view(), name='app_home'),

    url(r'^orgs/add/$', OrganizationCreateView.as_view(), name='orgs-add'),
    url(r'^orgs/(?P<pk>\d+)/$', OrganizationDetailView.as_view(), name='orgs-detail'),
    url(r'^orgs/$', 	OrganizationListView.as_view(), name='orgs-list'),
    url(r'^orgs/(?P<pk>\d+)/edit/$', OrganizationEditView.as_view(), name='orgs-edit'),
    url(r'^orgs/(?P<pk>\d+)/transfers/$', OrganizationTransfersView.as_view(), name='orgs-transfers-report'),

    url(r'^users/$', UsersListView.as_view(), name='users-list'),
    url(r'^users/by/(?P<page_type>(unassigned|company))/$', UsersListView.as_view(), name='users-list-by'),
    url(r'^users/(?P<pk>\d+)/$', UsersDetailView.as_view(), name='users-detail'),
    url(r'^users/(?P<pk>\d+)/edit/$', UsersEditView.as_view(), name='users-edit'),

    url(r'^password/reset$', PasswordResetView.as_view(), name='password-reset'),
    url(r'^users/(?P<pk>\d+)/password/change$', UserPasswordChangeView.as_view(), name='password-change'),

    url(r'^transfers/(?P<pk>\d+)$', TransferDetailView.as_view(), name='transfer-detail'),

    url(r'^transfers/$', OrgTransfersView.as_view(), name='org-transfers'),
    url(r'^my-transfers/$', MyTransfersView.as_view(), name='org-my-transfers'),
]
