from django.urls import include, re_path
from rest_framework.routers import DefaultRouter
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

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^get-token/", obtain_jwt_token),
]
