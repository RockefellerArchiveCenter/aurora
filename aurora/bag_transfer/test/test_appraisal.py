import random

from bag_transfer.models import DashboardMonthData, Transfer
from bag_transfer.test import helpers
from django.test import TestCase
from django.urls import reverse


class AppraisalTestCase(helpers.TestMixin, TestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        DashboardMonthData.objects.all().delete()
        self.to_appraise = Transfer.objects.filter(process_status=Transfer.VALIDATED)
        super().setUp()

    def test_list_view(self):
        response = self.client.get(reverse("appraise:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["uploads_count"], len(self.to_appraise))

    def test_accept_or_reject(self):
        """Tests accept or reject decisions."""
        for decision, expected_status in [(1, Transfer.ACCEPTED), (0, Transfer.REJECTED)]:
            transfer = random.choice(Transfer.objects.filter(process_status=Transfer.VALIDATED))
            self.assert_status_code(
                "get", reverse("appraise:list"), 200,
                data={
                    "req_form": "appraise",
                    "req_type": "decision",
                    "upload_id": transfer.pk,
                    "appraisal_decision": decision,
                }, ajax=True)
            transfer.refresh_from_db()
            self.assertEqual(transfer.process_status, expected_status)

    def test_detail(self):
        """Ensures detail responses are returned"""
        for transfer in Transfer.objects.filter(process_status=Transfer.VALIDATED):
            request = self.assert_status_code(
                "get", reverse("appraise:list"), 200,
                data={
                    "req_form": "detail",
                    "upload_id": transfer.pk,
                }, ajax=True)
            self.assertEqual(request.json()["object"], transfer.pk)

    def test_appraisal_note(self):
        """Tests submission and editing of appraisal note."""
        transfer = random.choice(
            Transfer.objects.filter(process_status=Transfer.VALIDATED))
        note_text = helpers.random_string(30)
        for req_type in ["submit", "edit", "delete"]:
            self.assert_status_code(
                "get", reverse("appraise:list"), 200,
                data={
                    "req_form": "appraise",
                    "req_type": req_type,
                    "upload_id": transfer.pk,
                    "appraisal_note": note_text,
                }, ajax=True)
            updated = Transfer.objects.get(pk=transfer.pk)
            self.assertEqual(updated.appraisal_note, None if req_type == "delete" else note_text)
