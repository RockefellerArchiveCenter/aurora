from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from bag_transfer.api.views import AccessionViewSet, OrganizationViewSet, ArchivesViewSet, BAGLogViewSet, BagItProfileViewSet, UserViewSet

router = DefaultRouter()
router.register(r'accessions', AccessionViewSet, 'accession')
router.register(r'bagit_profiles', BagItProfileViewSet, 'bagitprofile')
router.register(r'events', BAGLogViewSet, 'baglog')
router.register(r'orgs', OrganizationViewSet, 'organization')
router.register(r'transfers', ArchivesViewSet, 'archives')
router.register(r'users', UserViewSet, 'user')
schema_view = get_schema_view(
   openapi.Info(
      title="Aurora API",
      default_version='v1',
      description="API for Aurora",
      contact=openapi.Contact(email="archive@rockarch.org"),
      license=openapi.License(name="MIT License"),
   ),
   validators=['flex', 'ssv'],
   public=False,
)

urlpatterns = [
    url(r'^schema(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^', include(router.urls)),
    url(r'^get-token/', obtain_jwt_token),
]
