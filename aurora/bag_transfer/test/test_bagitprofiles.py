import random

from bag_transfer.models import BagItProfile, Organization
from bag_transfer.test import helpers
from bag_transfer.test.helpers import BAGINFO_FIELD_CHOICES, TestMixin
from django.test import TestCase
from django.urls import reverse


class BagItProfileTestCase(TestMixin, TestCase):
    fixtures = ["complete.json"]

    def test_views(self):
        profile = random.choice(BagItProfile.objects.all())
        org = random.choice(Organization.objects.all())
        for view in ["bagit-profiles:detail", "bagit-profiles:edit", "organization-bagit-profiles"]:
            self.assert_status_code("get", reverse(view, kwargs={"pk": profile.pk}), 200)
        self.assert_status_code("get", reverse("bagitprofile-list"), 200)

        data = {
            "contact_email": "archive@rockarch.org",
            "source_organization": org.pk,
            "organization": org.pk,
            "allow_fetch": random.choice([True, False]),
            "external_description": helpers.random_string(100),
            "serialization": random.choice(["forbidden", "required", "optional"]),
            "version": 0,
            "bag_info-INITIAL_FORMS": 0,
            "bag_info-TOTAL_FORMS": 1,
            "bag_info-0-required": random.choice([True, False]),
            "bag_info-0-field": random.choice(BAGINFO_FIELD_CHOICES)[0],
            "bag_info-0-repeatable": random.choice([True, False]),
            "nested_bag_info-0_bagitprofilebaginfovalues_set-0-name": helpers.random_string(20),
            "nested_bag_info-0_bagitprofilebaginfovalues_set-TOTAL_FORMS": 1,
            "nested_bag_info-0_bagitprofilebaginfovalues_set-INITIAL_FORMS": 0,
            "serialization-INITIAL_FORMS": 0,
            "serialization-TOTAL_FORMS": 1,
            "serialization-0-name": random.choice(
                ["application/zip", "application/x-tar", "application/x-gzip"]
            ),
            "tag_files-TOTAL_FORMS": 1,
            "tag_files-INITIAL_FORMS": 0,
            "tag_files-0-name": helpers.random_string(20),
            "tag_manifests-TOTAL_FORMS": 1,
            "tag_manifests-INITIAL_FORMS": 0,
            "tag_manifests-0-name": random.choice(["sha256", "sha512"]),
            "version-TOTAL_FORMS": 1,
            "version-INITIAL_FORMS": 0,
            "version-0-name": random.choice(["0.96", 0.97]),
            "manifests-TOTAL_FORMS": 1,
            "manifests-INITIAL_FORMS": 0,
            "manifests-0-name": random.choice(["sha256", "sha512"]),
            "manifests_allowed-TOTAL_FORMS": 1,
            "manifests_allowed-INITIAL_FORMS": 0,
            "manifests_allowed-0-name": random.choice(["sha256", "sha512"]),
        }
        previous_len = len(BagItProfile.objects.all())
        self.assert_status_code(
            "post", "{}?org={}".format(reverse("bagit-profiles:add"), org.pk),
            302, data=data)
        self.assertIsNot(None, profile.organization, "BagIt profile was not assigned to organization")
        self.assertEqual(
            previous_len + 1, len(BagItProfile.objects.all()),
            "Expected 1 new BagIt Profile to be created, found {}".format(len(BagItProfile.objects.all()) - previous_len))

        external_description = helpers.random_string(150)
        data["external_description"] = external_description
        self.assert_status_code(
            "post", reverse("bagit-profiles:edit", kwargs={"pk": profile.pk}),
            302, data=data)
        profile.refresh_from_db()
        self.assertIsNot(None, profile.organization, "BagIt profile not assigned to organization")
        org.refresh_from_db()
        self.assertEqual(profile.external_description, external_description, "External Description was not updated")
        self.assertEqual(
            previous_len + 1, len(BagItProfile.objects.all()),
            "A new BagIt Profile was unexpectedly created")

        delete_request = self.assert_status_code(
            "get",
            reverse("bagit-profiles:api", kwargs={"pk": profile.pk, "action": "delete"}),
            200, data={}, ajax=True)
        self.assertEqual(delete_request.json()["success"], 1)
        org.refresh_from_db()

        self.assert_status_code(
            "get", reverse("bagit-profiles:api", kwargs={"pk": profile.pk, "action": "delete"}), 404)
