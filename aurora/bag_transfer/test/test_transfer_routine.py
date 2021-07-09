import os
import random
import shutil

from asterism.file_helpers import remove_file_or_dir
from aurora import settings
from bag_transfer.lib.transfer_routine import TransferRoutine
from bag_transfer.models import Archives, DashboardMonthData, Organization
from bag_transfer.test import helpers
from django.test import TestCase


class TransferRoutineTestCase(TestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        Archives.objects.all().delete()
        DashboardMonthData.objects.all().delete()
        self.reset_org_dirs(Organization.objects.all())

    def test_setup_routine(self):
        self.routine = TransferRoutine()
        self.sub_test_db_has_active_orgs()
        self.sub_test_verify_organizations_paths()
        self.sub_test_no_orgs_with_dirs()
        self.sub_test_contents_dictionary()

    # def test_run_routine(self):
    #
    #     test_on_BagChecker = [r[0] for r in setup.BAGS_REF if len(r) > 2 and r[2]]
    #     test_on_transfer_routine = [r[0] for r in setup.BAGS_REF if len(r) > 3 and r[3]]
    #
    #     for ref in setup.BAGS_REF:
    #
    #         helpers.create_target_bags(ref[0], settings.TEST_BAGS_DIR, self.orgs[0])
    #         tr = TransferRoutine()
    #         self.assertTrue(tr.setup_routine(), "Transfer routine did not set up properly")
    #         self.assertTrue(isinstance(tr.run_routine(), dict), "Expected transfer routine to produce a dict, got {} instead".format(tr.run_routine()))
    #
    #         for trans in tr.transfers:
    #             if not trans["file_name"].startswith(ref[0]):
    #                 continue
    #             if ref[0] == "valid_bag":
    #                 self.assertFalse(trans["auto_fail"])
    #             else:
    #                 if ref[0] in test_on_transfer_routine:
    #                     self.assertTrue(trans["auto_fail"])
    #                     self.assertEqual(ref[1], trans["auto_fail_code"])
    #
    #             archive = Archives.initial_save(
    #                 self.orgs[0],
    #                 None,
    #                 trans["file_path"],
    #                 trans["file_size"],
    #                 trans["file_modtime"],
    #                 Archives().gen_identifier(),
    #                 trans["file_type"],
    #                 trans["bag_it_name"])
    #             archive.organization.name = "Ford Foundation"
    #             archive.organization.save()
    #
    #             self.assertIsNot(False, archive.machine_file_identifier, "Expected bag identifier to exist")
    #
    #             if trans["auto_fail"]:
    #                 continue
    #
    #             bag = BagChecker(archive)
    #             passed_all_results = bag.bag_passed_all()
    #
    #             if ref[0] in ["valid_bag", "no_metadata_file"]:
    #                 self.assertTrue(passed_all_results, "Bag unexpectedly invalid")
    #             else:
    #                 self.assertFalse(passed_all_results, "Bag unexpectedly valid")
    #                 if ref[0] in test_on_BagChecker:
    #                     self.assertEqual(ref[1], bag.ecode)
    #
    #             # deleting path in processing and tmp dir
    #             remove_file_or_dir(
    #                 os.path.join(settings.TRANSFER_EXTRACT_TMP, archive.bag_it_name))
    #             remove_file_or_dir(archive.machine_file_path)

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

    def sub_test_verify_organizations_paths(self):
        """Asserts that TransferRoutine setup checks for organization directories."""
        self.routine.has_active_organizations()
        original_active_count = len(self.routine.active_organizations)
        last_org = self.routine.active_organizations[0]
        last_org_upload_paths = last_org.org_machine_upload_paths()
        random_index = random.randrange(0, len(last_org_upload_paths))
        remove_file_or_dir(last_org_upload_paths[random_index])
        self.routine.verify_organizations_paths()
        self.assertEqual(
            original_active_count - 1, len(self.routine.active_organizations),
            "Expected one organization to have been removed from TransferRoutine.active_organizations")
        self.reset_org_dirs(last_org)

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

    def sub_test_contents_dictionary(self):
        """Asserts the TransferRoutine contents dictionary is correctly set up."""
        self.assertFalse(self.routine.setup_routine(), "Expected TransferRoutine setup to fail because there are no transfers in the transfer directory")
        organization = random.choice(Organization.objects.filter(is_active=True))
        helpers.create_target_bags("valid_bag", settings.TEST_BAGS_DIR, organization)
        self.assertTrue(self.routine.setup_routine(), "Expected TransferRoutine setup to succeed.")
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
            for dir in org.org_machine_upload_paths():
                if os.path.exists(dir):
                    shutil.rmtree(dir)

    def create_org_dirs(self, org_list):
        for org in org_list:
            for dir in org.org_machine_upload_paths():
                if not os.path.exists(dir):
                    os.makedirs(dir)
