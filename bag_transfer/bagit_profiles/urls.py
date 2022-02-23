from django.urls import re_path

from .views import (BagItProfileAPIAdminView, BagItProfileCreateView,
                    BagItProfileDetailView, BagItProfileUpdateView)

app_name = "bagit-profiles"

urlpatterns = [
    re_path(r"^add/$", BagItProfileCreateView.as_view(), name="add"),
    re_path(r"^(?P<pk>\d+)/$", BagItProfileDetailView.as_view(), name="detail"),
    re_path(r"^(?P<pk>\d+)/edit/$", BagItProfileUpdateView.as_view(), name="edit"),
    re_path(r"^(?P<pk>\d+)/(?P<action>(delete))/$", BagItProfileAPIAdminView.as_view(), name="api"),
]
