import random

from bag_transfer.models import Organization, User
from bag_transfer.test import helpers, setup
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

org_count = 1


class UserTestCase(TestCase):
    def setUp(self):
        self.orgs = helpers.create_test_orgs(org_count=org_count)
        self.client.force_login(User.objects.get(username="admin"))

    def assert_status_code(self, method, url, data, status_code):
        response = getattr(self.client, method)(url, data)
        self.assertEqual(response.status_code, status_code)
        return response

    def create_users(self):
        for group, username in [("donor", "donor"),
                                ("managing_archivists", "manager"),
                                ("appraisal_archivists", "appraiser"),
                                ("accessioning_archivists", "accessioner")]:
            is_staff = False if group == "donor" else True
            user = helpers.create_test_user(
                username=username,
                password=settings.TEST_USER["PASSWORD"],
                org=random.choice(self.orgs),
                groups=helpers.create_test_groups([group]),
                is_staff=is_staff)

        for username, assert_true, assert_false, privs in [
                ("donor", [], ["is_archivist", "can_appraise", "is_manager"], None),
                ("manager", ["is_archivist", "can_appraise", "is_manager"], [], "MANAGING"),
                ("accessioner", ["is_archivist"], ["can_appraise", "is_manager"], "ACCESSIONER"),
                ("appraiser", ["is_archivist", "can_appraise"], ["is_manager"], "APPRAISER")]:
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

    def user_views(self):
        user = User.objects.get(groups__name="managing_archivists")
        self.client.login(
            username=user.username, password=settings.TEST_USER["PASSWORD"])

        for view in ["users:detail", "users:edit"]:
            response = self.client.get(
                reverse(view, kwargs={"pk": random.choice(User.objects.all()).pk}))
            self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("users:add"))
        self.assertEqual(response.status_code, 200)

        user_data = setup.user_data
        user_data["organization"] = random.choice(self.orgs)
        response = self.client.post(reverse("users:add"), user_data)
        self.assertTrue(response.status_code, 200)

        # make user inactive
        user_data["active"] = False
        response = self.client.post(
            reverse("users:edit", kwargs={"pk": random.choice(User.objects.all()).pk}),
            user_data)
        self.assertTrue(response.status_code, 200)

    def test_users(self):
        self.create_users()
        self.user_views()

    def tearDown(self):
        helpers.delete_test_orgs(Organization.objects.all())
