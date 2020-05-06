import random

from bag_transfer.models import Organization, User
from bag_transfer.test import helpers, setup
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

org_count = 1


class UserOrgTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.orgs = helpers.create_test_orgs(org_count=org_count)
        self.bags = helpers.create_target_bags(
            "valid_bag", settings.TEST_BAGS_DIR, self.orgs[0]
        )
        tr = helpers.run_transfer_routine()
        self.archives = []
        for transfer in tr.transfers:
            archive = helpers.create_test_archive(transfer, self.orgs[0])
            self.archives.append(archive)

    def test_users(self):
        for user in (
            ("donor", "donor"),
            ("managing_archivists", "manager"),
            ("appraisal_archivists", "appraiser"),
            ("accessioning_archivists", "accessioner"),
        ):
            groups = helpers.create_test_groups([user[0]])
            user = helpers.create_test_user(
                username=user[1], org=random.choice(self.orgs)
            )
            for group in groups:
                user.groups.add(group)
                if group.name in [
                    "managing_archivists",
                    "appraisal_archivists",
                    "accessioning_archivists",
                ]:
                    user.is_staff = True
                    user.set_password(settings.TEST_USER["PASSWORD"])
                    user.save()

        # Username, assertTrue methods, assertFalse methods
        user_list = (
            ("donor", [], ["is_archivist", "can_appraise", "is_manager"], ""),
            ("manager", ["is_archivist", "can_appraise", "is_manager"], [], "MANAGING"),
            (
                "accessioner",
                ["is_archivist"],
                ["can_appraise", "is_manager"],
                "ACCESSIONER",
            ),
            (
                "appraiser",
                ["is_archivist", "can_appraise"],
                ["is_manager"],
                "APPRAISER",
            ),
        )
        for u in user_list:
            user = User.objects.get(username=u[0])
            for meth in u[1]:
                self.assertTrue(
                    getattr(user, meth)(),
                    "User {} is unable to perform function {}".format(user, meth),
                )
            for meth in u[2]:
                self.assertFalse(
                    getattr(user, meth)(),
                    "User {} should not be able to perform function {}".format(
                        user, meth
                    ),
                )
            if len(u[3]) > 1:
                self.assertTrue(user.has_privs(u[3]))

        # Test user views
        self.user_views()

    def test_orgs(self):
        groups = helpers.create_test_groups(["managing_archivists"])
        user = helpers.create_test_user(
            username=settings.TEST_USER["USERNAME"], org=random.choice(self.orgs)
        )
        for group in groups:
            user.groups.add(group)
        user.is_staff = True
        user.set_password(settings.TEST_USER["PASSWORD"])
        user.save()
        self.client.login(
            username=user.username, password=settings.TEST_USER["PASSWORD"]
        )

        # Test Org views
        self.org_views()
        for org in Organization.objects.all():
            if org not in self.orgs:
                self.orgs.append(org)

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)

    def user_views(self):
        user = User.objects.get(groups__name="managing_archivists")
        self.client.login(
            username=user.username, password=settings.TEST_USER["PASSWORD"]
        )

        for view in ["users:detail", "users:edit"]:
            response = self.client.get(
                reverse(view, kwargs={"pk": random.choice(User.objects.all()).pk})
            )
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
            user_data,
        )
        self.assertTrue(response.status_code, 200)

    def org_views(self):
        response = self.client.get(reverse("orgs:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), org_count)
        for view in ["orgs:detail", "orgs:edit"]:
            response = self.client.get(
                reverse(view, kwargs={"pk": random.choice(self.orgs).pk})
            )
            self.assertEqual(response.status_code, 200)

        org_data = setup.org_data
        response = self.client.post(reverse("orgs:add"), org_data)
        self.assertTrue(response.status_code, 200)

        # make org inactive
        org_data["active"] = False
        response = self.client.post(
            reverse("orgs:edit", kwargs={"pk": random.choice(self.orgs).pk}), org_data
        )
        self.assertTrue(response.status_code, 200)
