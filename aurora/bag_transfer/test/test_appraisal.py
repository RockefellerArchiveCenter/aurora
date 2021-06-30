import random

from bag_transfer.models import Archives, User
from bag_transfer.test import helpers
from django.test import TransactionTestCase
from django.urls import reverse


class AppraisalTestCase(TransactionTestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        self.to_appraise = Archives.objects.filter(process_status=Archives.VALIDATED)
        self.client.force_login(User.objects.get(username="admin"))

    def assert_successful_ajax_request(self, url, data):
        request = self.client.get(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.json()["success"], 1)
        return request

    def test_list_view(self):
        response = self.client.get(reverse("appraise:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["uploads_count"], len(self.to_appraise))

    def test_accept_or_reject(self):
        """Tests accept or reject decisions."""
        for decision, expected_status in [(1, Archives.ACCEPTED), (0, Archives.REJECTED)]:
            archive = random.choice(Archives.objects.filter(process_status=Archives.VALIDATED))
            self.assert_successful_ajax_request(
                reverse("appraise:list"),
                {
                    "req_form": "appraise",
                    "req_type": "decision",
                    "upload_id": archive.pk,
                    "appraisal_decision": decision,
                })
            archive.refresh_from_db()
            self.assertEqual(archive.process_status, expected_status)

    def test_detail(self):
        """Ensures detail responses are returned"""
        for archive in Archives.objects.filter(process_status=Archives.VALIDATED):
            request = self.assert_successful_ajax_request(
                reverse("appraise:list"),
                {
                    "req_form": "detail",
                    "upload_id": archive.pk,
                })
            self.assertEqual(request.json()["object"], archive.pk)

    def test_appraisal_note(self):
        """Tests submission and editing of appraisal note."""
        archive = random.choice(
            Archives.objects.filter(process_status=Archives.VALIDATED))
        note_text = helpers.random_string(30)
        for req_type in ["submit", "edit", "delete"]:
            self.assert_successful_ajax_request(
                reverse("appraise:list"), {
                    "req_form": "appraise",
                    "req_type": req_type,
                    "upload_id": archive.pk,
                    "appraisal_note": note_text,
                })
            updated = Archives.objects.get(pk=archive.pk)
            self.assertEqual(updated.appraisal_note, None if req_type == "delete" else note_text)
