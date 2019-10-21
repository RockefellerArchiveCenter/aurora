from django.conf.urls import url
from bag_transfer.accession.views import *

urlpatterns = [
    url(r'^$', 	AccessionView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', AccessionDetailView.as_view(), name='detail'),
    url(r'^add/', AccessionCreateView.as_view(), name='add'),
    url(r'^saved-datatable/$', SavedAccessionsDatatableView.as_view(), name='saved-datatable'),
]
