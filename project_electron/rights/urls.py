from django.conf.urls import url,include
from rights.views import *

urlpatterns = [

    url(r'^add/$', RightsCreateView.as_view(), name='rights-add'),
    url(r'^grants/(?P<rights_pk>\d+)/$', RightsGrantsCreateView.as_view(), name='rights-grants'),
    url(r'^(?P<rights_pk>\d+)/$', RightsDetailView.as_view(), name='rights-detail'),
    url(r'^(?P<rights_pk>\d+)/edit$', RightsUpdateView.as_view(), name='rights-update'),
    url(r'^(?P<rights_pk>\d+)/delete$', RightsDeleteView.as_view(), name='rights-delete'),

]
