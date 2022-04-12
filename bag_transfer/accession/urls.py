from django.urls import re_path

from bag_transfer.accession.views import (AccessionCreateView,
                                          AccessionDetailView, AccessionView,
                                          SavedAccessionsDatatableView)

app_name = 'accessions'

urlpatterns = [
    re_path(r"^$", AccessionView.as_view(), name="list"),
    re_path(r"^(?P<pk>\d+)/$", AccessionDetailView.as_view(), name="detail"),
    re_path(r"^add/", AccessionCreateView.as_view(), name="add"),
    re_path(
        r"^saved-datatable/$",
        SavedAccessionsDatatableView.as_view(),
        name="saved-datatable",
    ),
]
