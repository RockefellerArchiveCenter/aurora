from django.conf.urls import url
from rac_user.views import *

urlpatterns = [

    url(r'^reset$', UserPasswordResetView.as_view(), name='password-reset'),
    url(r'^reset/done$', UserPasswordResetDoneView.as_view(), name='password-reset-done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$', UserPasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    url(r'^reset/complete$', UserPasswordResetCompleteView.as_view(), name='password-reset-complete'),

]
