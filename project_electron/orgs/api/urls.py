from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from orgs.api.views import OrganizationViewSet, ArchivesViewSet, BAGLogViewSet, BagItProfileViewSet

router = DefaultRouter()
router.register(r'orgs', OrganizationViewSet)
router.register(r'transfers', ArchivesViewSet)
router.register(r'events', BAGLogViewSet)
router.register(r'bagit_profiles', BagItProfileViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
