import random

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse

from bag_transfer.test import helpers
from bag_transfer.models import Archives


class AppraisalTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.orgs = helpers.create_test_orgs(org_count=1)
        self.bags = helpers.create_target_bags(
            "valid_bag", settings.TEST_BAGS_DIR, self.orgs[0]
        )
        tr = helpers.run_transfer_routine()
        self.archives = []
        for transfer in tr.transfers:
            archive = helpers.create_test_archive(transfer, self.orgs[0])
            self.archives.append(archive)
        self.groups = helpers.create_test_groups(["appraisal_archivists"])
        self.user = helpers.create_test_user(
            username=settings.TEST_USER["USERNAME"], org=random.choice(self.orgs)
        )
        for group in self.groups:
            self.user.groups.add(group)
        self.user.is_staff = True
        self.user.set_password(settings.TEST_USER["PASSWORD"])
        self.user.save()

    def test_appraisal(self):
        for archive in self.archives:
            archive.process_status = Archives.VALIDATED
            archive.save()

        # Test GET views
        self.client.login(
            username=self.user.username, password=settings.TEST_USER["PASSWORD"]
        )
        response = self.client.get(reverse("appraise:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["uploads_count"], len(self.archives))

        # Accept/Reject archives
        accept_archive = random.choice(
            Archives.objects.filter(process_status=Archives.VALIDATED)
        )
        accept_request = self.client.get(
            reverse("appraise:list"),
            {
                "req_form": "appraise",
                "req_type": "decision",
                "upload_id": accept_archive.pk,
                "appraisal_decision": 1,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(accept_request.status_code, 200)
        resp = accept_request.json()
        self.assertEqual(resp["success"], 1)
        reject_archive = random.choice(
            Archives.objects.filter(process_status=Archives.VALIDATED)
        )
        reject_request = self.client.get(
            reverse("appraise:list"),
            {
                "req_form": "appraise",
                "req_type": "decision",
                "upload_id": reject_archive.pk,
                "appraisal_decision": 0,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        resp = reject_request.json()
        self.assertEqual(resp["success"], 1)

        # Submit and Edit appraisal note
        note_archive = random.choice(
            Archives.objects.filter(process_status=Archives.VALIDATED)
        )
        submit_note_request = self.client.get(
            reverse("appraise:list"),
            {
                "req_form": "appraise",
                "req_type": "submit",
                "upload_id": note_archive.pk,
                "appraisal_note": "Test appraisal note",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        resp = submit_note_request.json()
        self.assertEqual(resp["success"], 1)
        updated_archive = Archives.objects.get(pk=note_archive.pk)
        self.assertEqual(updated_archive.appraisal_note, "Test appraisal note")
        edit_note_request = self.client.get(
            reverse("appraise:list"),
            {"req_form": "appraise", "req_type": "edit", "upload_id": note_archive.pk},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        resp = edit_note_request.json()
        self.assertEqual(resp["success"], 1)
        self.assertEqual(resp["appraisal_note"], "Test appraisal note")

        # Make sure appraised archives are no longer in this view
        response = self.client.get(reverse("appraise:list"))
        self.assertEqual(response.context["uploads_count"], len(self.archives) - 2)

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
