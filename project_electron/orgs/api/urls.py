from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from orgs.api.views import OrganizationViewSet, ArchivesViewSet, BAGLogViewSet

router = DefaultRouter()
router.register(r'orgs', OrganizationViewSet)
router.register(r'transfers', ArchivesViewSet)
router.register(r'events', BAGLogViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
