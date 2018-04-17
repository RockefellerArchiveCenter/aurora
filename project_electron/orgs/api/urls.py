from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from orgs.api.views import OrganizationViewSet, ArchivesViewSet, BAGLogViewSet, BagItProfileViewSet, UserViewSet

router = DefaultRouter()
router.register(r'orgs', OrganizationViewSet)
router.register(r'transfers', ArchivesViewSet)
router.register(r'events', BAGLogViewSet)
router.register(r'bagit_profiles', BagItProfileViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^get-token/', obtain_jwt_token),
    url(r'^refresh-token/', refresh_jwt_token),
]
