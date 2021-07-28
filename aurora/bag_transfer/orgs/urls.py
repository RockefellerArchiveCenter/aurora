from bag_transfer.orgs.views import (BagItProfileAPIAdminView,
                                     BagItProfileCreateView,
                                     BagItProfileDetailView,
                                     BagItProfileUpdateView,
                                     OrganizationCreateView,
                                     OrganizationDetailView,
                                     OrganizationEditView,
                                     OrganizationListView)
from django.conf.urls import url

app_name = "orgs"

urlpatterns = [
    url(r"^add/$", OrganizationCreateView.as_view(), name="add"),
    url(r"^(?P<pk>\d+)/$", OrganizationDetailView.as_view(), name="detail"),
    url(r"^$", OrganizationListView.as_view(), name="list"),
    url(r"^(?P<pk>\d+)/edit/$", OrganizationEditView.as_view(), name="edit"),
    url(
        r"^(?P<pk>\d+)/bagit_profiles/add/$",
        BagItProfileCreateView.as_view(),
        name="bagit-profiles-add",
    ),
    url(
        r"^(?P<pk>\d+)/bagit_profile/$",
        BagItProfileDetailView.as_view(),
        name="bagit-profiles-detail",
    ),
    url(
        r"^(?P<pk>\d+)/bagit_profile/edit$",
        BagItProfileUpdateView.as_view(),
        name="bagit-profiles-edit",
    ),
    url(
        r"^(?P<pk>\d+)/bagit_profile/(?P<action>(delete))/$",
        BagItProfileAPIAdminView.as_view(),
        name="bagit-profiles-api",
    ),
]
