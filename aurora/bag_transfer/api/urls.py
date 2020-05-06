from bag_transfer.api.views import (AccessionViewSet, ArchivesViewSet,
                                    BagItProfileViewSet, BAGLogViewSet,
                                    OrganizationViewSet, UserViewSet)
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework_jwt.views import obtain_jwt_token

router = DefaultRouter()
router.register(r"accessions", AccessionViewSet, "accession")
router.register(r"bagit_profiles", BagItProfileViewSet, "bagitprofile")
router.register(r"events", BAGLogViewSet, "baglog")
router.register(r"orgs", OrganizationViewSet, "organization")
router.register(r"transfers", ArchivesViewSet, "archives")
router.register(r"users", UserViewSet, "user")

schema_view = get_schema_view(
    title="Aurora API",
    description=("API endpoints for Aurora, an application to receive, "
                 "virus check and validate transfers of digital archival records, and allow "
                 "archivists to appraise and accession those records."),
)

urlpatterns = [
    url(r'^schema/', schema_view, name='schema'),
    url(r"^", include(router.urls)),
    url(r"^get-token/", obtain_jwt_token),
]
