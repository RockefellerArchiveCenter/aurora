from django.conf.urls import url, include
from bag_transfer.rights.views import (
    RightsAPIAdminView,
    RightsDetailView,
    RightsManageView,
)

app_name = 'rights'

urlpatterns = [
    url(r"^add/$", RightsManageView.as_view(), name="add"),
    url(r"^(?P<pk>\d+)/$", RightsDetailView.as_view(), name="detail"),
    url(r"^(?P<pk>\d+)/edit$", RightsManageView.as_view(), name="edit"),
    url(
        r"^(?P<pk>\d+)/(?P<action>(delete))/$", RightsAPIAdminView.as_view(), name="api"
    ),
]
