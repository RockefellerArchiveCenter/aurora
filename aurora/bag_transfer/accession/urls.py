from django.conf.urls import url
from bag_transfer.accession.views import *

urlpatterns = [
    url(r'^$', 	AccessionView.as_view(), name='list'),
    url(r'^add/', AccessionRecordView.as_view(), name='detail'),
    url(r'^saved-datatable/$', SavedAccessionsDatatableView.as_view(), name='saved-datatable'),
]
