from django.conf.urls import url
from orgs.accession.views import *

urlpatterns = [
    url(r'^$', 	AccessionView.as_view(), name='accession-main'),
    url(r'^add/', 	AccessionRecordView.as_view(), name='accession-record'),
]
