import random

from bag_transfer.models import Archives
from bag_transfer.test import helpers
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse


class AppraisalTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.orgs = helpers.create_test_orgs(org_count=1)
        self.archives = helpers.create_test_archives(
            organization=self.orgs[0],
            process_status=Archives.VALIDATED,
            count=10)
        self.groups = helpers.create_test_groups(["appraisal_archivists"])
        self.user = helpers.create_test_user(
            username=settings.TEST_USER["USERNAME"],
            password=settings.TEST_USER["PASSWORD"],
            org=random.choice(self.orgs),
            is_staff=True,
            groups=self.groups)
        self.client.login(
            username=self.user.username, password=settings.TEST_USER["PASSWORD"])

    def list_views(self):
        response = self.client.get(reverse("appraise:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["uploads_count"], len(self.archives))

    def accept_or_reject(self):
        """Tests accept or reject decisions."""
        for decision in [1, 0]:
            archive = random.choice(Archives.objects.all())
            request = self.client.get(
                reverse("appraise:list"),
                {
                    "req_form": "appraise",
                    "req_type": "decision",
                    "upload_id": archive.pk,
                    "appraisal_decision": decision,
                },
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",)
            self.assertEqual(request.status_code, 200)
            self.assertEqual(request.json()["success"], 1)

    def appraisal_note(self):
        """Tests submission and editing of appraisal note."""
        archive = random.choice(
            Archives.objects.filter(process_status=Archives.VALIDATED))
        note_text = helpers.random_string(30)
        for req_type in ["submit", "edit"]:
            request = self.client.get(
                reverse("appraise:list"),
                {
                    "req_form": "appraise",
                    "req_type": req_type,
                    "upload_id": archive.pk,
                    "appraisal_note": note_text,
                },
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",)
            self.assertEqual(request.json()["success"], 1)
            updated = Archives.objects.get(pk=archive.pk)
            self.assertEqual(updated.appraisal_note, note_text)
            if request.json().get("appraisal_note"):
                self.assertEqual(request.json()["appraisal_note"], note_text)

    def list_count(self):
        response = self.client.get(reverse("appraise:list"))
        self.assertEqual(response.context["uploads_count"], len(self.archives) - 2)

    def test_appraisal(self):
        self.list_views()
        self.accept_or_reject()
        self.appraisal_note()
        self.list_count()

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
