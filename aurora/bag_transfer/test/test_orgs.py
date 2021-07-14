import random
from unittest.mock import patch

from bag_transfer.models import Organization
from bag_transfer.test import helpers
from django.test import TestCase
from django.urls import reverse


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

    def test_org_model_methods(self):
        self.org_machine_upload_paths()
        self.save_test()
        self.users_by_org()
        self.is_org_active()

    def org_machine_upload_paths(self):
        machine_name = helpers.random_string(20)
        org = Organization(machine_name=machine_name)
        upload_paths = org.org_machine_upload_paths()
        self.assertEqual(len(upload_paths), 2)
        self.assertTrue(any([u.endswith("{}/upload/".format(machine_name)) for u in upload_paths]))
        self.assertTrue(any([u.endswith("{}/processing/".format(machine_name)) for u in upload_paths]))

    def save_test(self):
        org = random.choice(Organization.objects.all())
        org.is_active = False
        org.save()
        self.assertTrue([u.is_active is False for u in org.org_users()])

    def users_by_org(self):
        users_by_org = Organization.users_by_org()
        self.assertTrue(isinstance(users_by_org, list))
        self.assertEqual(len(Organization.objects.all()), len(users_by_org))

    def is_org_active(self):
        org = random.choice(Organization.objects.filter(is_active=True))
        self.assertEqual(Organization.is_org_active(org.machine_name), org)
        self.assertEqual(Organization.is_org_active("foobar"), None)
