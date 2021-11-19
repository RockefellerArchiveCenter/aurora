from bag_transfer.rights.views import (RightsAPIAdminView, RightsCreateView,
                                       RightsDetailView, RightsUpdateView)
from django.conf.urls import url

app_name = 'rights'

urlpatterns = [
    url(r"^add/$", RightsCreateView.as_view(), name="add"),
    url(r"^(?P<pk>\d+)/$", RightsDetailView.as_view(), name="detail"),
    url(r"^(?P<pk>\d+)/edit$", RightsUpdateView.as_view(), name="edit"),
    url(
        r"^(?P<pk>\d+)/(?P<action>(delete))/$", RightsAPIAdminView.as_view(), name="api"
    ),
]
