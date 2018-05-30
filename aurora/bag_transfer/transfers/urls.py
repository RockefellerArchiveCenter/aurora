from django.conf.urls import url
from bag_transfer.transfers.views import *

urlpatterns = [
    url(r'^$', TransfersView.as_view(), name='transfers'),
    url(r'^csv/$', TransferDataView.as_view(), name='transfer-data'),
    url(r'^(?P<pk>\d+)$', TransferDetailView.as_view(), name='transfer-detail'),
]
