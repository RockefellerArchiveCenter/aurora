import random
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from bag_transfer.models import Organization, User
from bag_transfer.test.helpers import TestMixin


class UserTestCase(TestMixin, TestCase):
    fixtures = ["complete.json"]

    def test_user_model_methods(self):
        """Test user model methods."""
        self.has_privs()
        self.in_group()
        self.is_user_active()
        self.permissions_by_group()
        self.save_test()

    def has_privs(self):
        for username, assert_true, assert_false, privs in [
                ("donor", [], ["is_archivist", "can_appraise", "is_manager"], None),
                ("manager", ["can_accession", "can_appraise", "is_manager"], [], "MANAGING"),
                ("accessioner", ["can_accession"], ["can_appraise", "is_manager"], "ACCESSIONER"),
                ("appraiser", ["can_appraise"], ["is_manager", "can_accession"], "APPRAISER")]:
            user = User.objects.get(username=username)
            for meth in assert_true:
                self.assertTrue(
                    getattr(user, meth)(),
                    "User {} is unable to perform function {}".format(user, meth))
            for meth in assert_false:
                self.assertFalse(
                    getattr(user, meth)(),
                    "User {} should not be able to perform function {}".format(
                        user, meth))
            if privs:
                self.assertTrue(user.has_privs(privs))
            else:
                for priv in ["MANAGING", "ACCESSIONER", "APPRAISER"]:
                    self.assertFalse(user.has_privs(priv))

    def in_group(self):
        group = random.choice(["appraisal_archivists", "managing_archivists", "accessioning_archivists"])
        user = random.choice(User.objects.filter(groups__name=group))
        self.assertTrue(user.in_group(group))
        self.assertFalse(user.in_group("foo"))

    def is_user_active(self):
        user = random.choice(User.objects.filter(is_active=True))
        self.assertEqual(user.is_user_active(user, user.organization), user)
        self.assertEqual(user.is_user_active(user, 1000), None)
        user.is_active = False
        user.save()
        self.assertEqual(user.is_user_active(user, user.organization), None)

    def permissions_by_group(self):
        user = User.objects.get(username="admin")
        self.assertTrue(user.permissions_by_group(User.APPRAISER_GROUPS))
        user = random.choice(User.objects.filter(groups__name="appraisal_archivists"))
        self.assertTrue(user.permissions_by_group(User.APPRAISER_GROUPS))
        self.assertFalse(user.permissions_by_group(User.ACCESSIONER_GROUPS))

    @patch("bag_transfer.lib.RAC_CMD.del_from_org")
    @patch("bag_transfer.lib.RAC_CMD.add2grp")
    @patch("bag_transfer.lib.RAC_CMD.add_user")
    def save_test(self, mock_add_user, mock_add2grp, mock_del):
        """Asserts behaviors for new and updated users."""
        mock_add_user.return_value = True
        user = random.choice(User.objects.all())
        old_org = user.organization
        user.organization = random.choice(Organization.objects.all().exclude(id=old_org.pk))
        user.save()
        mock_del.assert_called_once()
        mock_add2grp.assert_called_once()

        User.objects.create_user(
            username="jdoe",
            is_active=True,
            first_name="John",
            last_name="Doe",
            email="test@example.org",
            organization=random.choice(Organization.objects.all()))
        mock_add_user.assert_called_once()
        self.assertEqual(mock_add2grp.call_count, 2)

    def test_user_views(self):
        """Ensures correct HTTP status codes are received for views."""
        for view in ["users:detail", "users:edit"]:
            self.assert_status_code(
                "get", reverse(view, kwargs={"pk": random.choice(User.objects.filter(transfers__isnull=False)).pk}), 200)
        for view in ["users:add", "users:list", "users:password-change"]:
            self.assert_status_code("get", reverse(view), 200)

        user_data = {
            "is_active": True,
            "first_name": "John",
            "last_name": "Doe",
            "username": "jdoe",
            "email": "test@example.org",
            "organization": random.choice(Organization.objects.all()).pk
        }
        self.assert_status_code("post", reverse("users:add"), 302, data=user_data)
        user_data["active"] = False
        self.assert_status_code(
            "post", reverse("users:edit", kwargs={"pk": random.choice([1, 2, 3])}), 200, data=user_data)

        # ensure logged out users are redirected to splash page
        self.client.logout()
        response = self.assert_status_code("get", reverse("splash"), 302)
        self.assertTrue(response.url.startswith(reverse("login")))
