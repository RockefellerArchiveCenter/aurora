from django.conf.urls import url
from orgs.views import *
from orgs.gviews import *

urlpatterns = [

    url(r'^transfers/(?P<pk>\d+)$', TransferDetailView.as_view(), name='transfer-detail'),

    url(r'^transfers/$', OrgTransfersView.as_view(), name='org-transfers'),
    url(r'^my-transfers/$', MyTransfersView.as_view(), name='org-my-transfers'),
]
