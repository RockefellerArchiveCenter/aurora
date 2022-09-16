import random
from os.path import join
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from bag_transfer.models import Organization
from bag_transfer.test import helpers


class OrgTestCase(helpers.TestMixin, TestCase):
    fixtures = ["complete.json"]

    @patch("bag_transfer.lib.RAC_CMD.add_org")
    def test_org_views(self, mock_add_org):
        list = self.assert_status_code("get", reverse("orgs:list"), 200)
        self.assertEqual(len(list.context["object_list"]), len(Organization.objects.all()))
        for view in ["orgs:detail", "orgs:edit"]:
            self.assert_status_code(
                "get", reverse(view, kwargs={"pk": Organization.objects.get(name="Donor Organization").pk}), 200)

        org_data = {
            "active": True,
            "name": "Test Organization",
            "acquisition_type": "donation"
        }
        self.assert_status_code("get", reverse("orgs:add"), 200)
        self.assert_status_code("post", reverse("orgs:add"), 302, data=org_data)
        org_data["active"] = False
        self.assert_status_code("post", reverse("orgs:add"), 200, data=org_data)
        mock_add_org.assert_called_once()

    def test_org_machine_upload_paths(self):
        """Asserts org_machine_upload_paths property returns expected values."""
        machine_name = helpers.random_string(20)
        org = Organization(machine_name=machine_name)
        root_dir = join(settings.TRANSFER_UPLOADS_ROOT.rstrip("/"), org.machine_name)
        upload_paths = org.org_machine_upload_paths
        self.assertEqual(upload_paths, [join(root_dir, "upload"), join(root_dir, "processing")])

        with self.settings(S3_USE=True):
            upload_paths = org.org_machine_upload_paths
            self.assertEqual(upload_paths, [f"{settings.S3_PREFIX}-{org.machine_name}-upload", join(root_dir, "processing")])

    @patch("bag_transfer.lib.RAC_CMD.add_org")
    @patch("bag_transfer.models.Organization.create_s3_bucket")
    @patch("bag_transfer.models.Organization.create_iam_user")
    def test_create(self, mock_create_user, mock_create_bucket, mock_add_org):
        """Asserts custom behaviors when new objects are added."""
        org = Organization.objects.create(name="Test Organization")
        mock_add_org.assert_called_once_with("testorganization")
        self.assertEqual(org.machine_name, "testorganization")

        with self.settings(S3_USE=True):
            bucket_name = "foo"
            credentials = ("foo", "bar", "baz")
            mock_create_bucket.return_value = bucket_name
            mock_create_user.return_value = credentials
            org = Organization.objects.create(name="New Test Organization")
            mock_create_user.assert_called_once_with(bucket_name)
            mock_create_bucket.assert_called_once()
            self.assertEqual(org.s3_access_key_id, credentials[0])
            self.assertEqual(org.s3_secret_access_key, credentials[1])
            self.assertEqual(org.s3_username, credentials[2])

    @patch("bag_transfer.models.Organization.deactivate_iam_user")
    @patch("bag_transfer.models.Organization.create_s3_bucket")
    @patch("bag_transfer.models.Organization.create_iam_user")
    def test_update(self, mock_create_user, mock_create_bucket, mock_deactivate):
        """Asserts custom behaviors when organizations are updated."""

        """Setting active organization inactive."""
        org = random.choice(Organization.objects.all())
        org.is_active = False
        org.save()
        self.assertTrue([u.is_active is False for u in org.org_users()])

        org = random.choice(Organization.objects.filter(is_active=True))
        org.is_active = False
        org.s3_username = "foo"
        org.save()
        mock_deactivate.assert_called_once()

        """Setting inactive organization active."""
        with self.settings(S3_USE=True):
            bucket_name = "foo"
            credentials = ("foo", "bar", "baz")
            mock_create_bucket.return_value = bucket_name
            mock_create_user.return_value = credentials
            org = random.choice(Organization.objects.filter(is_active=False))
            org.s3_username = None
            org.is_active = True
            org.save()
            mock_create_user.assert_called_once_with(bucket_name)
            mock_create_bucket.assert_called_once()
            self.assertEqual(org.s3_access_key_id, credentials[0])
            self.assertEqual(org.s3_secret_access_key, credentials[1])
            self.assertEqual(org.s3_username, credentials[2])

    @patch("bag_transfer.signals.chown_path_to_root")
    @patch("bag_transfer.signals.delete_system_group")
    @patch("bag_transfer.models.Organization.deactivate_iam_user")
    @patch("bag_transfer.signals.set_count")
    def test_delete(self, mock_signal, mock_deactivate, mock_delete_group, mock_chown_path):
        """Asserts custom behaviors on organization delete."""
        org = random.choice(Organization.objects.all())
        upload_path = org.org_machine_upload_paths[0]
        machine_name = org.machine_name
        org.delete()
        mock_delete_group.assert_called_once_with(machine_name)
        mock_chown_path.assert_called_once_with(upload_path)

        with self.settings(S3_USE=True):
            org = random.choice(Organization.objects.all())
            machine_name = org.machine_name
            org.delete()
            mock_deactivate.assert_called_once_with(machine_name)

    def test_users_by_org(self):
        users_by_org = Organization.users_by_org()
        self.assertTrue(isinstance(users_by_org, list))
        self.assertEqual(len(Organization.objects.all()), len(users_by_org))

    def test_is_org_active(self):
        org = random.choice(Organization.objects.filter(is_active=True))
        self.assertEqual(Organization.is_org_active(org.machine_name), org)
        self.assertEqual(Organization.is_org_active("foobar"), None)
