from django.conf.urls import url,include
from rights.views import *

urlpatterns = [

    url(r'^add/$', RightsManageView.as_view(), name='rights-add'),
    url(r'^grants/(?P<pk>\d+)/$', RightsGrantsManageView.as_view(), name='rights-grants'),
    url(r'^(?P<rights_pk>\d+)/$', RightsDetailView.as_view(), name='rights-detail'),
    url(r'^(?P<pk>\d+)/edit$', RightsManageView.as_view(), name='rights-update'),
    url(r'^(?P<pk>\d+)/(?P<action>(delete))/$', RightsAPIAdminView.as_view(), name='rights-api'),

]
