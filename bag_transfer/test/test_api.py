import json
from datetime import datetime
from os.path import join
from unittest.mock import patch

from django.http import HttpRequest
from django.test import TestCase, modify_settings
from django.urls import reverse
from rac_schema_validator import is_valid

from bag_transfer.accession.models import Accession
from bag_transfer.authentication import CognitoAppAuthentication
from bag_transfer.models import (Application, BAGLog, Organization, Transfer,
                                 User)
from bag_transfer.test.helpers import TestMixin


class APITest(TestMixin, TestCase):
    fixtures = ["complete.json"]

    def test_create_transfer(self):
        """Asserts transfer is created as expected via POST request."""
        data = {
            "organization": "/api/orgs/1/",
            "file_path": "/foo/bar",
            "file_size": 123456789,
            "file_upload_time": datetime.now(),
            "identifier": "transfer_id",
            "file_type": "tar",
            "bag_it_name": "bag_it_name",
        }
        created = self.client.post(
            reverse('transfer-list'),
            data=data,
            format="json")
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['identifier'], 'transfer_id')
        self.assertEqual(created.data['organization'], 'http://testserver/api/orgs/1/')
        self.assertEqual(created.data['bag_it_name'], 'bag_it_name')
        self.assertEqual(created.data['process_status'], 20)
        self.assertEqual(created.data['file_size'], 123456789)
        self.assertEqual(created.data['file_type'], 'tar')
        self.assertEqual(created.data['file_upload_time'], '2026-01-01')
        self.assertEqual(created.data['file_path'], '/foo/bar')

    @patch("bag_transfer.lib.cleanup.CleanupRoutine.run")
    def test_update_transfer(self, mock_cleanup):
        """Asserts bad data can be updated."""
        new_values = {
            "process_status": Transfer.ACCESSIONING_STARTED,
            "archivesspace_identifier": "/repositories/2/archival_objects/3",
            "archivesspace_parent_identifier": "/repositories/2/archival_objects/4"
        }

        for transfer in Transfer.objects.all():
            transfer_data = self.client.get(
                reverse("transfer-detail", kwargs={"pk": transfer.pk}), format="json").json()
            transfer_data.update(new_values)

            updated = self.client.put(
                reverse("transfer-detail", kwargs={"pk": transfer.pk}),
                data=json.dumps(transfer_data),
                content_type="application/json")
            self.assertEqual(updated.status_code, 200, updated.data)
            for field in new_values:
                self.assertEqual(updated.data[field], new_values[field], "{} not updated in {}".format(field, updated.data))
            mock_cleanup.assert_called_once()
            mock_cleanup.reset_mock()

    def test_create_event(self):
        """Assert events are created as expected via POST requests"""
        data = {
            "code": "PBAG",
            "transfer": "/api/transfers/1"
        }
        created = self.client.post(
            reverse('baglog-list'),
            data=data,
            format="json")
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['type'], 'Accept')
        self.assertEqual(created.data['summary'], 'Transfer passed BagIt validation')
        self.assertEqual(created.data['object'], 'http://testserver/api/transfers/1/')
        self.assertEqual(created.data['result'], {'name': 'Transfer staged for BagIt Profile validation'})

    def test_find_by_upload_target(self):
        org = Organization.objects.get(pk=1)
        results = self.client.get(f"{reverse('organization-find-by-upload-target')}?upload_target={org.upload_target}")
        self.assertEqual(len(results.data['results']), 1)
        self.assertEqual(results.data['results'][0]['url'], "http://testserver/api/orgs/1/")

        results = self.client.get(f"{reverse('organization-find-by-upload-target')}")
        self.assertEqual(results.status_code, 500)
        self.assertEqual(results.data, {'detail': 'You must include an `upload_target` in the URL params'})

    def test_schema_response(self):
        self.assert_status_code("get", reverse("schema"), 200)

    def test_status_response(self):
        self.assert_status_code("get", reverse("ping"), 200)

    def test_action_endpoints(self):
        """Asserts custom action endpoints return expected status code."""
        org = Organization.objects.get(name="Donor Organization").pk
        self.assert_status_code("get", reverse("organization-bagit-profiles", kwargs={"pk": org}), 200)
        self.assert_status_code("get", reverse("organization-rights-statements", kwargs={"pk": org}), 200)
        self.assert_status_code("get", reverse("user-current"), 200)

    def test_list_views(self):
        """Asserts list endpoints return expected response."""
        for view in ["transfer-list", "accession-list", "baglog-list", "organization-list", "user-list"]:
            self.assert_status_code("get", reverse(view), 200)

    def test_detail_views(self):
        for view, model_cls in [
                ("transfer-detail", Transfer),
                ("accession-detail", Accession),
                ("baglog-detail", BAGLog),
                ("organization-detail", Organization),
                ("user-detail", User)]:
            for obj in model_cls.objects.all():
                self.assert_status_code("get", reverse(view, kwargs={"pk": obj.pk}), 200)

    def test_validation(self):
        """Asserts that endpoint responses are valid against RAC schemas."""
        base_file = open(join('rac_schemas', 'schemas', 'base.json'), 'r')
        base_schema = json.load(base_file)
        base_file.close()
        with open(join('rac_schemas', 'schemas', 'rights_statement.json'), 'r') as object_file:
            object_schema = json.load(object_file)
            for org in Organization.objects.all():
                rights_statements = self.client.get(reverse("organization-rights-statements", kwargs={"pk": org.pk}))
                for statement in rights_statements.json():
                    self.assertTrue(is_valid(statement, object_schema, base_schema))
        for queryset, view, schema in [
                (Transfer.objects.filter(process_status__gte=Transfer.ACCESSIONING_STARTED), "transfer-detail", "aurora_bag"),
                (Accession.objects.all(), "accession-detail", "accession")]:
            with open(join('rac_schemas', 'schemas', f'{schema}.json'), 'r') as object_file:
                object_schema = json.load(object_file)
                for obj in queryset:
                    data = self.client.get(reverse(view, kwargs={"pk": obj.pk})).json()
                    self.assertTrue(is_valid(data, object_schema, base_schema))


