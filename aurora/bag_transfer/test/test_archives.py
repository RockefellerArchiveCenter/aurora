import random
from unittest.mock import PropertyMock, patch

from bag_transfer.models import (Archives, BagInfoMetadata, BAGLog,
                                 BAGLogCodes, LanguageCode, Organization,
                                 RecordCreators, User)
from bag_transfer.rights.models import RightsStatement
from bag_transfer.test.helpers import TestMixin
from django.test import TestCase
from django.urls import reverse


class BagTestCase(TestMixin, TestCase):
    fixtures = ["complete.json"]

    def assert_all_views(self, organization=None):
        archives = Archives.objects.filter(organization=organization) if organization else Archives.objects.all()
        for view in ["transfers:list", "transfers:data", "transfers:datatable", "app_home"]:
            self.assert_status_code("get", reverse(view), 200)
        for arc in archives:
            self.assert_status_code("get", reverse("transfers:detail", kwargs={"pk": arc.pk}), 200)
        self.assert_status_code("get", "{}?q=user".format(reverse("transfers:datatable")), 200)

    def test_views(self):
        """Asserts views return expected responses for admin and donor users."""
        self.assert_all_views()
        self.client.logout()
        donor_user = User.objects.get(username="donor")
        self.client.force_login(donor_user)
        self.assert_all_views(donor_user.organization)

    def test_model_methods(self):
        """Tests Archives model methods."""
        self.bag_or_failed_name()
        self.errors()
        self.failures()
        self.additional_errors()
        self.add_autofail_information()
        self.get_or_create_mtm_objects()
        self.save_bag_data()
        self.records_creators()
        self.assign_rights()  # 403-452

    @patch("bag_transfer.models.Archives.bag_data", new_callable=PropertyMock)
    def bag_or_failed_name(self, mock_bag_data):
        """Asserts bag_or_failed_name returns expected values."""
        for instance, bag_data, expected_name in [
                (Archives(bag_it_valid=False, machine_file_path="/baz/bar/foo"), None, "foo"),
                (Archives(bag_it_valid=True), {"title": "foo", "external_identifier": "bar"}, "foo (bar)"),
                (Archives(bag_it_valid=True), {"title": "foo"}, "foo")]:
            mock_bag_data.return_value = bag_data
            self.assertEqual(
                instance.bag_or_failed_name, expected_name,
                "Expected bag_or_failed_name to be {}, got {} instead".format(expected_name, instance.bag_or_failed_name))

    def errors(self):
        archive = random.choice(Archives.objects.filter(bag_it_valid=True))
        self.assertEqual(archive.errors, None)
        code = BAGLogCodes.objects.filter(code_type="BE").first()
        BAGLog.objects.create(archive=archive, log_info="foo", code=code)
        archive.bag_it_valid = False
        self.assertEqual(len(archive.errors), 1)

    def failures(self):
        archive = random.choice(Archives.objects.filter(bag_it_valid=True).exclude(events__code__code_type__in=["BE"]))
        self.assertFalse(archive.failures)
        self.assertFalse(archive.last_failure)
        archive.bag_it_valid = False
        self.assertFalse(archive.failures)
        self.assertFalse(archive.last_failure)
        code = BAGLogCodes.objects.filter(code_type="BE").first()
        BAGLog.objects.create(archive=archive, log_info="foo", code=code)
        BAGLog.objects.create(archive=archive, log_info="bar", code=code)
        self.assertTrue(isinstance(archive.last_failure, BAGLog))
        self.assertEqual(len(archive.failures), 2)

    @patch("bag_transfer.models.Archives.failures", new_callable=PropertyMock)
    def additional_errors(self, mock_failures):
        archive = random.choice(Archives.objects.all())
        archive.additional_error_info = "foo"
        self.assertEqual(archive.additional_errors, ["foo"])
        archive.additional_error_info = None
        for return_value, expected in [
                (None, []),
                ([BAGLog(code=BAGLogCodes(code_short="BZIP2"))], ["Transfer contained more than one top level directory"]),
                ([BAGLog(code=BAGLogCodes(code_short="BTAR2"))], ["Transfer contained more than one top level directory"]),
                ([BAGLog(code=BAGLogCodes(code_short="FSERR"))], []),
                ([BAGLog(code=BAGLogCodes(code_short="BZIP2")), BAGLog(code=BAGLogCodes(code_short="FSERR"))],
                    ["Transfer contained more than one top level directory"])]:
            mock_failures.return_value = return_value
            self.assertEqual(
                archive.additional_errors, expected,
                "additional_errors returned {}, expecting {}".format(
                    archive.additional_errors, expected))

    def add_autofail_information(self):
        for instance, information in [
                ({"auto_fail_code": "VIRUS", "virus_scanresult": ["foo"]}, "Virus found in: foo"),
                ({"auto_fail_code": "FSERR", "file_size": 4000}, "Bag size (4000) is larger than maximum allowed size (2000000000000)")]:
            arch = Archives()
            arch.add_autofail_information(instance)
            self.assertEqual(arch.additional_error_info, information)

    def get_or_create_mtm_objects(self):
        for cls, model_field, field_data, expected_len in [
                (RecordCreators, "name", ["foo", "bar"], 2),
                (LanguageCode, "code", "eng ", 1)]:
            objects = Archives().get_or_create_mtm_objects(cls, model_field, field_data)
            self.assertEqual(len(objects), expected_len)
            self.assertTrue([isinstance(o, cls) for o in objects])

    def save_bag_data(self):
        metadata = {
            "Source_Organization": "Donor Organization",
            "External_Identifier": "123456",
            "Internal_Sender_Description": "foobar",
            "Title": "foobar",
            "Date_Start": "2021-01-01",
            "Date_End": "2021-12-01",
            "Record_Type": "grants",
            "Bagging_Date": "2021-12-01",
            "Bag_Count": "1 of 2",
            "Bag_Group_Identifier": "12345",
            "Payload_Oxum": "22.12",
            "BagIt_Profile_Identifier": "",
            "Record_Creators": ["foo", "bar"],
            "Language": "eng"
        }
        archive = random.choice(Archives.objects.all())
        BagInfoMetadata.objects.filter(archive=archive).delete()
        archive.save_bag_data(metadata)
        self.assertEqual(len(BagInfoMetadata.objects.filter(archive=archive)), 1)
        self.assertFalse(archive.save_bag_data(None))

    def records_creators(self):
        archive = random.choice(Archives.objects.all())
        creators = archive.records_creators
        self.assertTrue(isinstance(creators, list))
        self.assertTrue([isinstance(c, RecordCreators) for c in creators])

    def assign_rights(self):
        org = Organization.objects.get(name="Donor Organization")
        archive = random.choice(Archives.objects.filter(organization=org))
        RightsStatement.objects.filter(archive=archive).delete()
        expected_len = len(RightsStatement.objects.filter(
            organization=org,
            applies_to_type__name=archive.bag_data["record_type"],
            archive__isnull=True))
        archive.assign_rights()
        self.assertEqual(
            len(archive.rights_statements.all()), expected_len,
            "Expected {} rights statements to be assigned, but got {}".format(expected_len, len(archive.rights_statements.all())))
