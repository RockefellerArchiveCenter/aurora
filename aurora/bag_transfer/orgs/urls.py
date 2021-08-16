from bag_transfer.orgs.views import (OrganizationCreateView,
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
]
