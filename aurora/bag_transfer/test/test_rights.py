import random

from bag_transfer.models import Archives
from bag_transfer.rights.models import RightsStatement
from bag_transfer.test import helpers, setup
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse


class RightsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.record_types = helpers.create_test_record_types(setup.record_types)
        self.orgs = helpers.create_test_orgs(org_count=1)
        self.archives = helpers.create_test_archives(
            organization=self.orgs[0],
            process_status=Archives.TRANSFER_COMPLETED,
            count=10)
        for archive in self.archives:
            helpers.create_test_baginfometadatas(archive)
        self.user = helpers.create_test_user(
            username=settings.TEST_USER["USERNAME"],
            password=settings.TEST_USER["PASSWORD"],
            org=random.choice(self.orgs),
            groups=helpers.create_test_groups(["managing_archivists"]),
            is_staff=True)

    def test_rights(self):
        for record_type in self.record_types:
            helpers.create_rights_statement(
                record_type=record_type,
                org=random.choice(self.orgs),
                rights_basis=random.choice(setup.rights_bases))
        self.assertEqual(len(RightsStatement.objects.all()), len(self.record_types))

        for rights_statement in RightsStatement.objects.all():
            self.assemble_rights_statement(rights_statement)

        # Assign rights statements to archives
        for archive in self.archives:
            assign = archive.assign_rights()
            self.assertTrue(assign)

        # Rights statements are cloned when assigned, so we should have more of them now
        assigned_length = len(RightsStatement.objects.all())
        self.assertEqual(assigned_length, len(setup.record_types) + len(self.archives))

        # Test GET views
        self.get_requests()

        # Test POST views
        # self.post_requests()

        # Delete rights statements via AJAX
        self.ajax_requests()

        # Delete rights statement
        to_delete = random.choice(RightsStatement.objects.all())
        self.assertTrue(to_delete.delete())
        # self.assertEqual(len(RightsStatement.objects.all()), assigned_length - 1)

    #############################################
    # Functions used in Rights Statements tests #
    #############################################

    def assemble_rights_statement(self, rights_statement):
        helpers.create_rights_info(rights_statement=rights_statement)
        helpers.create_rights_granted(
            rights_statement=rights_statement, granted_count=random.randint(1, 2)
        )

        # Make sure correct rights info objects were assigned
        rights_basis_type = setup.get_rights_basis_type(rights_statement)
        self.assertIsInstance(
            rights_statement.get_rights_info_object(), rights_basis_type
        )

        # Make sure RightsGranted objects were created
        self.assertIsNot(False, rights_statement.get_rights_granted_objects())

    def get_requests(self):
        self.client.login(
            username=self.user.username, password=settings.TEST_USER["PASSWORD"]
        )
        for view in ["rights:edit", "rights:detail"]:
            rights_statement = random.choice(RightsStatement.objects.all())
            response = self.client.get(
                reverse(view, kwargs={"pk": rights_statement.pk}))
            self.assertEqual(response.status_code, 200)
        add_response = self.client.get(reverse("rights:add"), {"org": self.orgs[0].pk})
        self.assertEqual(add_response.status_code, 200)

        resp = self.client.get(
            reverse("organization-rights-statements", kwargs={"pk": self.orgs[0].pk}))
        self.assertEqual(resp.status_code, 200)

    def post_requests(self):
        # Creating new RightsStatements
        post_organization = random.choice(self.orgs)
        new_basis_data = random.choice(setup.basis_data)
        new_basis_data["organization"] = post_organization.pk
        new_basis_data.update(setup.grant_data)
        previous_length = len(RightsStatement.objects.all())
        new_request = self.client.post(
            "{}{}".format(
                reverse("rights:add"), "?org={}".format(post_organization.pk)),
            new_basis_data)
        self.assertEqual(new_request.status_code, 302, "Request was not successful")
        self.assertEqual(
            len(RightsStatement.objects.all()),
            previous_length + 1,
            "{} Rights Statements were created, correct number is 1".format(
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
        update_request = self.client.post(
            reverse("rights:edit", kwargs={"pk": rights_statement.pk}),
            updated_basis_data)
        self.assertEqual(update_request.status_code, 302, "Request was not redirected")
        self.assertEqual(
            len(RightsStatement.objects.all()),
            previous_length + 1,
            "Another rights statement was mistakenly created")

    def ajax_requests(self):
        rights_statement = RightsStatement.objects.last()
        delete_request = self.client.get(
            reverse(
                "rights:api", kwargs={"pk": rights_statement.pk, "action": "delete"}),
            {},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(delete_request.status_code, 200)
        resp = delete_request.json()
        self.assertEqual(resp["success"], 1)
        non_ajax_request = self.client.get(
            reverse(
                "rights:api",
                kwargs={"pk": rights_statement.pk, "action": "delete"}))
        self.assertEqual(non_ajax_request.status_code, 404)

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
