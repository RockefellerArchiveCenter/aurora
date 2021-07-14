import random

from bag_transfer.models import Organization, User
from bag_transfer.rights.models import (RightsStatement,
                                        RightsStatementCopyright,
                                        RightsStatementLicense,
                                        RightsStatementOther,
                                        RightsStatementStatute)
from bag_transfer.test.helpers import RIGHTS_BASIS_DATA, RIGHTS_GRANTED_DATA
from django.test import TestCase
from django.urls import reverse


class RightsTestCase(TestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        self.client.force_login(User.objects.get(username="admin"))

    def assert_status_code(self, method, url, data, status_code):
        response = getattr(self.client, method)(url, data)
        self.assertEqual(response.status_code, status_code)
        return response

    def test_model_methods(self):
        self.rights_info()
        self.rights_info_notes()
        self.get_date_keys()
        self.merge_rights()

    def rights_info(self):
        for basis, expected_type in [
                ("Copyright", RightsStatementCopyright),
                ("License", RightsStatementLicense),
                ("Statute", RightsStatementStatute),
                ("Other", RightsStatementOther)]:
            rights_statement = random.choice(RightsStatement.objects.filter(rights_basis=basis))
            self.assertTrue(isinstance(rights_statement.rights_info, expected_type))

    def rights_info_notes(self):
        rights_statement = random.choice(RightsStatement.objects.all())
        self.assertTrue(isinstance(rights_statement.rights_info_notes(), str))

    def get_date_keys(self):
        for basis, prefix in [
                ("Copyright", "copyright_applicable"),
                ("License", "license_applicable"),
                ("Statute", "statute_applicable"),
                ("Other", "other_rights_applicable")]:
            rights_statement = random.choice(RightsStatement.objects.filter(rights_basis=basis))
            for periods, expected_len in [(False, 2), (True, 4)]:
                keys = rights_statement.get_date_keys(periods=periods)
                self.assertEqual(len(keys), expected_len)
                self.assertTrue([s.startswith(prefix) for s in keys])

    def merge_rights(self):
        for merge_list in [
                random.choices(RightsStatement.objects.filter(rights_basis="Copyright"), k=3),
                random.choices(RightsStatement.objects.all(), k=3)]:
            merge_list = random.choices(RightsStatement.objects.filter(rights_basis="Copyright"), k=3)
            merged = RightsStatement.merge_rights(merge_list)
            self.assertTrue(isinstance(merged, list))
            self.assertTrue([isinstance(m, RightsStatement) for m in merged])

    def test_views(self):
        """Asserts that views return expected status codes"""
        for view in ["rights:edit", "rights:detail"]:
            self.assert_status_code("get", reverse(view, kwargs={"pk": random.choice(RightsStatement.objects.all()).pk}), None, 200)
        for org in Organization.objects.all():
            self.assert_status_code("get", reverse("rights:add"), {"org": org.pk}, 200)

    def test_manage_rights_statements(self):
        """Tests creation and update of rights statement views, as well as error handling"""
        # Creating new RightsStatements
        post_organization = random.choice(Organization.objects.all())
        new_basis_data = random.choice(RIGHTS_BASIS_DATA)
        new_basis_data["organization"] = post_organization.pk
        new_basis_data.update(RIGHTS_GRANTED_DATA)
        previous_length = len(RightsStatement.objects.all())
        self.assert_status_code(
            "post",
            "{}{}".format(reverse("rights:add"), "?org={}".format(post_organization.pk)),
            new_basis_data, 302)

        self.assertEqual(
            len(RightsStatement.objects.all()),
            previous_length + 1,
            "{} Rights Statements were created, expected number is 1".format(
                len(RightsStatement.objects.all()) - previous_length))
        self.assertEqual(
            RightsStatement.objects.last().rights_basis,
            new_basis_data["rights_basis"],
            "Rights bases do not match")

        # Updating RightsStatements
        rights_statement = RightsStatement.objects.last()
        updated_basis_data = new_basis_data
        if updated_basis_data["rights_basis"] == "Other":
            basis_set = "rightsstatementother_set"
            note_key = "other_rights_note"
        else:
            basis_set = "rightsstatement{}_set".format(
                updated_basis_data["rights_basis"].lower())
            note_key = "{}_note".format(updated_basis_data["rights_basis"].lower())
        updated_basis_data[basis_set + "-0-" + note_key] = "Revised test note"
        basis_objects = getattr(rights_statement, basis_set).all()
        updated_basis_data[basis_set + "-0-id"] = basis_objects[0].pk
        self.assert_status_code(
            "post", reverse("rights:edit", kwargs={"pk": rights_statement.pk}),
            updated_basis_data, 302)
        self.assertEqual(
            len(RightsStatement.objects.all()),
            previous_length + 1,
            "Another rights statement was mistakenly created")

        invalid_data = updated_basis_data
        del invalid_data["rights_basis"]
        del invalid_data["rights_granted-0-act"]
        self.assert_status_code(
            "post", reverse("rights:edit", kwargs={"pk": rights_statement.pk}),
            invalid_data, 200)
        self.assert_status_code(
            "post",
            "{}{}".format(reverse("rights:add"), "?org={}".format(post_organization.pk)),
            invalid_data, 200)

    def test_ajax_requests(self):
        """Asserts that requests made with javascript are processed correctly."""
        rights_statement = RightsStatement.objects.last()
        delete_request = self.client.get(
            reverse(
                "rights:api", kwargs={"pk": rights_statement.pk, "action": "delete"}), {},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(delete_request.status_code, 200)
        resp = delete_request.json()
        self.assertEqual(resp["success"], 1)
        non_ajax_request = self.client.get(
            reverse("rights:api", kwargs={"pk": rights_statement.pk, "action": "delete"}))
        self.assertEqual(non_ajax_request.status_code, 404)
