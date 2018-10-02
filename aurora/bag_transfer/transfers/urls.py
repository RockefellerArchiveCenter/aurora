from django.conf.urls import url
from bag_transfer.transfers.views import *

urlpatterns = [
    url(r'^$', TransfersView.as_view(), name='list'),
    url(r'^csv/$', TransferDataView.as_view(), name='data'),
    url(r'^datatable/$', TransferDataTableView.as_view(), name='datatable'),
    url(r'^(?P<pk>\d+)$', TransferDetailView.as_view(), name='detail'),
]
