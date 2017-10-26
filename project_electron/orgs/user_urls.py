from django.conf.urls import url
from orgs.views import *
from rac_user.views import *

urlpatterns = [

    url(r'^$', UsersListView.as_view(), name='users-list'),
    url(r'^add/$', UsersCreateView.as_view(), name='users-add'),
    url(r'^(?P<pk>\d+)/$', UsersDetailView.as_view(), name='users-detail'),
    url(r'^(?P<pk>\d+)/edit/$', UsersEditView.as_view(), name='users-edit'),
    url(r'^(?P<pk>\d+)/transfers/$', UsersTransfersView.as_view(), name='users-transfers-report'),

    # url(r'^password/reset$', PasswordResetView.as_view(), name='password-reset'),
    # url(r'^password/reset/done$', PasswordResetDoneView.as_view(), name='password-reset-done'),
    # url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    # url(r'^password/reset/complete$', PasswordResetCompleteView.as_view(), name='password-reset-complete'),
    url(r'^(?P<pk>\d+)/password/change$', UserPasswordChangeView.as_view(), name='password-change'),

]
