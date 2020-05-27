import random
from unittest.mock import patch

from aurora import settings
from bag_transfer.api.views import ArchivesViewSet
from bag_transfer.models import Archives
from bag_transfer.test import helpers
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory


class APITest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.process_status = Archives.ACCESSIONING_STARTED
        self.archivesspace_identifier = "/repositories/2/archival_objects/3"
        self.archivesspace_parent_identifier = "/repositories/2/archival_objects/4"
        self.orgs = helpers.create_test_orgs(org_count=1)
        helpers.create_test_archives(organization=self.orgs[0], count=10)
        self.user = helpers.create_test_user(
            username=settings.TEST_USER["USERNAME"],
            password=settings.TEST_USER["PASSWORD"],
            org=random.choice(self.orgs),
            is_staff=True)

    @patch("bag_transfer.lib.cleanup.CleanupRoutine.run")
    def update_transfer(self, mock_cleanup):
        for archive in Archives.objects.all():
            request = self.factory.get(
                reverse("archives-detail", kwargs={"pk": archive.pk}), format="json")
            request.user = self.user
            new_transfer = ArchivesViewSet.as_view(
                actions={"get": "retrieve"})(request, pk=archive.pk).data
            for field in ["process_status", "archivesspace_identifier", "archivesspace_parent_identifier"]:
                new_transfer[field] = getattr(self, field)

            request = self.factory.put(
                reverse("archives-detail", kwargs={"pk": archive.pk}),
                data=new_transfer,
                format="json")
            request.user = self.user
            response = ArchivesViewSet.as_view(
                actions={"put": "update"})(request, pk=archive.pk)
            self.assertEqual(response.status_code, 200, "Wrong HTTP status code")
            for field in ["process_status", "archivesspace_identifier", "archivesspace_parent_identifier"]:
                self.assertEqual(
                    response.data[field],
                    getattr(self, field),
                    "{} status not updated".format(field),
                )
            mock_cleanup.assert_called_once()
            mock_cleanup.reset_mock()

    def schema_response(self):
        schema = self.client.get(reverse("schema"))
        self.assertEqual(schema.status_code, 200, "Wrong HTTP code")

    def health_check_response(self):
        status = self.client.get(reverse('api_health_ping'))
        self.assertEqual(status.status_code, 200, "Wrong HTTP code")

    def test_api(self):
        self.update_transfer()
        self.schema_response()
        self.health_check_response()

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