class TestAPICognitoAuth(TestMixin, TestCase):
    fixtures = ['complete.json']

    @patch('bag_transfer.middleware.cognito.CognitoMiddleware.get_application')
    @modify_settings(MIDDLEWARE={"append": "bag_transfer.middleware.cognito.CognitoMiddleware"})
    def test_application_auth(self, mock_user):
        """Asserts mixin correctly calls authentication."""
        self.client.get("/api/", content_type="application/json", **{"HTTP_ACCEPT": "application/json"})
        mock_user.assert_called_once()
        self.client.get("/api/", content_type="application/json")
        mock_user.call_count = 1
        self.client.get("/", content_type="application/json", **{"HTTP_ACCEPT": "application/json"})
        mock_user.call_count = 1

    @patch('bag_transfer.authentication.CognitoAppAuthentication.get_auth_token')
    @patch('bag_transfer.authentication.CognitoAppAuthentication.get_claims')
    def test_get_application(self, mock_get_claims, mock_get_token):
        """Asserts get_application method correctly handles exceptions."""
        request = HttpRequest()
        token = "12345"
        exception_msg = "There was an error!"
        mock_get_token.return_value = token
        mock_get_claims.side_effect = Exception(exception_msg)

        with self.assertRaises(Exception) as e:
            CognitoAppAuthentication().get_application(request)
        self.assertTrue(exception_msg in str(e.exception))

        mock_get_claims.side_effect = None
        mock_get_claims.return_value = {}
        with self.assertRaises(Exception) as e:
            CognitoAppAuthentication().get_application(request)
        self.assertTrue("The authentication token does not have claims associated with it." in str(e.exception))

        mock_get_claims.return_value = {"client_id": "foobar"}
        with self.assertRaises(Exception) as e:
            CognitoAppAuthentication().get_application(request)
        self.assertTrue("The application associated with this token does not exist." in str(e.exception))

        app = Application.objects.create(name="foobar", client_id="barbaz")
        mock_get_claims.return_value = {"client_id": "barbaz"}
        returned = CognitoAppAuthentication().get_application(request)
        self.assertEqual(returned.pk, app.pk)

    def test_get_auth_token(self):
        """Asserts Bearer token is correctly parsed."""
        token = "12345"
        request = HttpRequest()
        with self.assertRaises(Exception) as e:
            CognitoAppAuthentication().get_auth_token(request)
        self.assertEqual(str(e.exception), 'Expected an Authorization header but got none.')

        request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        parsed = CognitoAppAuthentication().get_auth_token(request)
        self.assertEqual(parsed, token)

        request.META["HTTP_AUTHORIZATION"] = token
        with self.assertRaises(ValueError):
            CognitoAppAuthentication().get_auth_token(request)
