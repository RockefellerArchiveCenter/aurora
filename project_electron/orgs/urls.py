from django.conf.urls import url,include
from orgs.views import *

urlpatterns = [

    url(r'^add/$', OrganizationCreateView.as_view(), name='orgs-add'),
    url(r'^(?P<pk>\d+)/$', OrganizationDetailView.as_view(), name='orgs-detail'),
    url(r'^$', 	OrganizationListView.as_view(), name='orgs-list'),
    url(r'^(?P<pk>\d+)/edit/$', OrganizationEditView.as_view(), name='orgs-edit'),
    url(r'^(?P<pk>\d+)/transfers/$', OrganizationTransfersView.as_view(), name='orgs-transfers-report'),
    url(r'^(?P<pk>\d+)/rights/', include('orgs.rights_urls')),

]
