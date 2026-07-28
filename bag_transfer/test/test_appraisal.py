import random

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from moto import mock_aws

from bag_transfer.models import Transfer
from bag_transfer.test import helpers


class AppraisalTestCase(helpers.TestMixin, TestCase):
    fixtures = ["complete.json"]

    def setUp(self):
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

    @mock_aws
    def test_reject_s3(self):
        transfer = random.choice(Transfer.objects.filter(process_status=Transfer.VALIDATED))
        with self.settings(S3_USE=True):
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=settings.STORAGE_BUCKET)
            s3_client.put_object(
                Body='mockfileobject',
                Bucket=settings.STORAGE_BUCKET,
                Key=f"{transfer.machine_file_identifier}.tar.gz",
            )
            self.assert_status_code(
                "get", reverse("appraise:list"), 200,
                data={
                    "req_form": "appraise",
                    "req_type": "decision",
                    "upload_id": transfer.pk,
                    "appraisal_decision": 0,
                }, ajax=True)
            transfer.refresh_from_db()
            self.assertEqual(transfer.process_status, Transfer.REJECTED)
            with self.assertRaises(ClientError):
                s3_client.head_object(
                    Bucket=settings.STORAGE_BUCKET,
                    Key=f"{transfer.machine_file_identifier}.tar.gz")

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
