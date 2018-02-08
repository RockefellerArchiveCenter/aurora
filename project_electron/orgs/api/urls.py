from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from orgs.api.views import OrganizationViewSet, ArchivesViewSet

router = DefaultRouter()
router.register(r'orgs', OrganizationViewSet)
router.register(r'transfers', ArchivesViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
