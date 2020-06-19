import random

from bag_transfer.models import (AcceptBagItVersion, AcceptSerialization,
                                 BagItProfileBagInfo, ManifestsAllowed,
                                 ManifestsRequired, TagFilesRequired,
                                 TagManifestsRequired)
from bag_transfer.test import helpers
from bag_transfer.test.setup import BAGINFO_FIELD_CHOICES
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse


class BagItProfileTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.orgs = helpers.create_test_orgs(org_count=1)
        self.user = helpers.create_test_user(
            username=settings.TEST_USER["USERNAME"],
            password=settings.TEST_USER["PASSWORD"],
            org=random.choice(self.orgs),
            groups=helpers.create_test_groups(["managing_archivists"]),
            is_staff=True)
        self.client.login(
            username=self.user.username, password=settings.TEST_USER["PASSWORD"])
        self.bagitprofiles = []
        self.baginfos = []

    def test_bagitprofiles(self):
        for org in self.orgs:
            profile = helpers.create_test_bagitprofile(organization=org)
            response = self.client.get(
                reverse("bagitprofile-detail", kwargs={"pk": profile.pk}))
            self.assertEqual(response.status_code, 200)
            self.bagitprofiles.append(profile)
        self.assertEqual(len(self.bagitprofiles), len(self.orgs))

        for profile in self.bagitprofiles:
            helpers.create_test_manifestsallowed(bagitprofile=profile)
            helpers.create_test_manifestsrequired(bagitprofile=profile)
            helpers.create_test_acceptserialization(bagitprofile=profile)
            helpers.create_test_acceptbagitversion(bagitprofile=profile)
            helpers.create_test_tagmanifestsrequired(bagitprofile=profile)
            helpers.create_test_tagfilesrequired(bagitprofile=profile)
            for field in BAGINFO_FIELD_CHOICES:
                baginfo = helpers.create_test_bagitprofilebaginfo(
                    bagitprofile=profile, field=field)
                self.baginfos.append(baginfo)
            self.assertEqual(
                len(BagItProfileBagInfo.objects.all()), len(BAGINFO_FIELD_CHOICES))

            for info in self.baginfos:
                helpers.create_test_bagitprofilebaginfovalues(baginfo=info)

            for obj in (ManifestsAllowed, ManifestsRequired, AcceptSerialization,
                        AcceptBagItVersion, TagManifestsRequired, TagFilesRequired):
                self.assertEqual(len(obj.objects.all()), len(self.bagitprofiles))

            for info in BagItProfileBagInfo.objects.all():
                self.assertTrue(len(info.bagitprofilebaginfovalues_set.all()) > 0)

        # Get bagit profiles for each org
        for org in self.orgs:
            self.assertTrue(org.bagit_profile)

        # Test GET views
        org = random.choice(self.orgs)

        for view in ["orgs:bagit-profiles-add", "orgs:bagit-profiles-edit", "organization-bagit-profile"]:
            response = self.client.get(reverse(view, kwargs={"pk": org.pk}))
            self.assertEqual(response.status_code, 200, "Response error: {}".format(response))

        response = self.client.get(reverse("bagitprofile-list"))
        self.assertEqual(response.status_code, 200)

        # Creating new BagItProfile
        organization = random.choice(self.orgs)
        new_request = self.client.post(
            reverse("orgs:bagit-profiles-add", kwargs={"pk": organization.pk}),
            {
                "contact_email": "archive@rockarch.org",
                "source_organization": organization.pk,
                "allow_fetch": random.choice([True, False]),
                "external_description": helpers.random_string(100),
                "serialization": random.choice(["forbidden", "required", "optional"]),
                "version": 0,
                "bag_info-INITIAL_FORMS": 0,
                "bag_info-TOTAL_FORMS": 1,
                "bag_info-0-required": random.choice([True, False]),
                "bag_info-0-field": random.choice(BAGINFO_FIELD_CHOICES)[0],
                "bag_info-0-repeatable": random.choice([True, False]),
                "nested_bag_info-0_bagitprofilebaginfovalues_set-0-name": helpers.random_string(
                    20
                ),
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
            },
        )
        self.assertEqual(new_request.status_code, 302, "Request was not redirected")

        # Updating BagItProfile
        update_request = self.client.post(
            reverse(
                "orgs:bagit-profiles-edit",
                kwargs={"pk": organization.pk}),
            {
                "contact_email": "archive@rockarch.org",
                "source_organization": organization.pk,
                "allow_fetch": random.choice([True, False]),
                "external_description": helpers.random_string(100),
                "serialization": "optional",
                "version": 1,
                "bag_info-INITIAL_FORMS": 1,
                "bag_info-TOTAL_FORMS": 1,
                "bag_info-0-id": 1,
                "bag_info-0-required": True,
                "bag_info-0-field": "source_organization",
                "bag_info-0-repeatable": False,
                "nested_bag_info-0_bagitprofilebaginfovalues_set-0-name": "Ford Foundation",
                "nested_bag_info-0_bagitprofilebaginfovalues_set-0-id": 1,
                "nested_bag_info-0_bagitprofilebaginfovalues_set-TOTAL_FORMS": 1,
                "nested_bag_info-0_bagitprofilebaginfovalues_set-INITIAL_FORMS": 1,
                "serialization-INITIAL_FORMS": 1,
                "serialization-TOTAL_FORMS": 3,
                "serialization-0-id": 1,
                "serialization-0-name": "application/zip",
                "serialization-1-name": "application/x-tar",
                "serialization-2-name": "application/x-gzip",
                "tag_files-TOTAL_FORMS": 1,
                "tag_files-INITIAL_FORMS": 1,
                "tag_files-0-id": 1,
                "tag_files-0-DELETE": True,
                "tag_manifests-TOTAL_FORMS": 1,
                "tag_manifests-INITIAL_FORMS": 1,
                "tag_manifests-0-id": 1,
                "tag_manifests-0-DELETE": True,
                "version-TOTAL_FORMS": 2,
                "version-INITIAL_FORMS": 1,
                "version-0-id": 1,
                "version-0-name": "0.96",
                "version-1-name": 0.97,
                "manifests-TOTAL_FORMS": 0,
                "manifests-INITIAL_FORMS": 1,
                "manifests-0-id": 1,
                "manifests-0-DELETE": True,
                "manifests_allowed-TOTAL_FORMS": 1,
                "manifests_allowed-INITIAL_FORMS": 0,
                "manifests_allowed-0-name": random.choice(["sha256", "sha512"]),
            },
        )
        self.assertEqual(update_request.status_code, 302, "Request was not redirected")

        # Delete bagit profile
        delete_request = self.client.get(
            reverse(
                "orgs:bagit-profiles-api",
                kwargs={
                    "pk": organization.pk,
                    "action": "delete",
                },
            ),
            {},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(delete_request.status_code, 200)
        resp = delete_request.json()
        self.assertEqual(resp["success"], 1)
        non_ajax_request = self.client.get(
            reverse(
                "orgs:bagit-profiles-api",
                kwargs={
                    "pk": organization.pk,
                    "action": "delete",
                },
            )
        )
        self.assertEqual(non_ajax_request.status_code, 404)

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
