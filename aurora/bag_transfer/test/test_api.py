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
        self.org = helpers.create_test_orgs(org_count=1)[0]
        profile = helpers.create_test_bagitprofile(self.org)
        baginfo = helpers.create_test_bagitprofilebaginfo(bagitprofile=profile)
        for x in range(5):
            helpers.create_test_bagitprofilebaginfovalues(baginfo)
        helpers.create_test_accessions()
        rights_statement = helpers.create_rights_statement(org=self.org)
        helpers.create_rights_info(rights_statement)
        helpers.create_test_baglogs()
        helpers.create_test_archives(
            organization=self.org,
            process_status=Archives.ACCEPTED,
            count=10)
        self.user = helpers.create_test_user(
            username=settings.TEST_USER["USERNAME"],
            password=settings.TEST_USER["PASSWORD"],
            org=self.org,
            is_staff=True)

    def assert_status_code(self, url, status_code):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code, "Wrong HTTP status code, expecting {}".format(status_code))

    @patch("bag_transfer.lib.cleanup.CleanupRoutine.run")
    def test_update_transfer(self, mock_cleanup):
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

    def test_schema_response(self):
        self.assert_status_code(reverse("schema"), 200)

    def test_health_check_response(self):
        self.assert_status_code(reverse("api_health_ping"), 200)

    def test_action_endpoints(self):
        self.client.login(
            username=settings.TEST_USER["USERNAME"],
            password=settings.TEST_USER["PASSWORD"])
        org = self.org.pk
        self.assert_status_code(reverse("organization-bagit-profile", kwargs={"pk": org}), 200)
        self.assert_status_code(reverse("organization-rights-statements", kwargs={"pk": org}), 200)
        self.assert_status_code(reverse("user-current"), 200)

    def test_list_views(self):
        self.client.login(
            username=settings.TEST_USER["USERNAME"],
            password=settings.TEST_USER["PASSWORD"])
        self.assert_status_code(reverse("accession-list"), 200)
        self.assert_status_code(reverse("baglog-list"), 200)
        self.assert_status_code(reverse("organization-list"), 200)
        self.assert_status_code(reverse("user-list"), 200)
