import random

from asterism.file_helpers import remove_file_or_dir
from bag_transfer.lib.transfer_routine import TransferRoutine
from bag_transfer.test import helpers
from django.test import TestCase


class TransferRoutineTestCase(TestCase):
    def setUp(self):
        self.orgs = helpers.create_test_orgs(org_count=3)

    def test_setup_routine(self):
        self.TR = TransferRoutine()

        # has active orgs
        self.sub_test_db_has_active_orgs()

        # verify orgs upload paths exist and if 1 doesn't then drop for active dict
        self.sub_test_verify_organizations_paths()

        # still have active orgs

        # builds content dict

    # def test_run_routine(self):
    #
    #     test_on_bagchecker = [r[0] for r in setup.BAGS_REF if len(r) > 2 and r[2]]
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
    #             bag = bagChecker(archive)
    #             passed_all_results = bag.bag_passed_all()
    #
    #             if ref[0] in ["valid_bag", "no_metadata_file"]:
    #                 self.assertTrue(passed_all_results, "Bag unexpectedly invalid")
    #             else:
    #                 self.assertFalse(passed_all_results, "Bag unexpectedly valid")
    #                 if ref[0] in test_on_bagchecker:
    #                     self.assertEqual(ref[1], bag.ecode)
    #
    #             # deleting path in processing and tmp dir
    #             remove_file_or_dir(
    #                 os.path.join(settings.TRANSFER_EXTRACT_TMP, archive.bag_it_name))
    #             remove_file_or_dir(archive.machine_file_path)

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)

    def sub_test_db_has_active_orgs(self):
        self.change_all_orgs_in_list_status(
            self.orgs, False
        )  # turns all test orgs inactive
        self.assertFalse(self.TR.setup_routine())  # test setup catches inactives
        self.assertTrue(self.TR.has_setup_err)  # 2nd check that it was an error
        self.change_all_orgs_in_list_status(self.orgs, True)  # reverts back to True

    def sub_test_verify_organizations_paths(self):
        """removes directory from an org and check to see if item removed from active orgs"""
        self.TR.has_active_organizations()  # resets the active orgs
        original_active_count = len(self.TR.active_organizations)
        last_org = self.TR.active_organizations[0]
        last_org_upload_paths = last_org.org_machine_upload_paths()
        random_index = random.randrange(0, len(last_org_upload_paths))
        remove_file_or_dir(last_org_upload_paths[random_index])
        self.TR.verify_organizations_paths()
        self.assertNotEqual(original_active_count, len(self.TR.active_organizations))

    def change_all_orgs_in_list_status(self, orgs={}, Status=False):
        for org in orgs:
            org.is_active = Status
            org.save()
