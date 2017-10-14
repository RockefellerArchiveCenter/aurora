from django.conf.urls import url
from orgs.views import *
from transfer_app.views import *

urlpatterns = [
    url(r'^$', RecentTransfersView.as_view(), name='org-transfers'),
    url(r'^(?P<pk>\d+)$', TransferDetailView.as_view(), name='transfer-detail'),
]
