from django.conf.urls import url
from bag_transfer.users.views import *

urlpatterns = [

    url(r'^$', UsersListView.as_view(), name='users-list'),
    url(r'^(?P<pk>\d+)/$', UsersDetailView.as_view(), name='users-detail'),
    url(r'^(?P<pk>\d+)/add/$', UsersCreateView.as_view(), name='users-add'),
    url(r'^(?P<pk>\d+)/edit/$', UsersEditView.as_view(), name='users-edit'),
    url(r'^change-password/$', UserPasswordChangeView.as_view(), name='password-change'),
    url(r'^password/reset$', UserPasswordResetView.as_view(), name='password-reset'),
    url(r'^password/reset/done$', UserPasswordResetDoneView.as_view(), name='password-reset-done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$', UserPasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    url(r'^password/reset/complete$', UserPasswordResetCompleteView.as_view(), name='password-reset-complete'),

]
