import random

from bag_transfer.models import BagItProfile, Organization
from bag_transfer.test import helpers
from bag_transfer.test.helpers import BAGINFO_FIELD_CHOICES, TestMixin
from django.test import TestCase
from django.urls import reverse


class BagItProfileTestCase(TestMixin, TestCase):
    fixtures = ["complete.json"]

    def test_views(self):
        org = Organization.objects.get(name="Donor Organization")
        for view in ["orgs:bagit-profiles-add", "orgs:bagit-profiles-edit", "organization-bagit-profile"]:
            self.assert_status_code("get", reverse(view, kwargs={"pk": org.pk}), 200)
        self.assert_status_code("get", reverse("bagitprofile-list"), 200)
        org.bagit_profile = None
        org.save()
        self.assert_status_code("get", reverse("orgs:bagit-profiles-edit", kwargs={"pk": org.pk}), 200)

        data = {
            "contact_email": "archive@rockarch.org",
            "source_organization": org.pk,
            "applies_to_organization": org.pk,
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
        self.assert_status_code(
            "post", reverse("orgs:bagit-profiles-add", kwargs={"pk": org.pk}),
            302, data=data)
        org.refresh_from_db()
        self.assertIsNot(None, org.bagit_profile, "BagIt profile was not assigned to organization")

        external_description = helpers.random_string(150)
        data["external_description"] = external_description
        self.assert_status_code(
            "post", reverse("orgs:bagit-profiles-add", kwargs={"pk": org.pk}),
            302, data=data)
        self.assertIsNot(None, org.bagit_profile, "BagIt profile not assigned to organization")
        org.refresh_from_db()
        self.assertEqual(org.bagit_profile.external_description, external_description, "External Description was not updated")

        delete_request = self.assert_status_code(
            "get",
            reverse("orgs:bagit-profiles-api", kwargs={"pk": org.pk, "action": "delete"}),
            200, data={}, ajax=True)
        self.assertEqual(delete_request.json()["success"], 1)
        org.refresh_from_db()
        self.assertEqual(None, org.bagit_profile, "BagIt Profile not deleted")

        self.assert_status_code(
            "get", reverse("orgs:bagit-profiles-api", kwargs={"pk": org.pk, "action": "delete"}), 404)

        profile = random.choice(BagItProfile.objects.all())
        self.assert_status_code("get", reverse("orgs:bagit-profiles-detail", kwargs={"pk": profile.source_organization.pk}), 200)

    def test_save_to_org(self):
        """Asserts that the `save_to_org` method works as intended"""
        org = random.choice(Organization.objects.all())
        org.bagit_profile = None
        org.save()
        profile = random.choice(BagItProfile.objects.all())
        profile.save_to_org(org)
        self.assertIsNot(None, org.bagit_profile)
