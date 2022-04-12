from django.urls import re_path

from bag_transfer.orgs.views import (OrganizationCreateView,
                                     OrganizationDetailView,
                                     OrganizationEditView,
                                     OrganizationListView)

app_name = "orgs"

urlpatterns = [
    re_path(r"^add/$", OrganizationCreateView.as_view(), name="add"),
    re_path(r"^(?P<pk>\d+)/$", OrganizationDetailView.as_view(), name="detail"),
    re_path(r"^$", OrganizationListView.as_view(), name="list"),
    re_path(r"^(?P<pk>\d+)/edit/$", OrganizationEditView.as_view(), name="edit"),
]
