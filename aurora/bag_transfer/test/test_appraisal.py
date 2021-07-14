import random

from bag_transfer.models import Archives, DashboardMonthData, User
from bag_transfer.test import helpers
from django.test import TestCase
from django.urls import reverse


class AppraisalTestCase(helpers.TestMixins, TestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        DashboardMonthData.objects.all().delete()
        self.to_appraise = Archives.objects.filter(process_status=Archives.VALIDATED)
        self.client.force_login(User.objects.get(username="admin"))

    def test_list_view(self):
        response = self.client.get(reverse("appraise:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["uploads_count"], len(self.to_appraise))

    def test_accept_or_reject(self):
        """Tests accept or reject decisions."""
        for decision, expected_status in [(1, Archives.ACCEPTED), (0, Archives.REJECTED)]:
            archive = random.choice(Archives.objects.filter(process_status=Archives.VALIDATED))
            self.assert_status_code(
                "get", reverse("appraise:list"), 200,
                data={
                    "req_form": "appraise",
                    "req_type": "decision",
                    "upload_id": archive.pk,
                    "appraisal_decision": decision,
                }, ajax=True)
            archive.refresh_from_db()
            self.assertEqual(archive.process_status, expected_status)

    def test_detail(self):
        """Ensures detail responses are returned"""
        for archive in Archives.objects.filter(process_status=Archives.VALIDATED):
            request = self.assert_status_code(
                "get", reverse("appraise:list"), 200,
                data={
                    "req_form": "detail",
                    "upload_id": archive.pk,
                }, ajax=True)
            self.assertEqual(request.json()["object"], archive.pk)

    def test_appraisal_note(self):
        """Tests submission and editing of appraisal note."""
        archive = random.choice(
            Archives.objects.filter(process_status=Archives.VALIDATED))
        note_text = helpers.random_string(30)
        for req_type in ["submit", "edit", "delete"]:
            self.assert_status_code(
                "get", reverse("appraise:list"), 200,
                data={
                    "req_form": "appraise",
                    "req_type": req_type,
                    "upload_id": archive.pk,
                    "appraisal_note": note_text,
                }, ajax=True)
            updated = Archives.objects.get(pk=archive.pk)
            self.assertEqual(updated.appraisal_note, None if req_type == "delete" else note_text)
