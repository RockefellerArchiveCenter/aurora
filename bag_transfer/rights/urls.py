from django.urls import re_path

from bag_transfer.rights.views import (RightsAPIAdminView, RightsCreateView,
                                       RightsDetailView, RightsUpdateView)

app_name = 'rights'

urlpatterns = [
    re_path(r"^add/$", RightsCreateView.as_view(), name="add"),
    re_path(r"^(?P<pk>\d+)/$", RightsDetailView.as_view(), name="detail"),
    re_path(r"^(?P<pk>\d+)/edit$", RightsUpdateView.as_view(), name="edit"),
    re_path(
        r"^(?P<pk>\d+)/(?P<action>(delete))/$", RightsAPIAdminView.as_view(), name="api"
    ),
]
