from django.urls import include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework_jwt.views import obtain_jwt_token

from bag_transfer.api.views import (AccessionViewSet, BagItProfileViewSet,
                                    BAGLogViewSet, OrganizationViewSet,
                                    TransferViewSet, UserViewSet)

router = DefaultRouter()
router.register(r"accessions", AccessionViewSet, "accession")
router.register(r"bagit_profiles", BagItProfileViewSet, "bagitprofile")
router.register(r"events", BAGLogViewSet, "baglog")
router.register(r"orgs", OrganizationViewSet, "organization")
router.register(r"transfers", TransferViewSet, "transfer")
router.register(r"users", UserViewSet, "user")

schema_view = get_schema_view(
    title="Aurora API",
    description=("API endpoints for Aurora, an application to receive, "
                 "virus check and validate transfers of digital archival records, and allow "
                 "archivists to appraise and accession those records."),
)

urlpatterns = [
    re_path(r'^schema/', schema_view, name='schema'),
    re_path(r"^", include(router.urls)),
    re_path(r"^get-token/", obtain_jwt_token),
]
