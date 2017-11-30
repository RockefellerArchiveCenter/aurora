from django.conf.urls import url,include
from orgs.views import *

urlpatterns = [

    url(r'^add/$', RightsCreateView.as_view(), name='rights-add'),
    url(r'^(?P<pk>\d+)/$', RightsDetailView.as_view(), name='rights-detail'),
    url(r'^(?P<pk>\d+)/edit$', RightsUpdateView.as_view(), name='rights-update'),
    url(r'^(?P<pk>\d+)/delete$', RightsDeleteView.as_view(), name='rights-delete'),

]
