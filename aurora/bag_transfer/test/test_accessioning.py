import random
from unittest.mock import patch

from bag_transfer.accession.models import Accession
from bag_transfer.models import Archives, BAGLog, RecordCreators
from bag_transfer.test import helpers
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse


class AccessioningTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.orgs = helpers.create_test_orgs(org_count=1)
        self.archives = helpers.create_test_archives(
            organization=self.orgs[0], process_status=Archives.ACCEPTED)
        groups = helpers.create_test_groups(["accessioning_archivists"])
        helpers.create_test_record_creators(count=3)
        helpers.create_test_user(
            username=settings.TEST_USER["USERNAME"],
            org=random.choice(self.orgs),
            groups=groups,
            is_staff=True,
            password=settings.TEST_USER["PASSWORD"])
        self.client.login(
            username=settings.TEST_USER["USERNAME"],
            password=settings.TEST_USER["PASSWORD"])

    def test_accessioning(self):
        id_list = ",".join([str(archive.id) for archive in self.archives])
        self.get_views(id_list)
        self.post_views(id_list)
        self.detail_view()

    def get_views(self, id_list):
        list_response = self.client.get(reverse("accession:list"))
        self.assertEqual(list_response.status_code, 200)

        transfer_group = list_response.context["uploads"][0].transfer_group
        for upload in list_response.context["uploads"]:
            self.assertEqual(upload.transfer_group, transfer_group)
        self.assertEqual(len(list_response.context["uploads"]), len(self.archives))

        record_response = self.client.get(
            reverse("accession:add"), {"transfers": id_list})
        self.assertEqual(record_response.status_code, 200)

    @patch("bag_transfer.accession.views.requests.post")
    def post_views(self, id_list, mock_post):
        mock_post.return_value.status_code.return_value = 200
        accession_data = helpers.get_accession_data(
            creator=random.choice(RecordCreators.objects.all()))
        new_request = self.client.post(
            "{}?transfers={}".format(reverse("accession:add"), id_list), accession_data)
        self.assertEqual(new_request.status_code, 302, "Wrong HTTP response code")
        for acc in Accession.objects.all():
            self.assertTrue(acc.process_status >= Accession.CREATED)
        for arc_id in id_list:
            archive = Archives.objects.get(pk=arc_id)
            self.assertEqual(
                archive.process_status, Archives.ACCESSIONING_STARTED)
            self.assertEqual(
                len(BAGLog.objects.filter(archive=archive, code__code_short="BACC")), 1)

    def detail_view(self):
        accession = random.choice(Accession.objects.all())
        accession_response = self.client.get(
            reverse("accession:detail", kwargs={"pk": accession.pk}))
        self.assertEqual(accession_response.status_code, 200)

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
