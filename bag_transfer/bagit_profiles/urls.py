from django.conf.urls import url

from .views import (BagItProfileAPIAdminView, BagItProfileCreateView,
                    BagItProfileDetailView, BagItProfileUpdateView)

app_name = "bagit-profiles"

urlpatterns = [
    url(r"^add/$", BagItProfileCreateView.as_view(), name="add"),
    url(r"^(?P<pk>\d+)/$", BagItProfileDetailView.as_view(), name="detail"),
    url(r"^(?P<pk>\d+)/edit/$", BagItProfileUpdateView.as_view(), name="edit"),
    url(r"^(?P<pk>\d+)/(?P<action>(delete))/$", BagItProfileAPIAdminView.as_view(), name="api"),
]
