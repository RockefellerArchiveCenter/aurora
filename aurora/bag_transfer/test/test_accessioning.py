import json
import random
from datetime import datetime
from unittest.mock import patch

from bag_transfer.accession.models import Accession
from bag_transfer.accession.views import AccessionCreateView
from bag_transfer.models import BAGLog, LanguageCode, RecordCreators, Transfer
from bag_transfer.test import helpers
from django.test import TestCase
from django.urls import reverse


class AccessioningTestCase(helpers.TestMixin, TestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        super().setUp()
        self.to_accession = Transfer.objects.filter(process_status__lt=Transfer.ACCEPTED)

    def test_views(self):
        """Tests views to ensure exceptions are raised appropriately"""
        transfer_ids = [str(a.id) for a in self.to_accession]
        self.list_view(",".join(transfer_ids))
        self.create_view(transfer_ids)
        self.detail_view()
        self.ajax_list_view(transfer_ids)
        self.ajax_add_view()

    def test_grouped_transfer_data(self):
        """Tests the grouping of transfer data."""
        notes, dates, descriptions_list, languages_list, extent_files, extent_size, record_type = AccessionCreateView().grouped_transfer_data(self.to_accession)
        self.assertEqual(len(notes["appraisal"]), len(self.to_accession))
        self.assertTrue([isinstance(n, str) for n in notes["appraisal"]])
        self.assertEqual(len(dates["start"]), len(self.to_accession))
        self.assertTrue([isinstance(d, datetime) for d in dates["start"]])
        self.assertEqual(len(dates["end"]), len(self.to_accession))
        self.assertTrue([isinstance(d, datetime) for d in dates["end"]])
        self.assertEqual(len(descriptions_list), len(self.to_accession))
        self.assertTrue([isinstance(d, str) for d in descriptions_list])
        self.assertEqual(set(languages_list), set(["eng", "spa"]))
        self.assertTrue(isinstance(extent_files, int))
        self.assertTrue(isinstance(extent_size, int))
        self.assertTrue(isinstance(record_type, str))

    def test_parse_language(self):
        """Tests the parsing of a single language object from a list."""
        for list, expected in [([], "und"), (["eng"], "eng"), (["eng", "spa"], "mul")]:
            language = AccessionCreateView().parse_language(list)
            self.assertTrue(isinstance(language, LanguageCode))
            self.assertEqual(language.code, expected)

    def test_parse_title(self):
        """Tests the construction of a title from transfer data."""
        for organization, record_type, creators_list, expected in [
                ("Village Green Preservation Society", "grant records", "Ray Davies", "Village Green Preservation Society, Ray Davies grant records"),
                ("Village Green Preservation Society", "grant records", "", "Village Green Preservation Society grant records"), ]:
            title = AccessionCreateView().parse_title(organization, record_type, creators_list)
            self.assertEqual(title, expected)

    def test_update_accession_rights(self):
        """Tests that accessions are correctly linked to rights statements."""
        rights_statements = [helpers.create_rights_statement() for x in range(5)]
        accession_data = helpers.get_accession_data()
        accession = Accession.objects.create(**accession_data)
        AccessionCreateView().update_accession_rights(rights_statements, accession)
        self.assertTrue([r.accession == accession for r in rights_statements])

    def test_rights_statement_notes(self):
        rights_basis_list = ["Copyright", "Statute", "License", "Other"]
        rights_statements = [helpers.create_rights_statement(rights_basis=basis) for basis in rights_basis_list]
        for statement in rights_statements:
            helpers.create_test_rights_info(statement)
            helpers.create_test_rights_granted(statement)
        notes = AccessionCreateView().rights_statement_notes(rights_statements)
        for basis in rights_basis_list:
            key = basis.lower()
            self.assertEqual(len(notes[key]), 2)
            self.assertTrue(isinstance(n, str) for n in notes[key])

    @patch("bag_transfer.lib.clients.ArchivesSpaceClient.get_resource")
    def ajax_add_view(self, mock_as):
        mock_as.return_value = {"title": "foo", "id_0": "1", "uri": "foobar"}
        response = self.assert_status_code(
            "get", reverse("accession:add"), 200, data={"resource_id": 1}, ajax=True)
        data = json.loads(response.content)
        self.assertEqual(data["success"], 1)
        self.assertEqual(data["title"], "foo (1)")
        self.assertEqual(data["uri"], "foobar")

        mock_as.side_effect = Exception("mock exception")
        response = self.assert_status_code(
            "get", reverse("accession:add"), 200, data={"resource_id": 1}, ajax=True)
        data = json.loads(response.content)
        self.assertEqual(data["success"], 0)

    @patch("requests.post")
    def ajax_list_view(self, transfer_ids, mock_post):
        """Tests the AJAX logic branch of accession list view."""
        mock_post.status_code = 200
        accession = random.choice(Accession.objects.all())
        list_response = self.assert_status_code(
            "get", reverse("accession:list"), 200, data={"accession_id": accession.pk}, ajax=True)
        accession.refresh_from_db()  # refresh to pick up changes
        self.assertEqual(json.loads(list_response.content)["success"], 1)
        self.assertEqual(accession.process_status, Accession.DELIVERED)

        accession_id = 10000
        response = self.assert_status_code(
            "get", reverse("accession:list"), 200, data={"accession_id": accession_id}, ajax=True)
        self.assertEqual(json.loads(response.content)["success"], 0)

    def list_view(self, id_list):
        response = self.assert_status_code("get", reverse("accession:list"), 200)
        self.assertEqual(len(response.context["uploads"]), 4)

    @patch("requests.post")
    def create_view(self, id_list, mock_post):
        """Assert add view handles data and exceptions correctly."""
        self.assert_status_code("get", reverse("accession:add"), 200, data={"transfers": ",".join(id_list)})

        mock_post.status_code = 200
        joined_list = ",".join(id_list)
        accession_data = helpers.get_accession_form_data(
            creator=random.choice(RecordCreators.objects.all()))
        self.assert_status_code("post", "{}?transfers={}".format(reverse("accession:add"), joined_list), 302, data=accession_data)
        for acc in Accession.objects.all():
            self.assertTrue(acc.process_status >= Accession.CREATED)
        for arc_id in id_list:
            transfer = Transfer.objects.get(pk=arc_id)
            self.assertEqual(
                transfer.process_status, Transfer.ACCESSIONING_STARTED)
            self.assertEqual(
                len(BAGLog.objects.filter(transfer=transfer, code__code_short="BACC")), 1)

        mock_post.side_effect = Exception("mock exception")  # have secondary POST throw exception
        self.assert_status_code("post", "{}?transfers={}".format(reverse("accession:add"), joined_list), 302, data=accession_data)

        del accession_data["title"]  # try to submit invalid data
        self.assert_status_code("post", "{}?transfers={}".format(reverse("accession:add"), joined_list), 200, data=accession_data)

    def detail_view(self):
        """Assert Accessions detail view returns correct response code."""
        accession = random.choice(Accession.objects.all())
        self.assert_status_code("get", reverse("accession:detail", kwargs={"pk": accession.pk}), 200)
