from django.conf.urls import url,include
from orgs.views import *

urlpatterns = [

    url(r'^add/$', OrganizationCreateView.as_view(), name='orgs-add'),
    url(r'^(?P<pk>\d+)/$', OrganizationDetailView.as_view(), name='orgs-detail'),
    url(r'^$', 	OrganizationListView.as_view(), name='orgs-list'),
    url(r'^(?P<pk>\d+)/edit/$', OrganizationEditView.as_view(), name='orgs-edit'),
    url(r'^(?P<pk>\d+)/transfers/$', OrganizationTransfersView.as_view(), name='orgs-transfers-report'),
    url(r'^(?P<pk>\d+)/transfers/csv/$', OrganizationTransferDataView.as_view(), name='orgs-transfer-data'),
    url(r'^(?P<pk>\d+)/bagit_profiles/add/$', BagItProfileManageView.as_view(), name='bagit-profiles-add'),
    url(r'^(?P<pk>\d+)/bagit_profiles/(?P<profile_pk>\d+)/edit$', BagItProfileManageView.as_view(), name='bagit-profiles-edit'),
    url(r'^(?P<pk>\d+)/bagit_profiles/(?P<profile_pk>\d+)/(?P<action>(delete))/$', BagItProfileAPIAdminView.as_view(), name='bagit-profiles-api'),
    url(r'^(?P<pk>\d+)/bagit_profiles/(?P<profile_pk>\d+).json$', BagItProfileJSONView.as_view(), name='bagit-profiles-json'),
]
