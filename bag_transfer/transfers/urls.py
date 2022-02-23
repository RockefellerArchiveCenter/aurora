from django.urls import re_path

from bag_transfer.transfers.views import (TransferDataTableView,
                                          TransferDataView, TransferDetailView,
                                          TransfersView)

app_name = "transfers"

urlpatterns = [
    re_path(r"^$", TransfersView.as_view(), name="list"),
    re_path(r"^csv/$", TransferDataView.as_view(), name="data"),
    re_path(r"^datatable/$", TransferDataTableView.as_view(), name="datatable"),
    re_path(r"^(?P<pk>\d+)$", TransferDetailView.as_view(), name="detail"),
]
