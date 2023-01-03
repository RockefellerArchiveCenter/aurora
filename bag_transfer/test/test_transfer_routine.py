import os
import random
import shutil
from unittest.mock import patch

from asterism.file_helpers import remove_file_or_dir
from django.conf import settings
from django.test import TestCase

from bag_transfer.lib.bag_checker import BagChecker
from bag_transfer.lib.transfer_routine import (TransferFileObject,
                                               TransferRoutine,
                                               TransferRoutineException)
from bag_transfer.models import (DashboardMonthData, Organization, Transfer,
                                 User)
from bag_transfer.test import helpers


class TransferRoutineTestCase(helpers.TestMixin, TestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        Transfer.objects.all().delete()
        DashboardMonthData.objects.all().delete()
        self.reset_org_dirs(Organization.objects.all())

    def test_passes_filename(self):
        """Asserts passes_filename helper correctly evaluates files."""
        for file_path in ["/data/foo/bar.tar", "/data/foo/bar"]:
            output = TransferFileObject(file_path, random.choice(Organization.objects.all()).machine_name).passes_filename()
            self.assertTrue(output, f"Expected {file_path} test to return True.")

        for file_path in ["/data/foo/ba>", "/data/foo/ba<", "/data/foo/b!a", "/data/foo/b|a", "/data/foo/ba:", "/data/foo/ba?", "/data/foo/ba*"]:
            with self.assertRaises(TransferRoutineException) as err:
                TransferFileObject(file_path, random.choice(Organization.objects.all()).machine_name).passes_filename()
            self.assertEqual(err.exception.code, TransferFileObject.AUTO_FAIL_BFNM)

    def test_setup_routine(self):
        """Asserts TransferRoutine sets up correctly."""
        self.routine = TransferRoutine()
        self.sub_test_db_has_active_orgs()
        self.sub_test_verify_organizations_paths()
        self.sub_test_no_orgs_with_dirs()
        self.sub_test_no_processible()
        self.sub_test_contents_dictionary()

    def test_run_routine(self):
        """Asserts TransferRoutine handles valid and invalid bags."""
        test_on_BagChecker = [r[0] for r in helpers.BAGS_REF if len(r) > 2 and r[2]]
        test_on_transfer_routine = [r[0] for r in helpers.BAGS_REF if len(r) > 3 and r[3]]
        org = random.choice(Organization.objects.all())
        user = random.choice(User.objects.filter(organization=org))

        for prefix, error, *rest in helpers.BAGS_REF:

            helpers.create_target_bags(
                prefix, settings.TEST_BAGS_DIR, org, user.username)
            transfers = TransferRoutine().run_routine()
            self.assertTrue(
                isinstance(transfers, list),
                "Expected transfer routine to produce a list, got {} instead".format(transfers))

            for trans in transfers:
                if not trans["bag_it_name"].startswith(prefix):
                    continue
                if prefix == "valid_bag":
                    self.assertFalse(trans["auto_fail"])
                else:
                    if prefix in test_on_transfer_routine:
                        self.assertTrue(trans["auto_fail"])
                        self.assertEqual(error, trans["auto_fail_code"])

                transfer = Transfer.objects.create(
                    organization=org,
                    machine_file_path=trans["machine_file_path"],
                    machine_file_size=trans["machine_file_size"],
                    machine_file_upload_time=trans["machine_file_upload_time"],
                    machine_file_identifier=trans["machine_file_identifier"],
                    machine_file_type=trans["machine_file_type"],
                    bag_it_name=trans["bag_it_name"])

                if trans["auto_fail"]:
                    continue

                bag = BagChecker(transfer)
                passed_all_results = bag.bag_passed_all()

                if prefix in ["valid_bag", "no_metadata_file"]:
                    self.assertTrue(passed_all_results, "Bag unexpectedly invalid")
                else:
                    self.assertFalse(passed_all_results, "Bag unexpectedly valid")
                    if prefix in test_on_BagChecker:
                        self.assertEqual(error, bag.ecode)

                # deleting binary
                remove_file_or_dir(transfer.machine_file_path)

    def sub_test_db_has_active_orgs(self):
        """Asserts TransferRoutine setup handles inactive organizations."""
        self.change_all_orgs_in_list_status(Organization.objects.all(), False)
        self.assertFalse(
            self.routine.setup_routine(),
            "Expected TransferRoutine setup to return False because there are no active orgs")
        self.assertTrue(
            self.routine.has_setup_err,
            "Expected TransferRoutine.has_setup_err to be true because there are no active orgs")
        self.change_all_orgs_in_list_status(Organization.objects.all(), True)

    @patch("bag_transfer.lib.transfer_routine.s3_bucket_exists")
    def sub_test_verify_organizations_paths(self, mock_bucket):
        """Asserts that TransferRoutine setup checks for organization directories."""
        self.change_all_orgs_in_list_status(Organization.objects.all(), True)
        original_active_count = len(Organization.objects.all())
        active_orgs = self.routine.verify_organizations_paths(Organization.objects.all())
        self.assertEqual(
            original_active_count,
            len(active_orgs),
            "Expected active organizations to have remained the same")

        with self.settings(S3_USE=True):
            active_orgs = self.routine.verify_organizations_paths(Organization.objects.all())
            self.assertEqual(
                original_active_count,
                len(active_orgs),
                "Expected active organizations to have remained the same")

            mock_bucket.return_value = False
            active_orgs = self.routine.verify_organizations_paths(Organization.objects.all())
            self.assertEqual(0, len(active_orgs),
                             "Expected no active organizations to be available")

        last_org = random.choice(Organization.objects.all())
        remove_file_or_dir(last_org.upload_target)
        active_orgs = self.routine.verify_organizations_paths(Organization.objects.all())
        self.assertEqual(
            original_active_count - 1, len(active_orgs),
            "Expected one organization to have been removed from TransferRoutine.active_organizations")
        self.reset_org_dirs([last_org])

    def sub_test_no_orgs_with_dirs(self):
        self.change_all_orgs_in_list_status(Organization.objects.all(), True)
        self.delete_org_dirs(Organization.objects.all())
        self.assertFalse(
            self.routine.setup_routine(),
            "Expected TransferRoutine setup to fail because there are no orgs with directories")
        self.assertTrue(
            self.routine.has_setup_err,
            "Expected TransferRoutine.has_setup_err to be true because there are no orgs with directories")
        self.create_org_dirs(Organization.objects.all())

    def sub_test_no_processible(self):
        """Asserts that TransferRoutines without files end gracefully."""
        self.assertFalse(
            self.routine.setup_routine(),
            "Expected TransferRoutine setup to fail because there are no transfers in the transfer directory")
        self.assertFalse(
            self.routine.has_setup_err,
            "Expected TransferRoutine.has_setup_err to be False because there are no transfers in the transfer directory")

    @patch("boto3.client")
    def sub_test_contents_dictionary(self, mock_boto):
        """Asserts the TransferRoutine contents dictionary is correctly set up."""
        organization = random.choice(Organization.objects.filter(is_active=True))
        user = random.choice(User.objects.filter(organization=organization))
        bag_name = "valid_bag"
        helpers.create_target_bags(bag_name, settings.TEST_BAGS_DIR, organization, username=user.username)
        self.assertTrue(self.routine.setup_routine(), "Expected TransferRoutine setup to succeed.")
        self.assertTrue(
            isinstance(self.routine.routine_contents_dictionary, dict),
            "Expecting TransferRoutine.routine_contents_dictionary to be a dict")

        with self.settings(S3_USE=True):
            mock_boto().get_paginator().paginate.return_value = [{"KeyCount": 1, "Contents": [{"Key": "valid_bag.tar"}]}]
            self.assertTrue(self.routine.setup_routine(), "Expected TransferRoutine setup to succeed.")
            self.assertTrue(
                isinstance(self.routine.routine_contents_dictionary, dict),
                "Expecting TransferRoutine.routine_contents_dictionary to be a dict")

        self.reset_org_dirs(Organization.objects.all())

    def change_all_orgs_in_list_status(self, orgs={}, Status=False):
        """Helper function to change the status of organizations."""
        for org in orgs:
            org.is_active = Status
            org.save()

    def reset_org_dirs(self, org_list):
        self.delete_org_dirs(org_list)
        self.create_org_dirs(org_list)

    def delete_org_dirs(self, org_list):
        for org in org_list:
            if os.path.exists(org.upload_target):
                shutil.rmtree(org.upload_target)

    def create_org_dirs(self, org_list):
        for org in org_list:
            if not os.path.exists(org.upload_target):
                os.makedirs(org.upload_target)
