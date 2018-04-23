from django.test import TransactionTestCase

from orgs import test_helpers

from orgs.lib.transfer_routine import *
from orgs.lib.files_helper import *

import random


class TransferRoutineTestCase(TransactionTestCase):
    def setUp(self):
        self.orgs = test_helpers.create_test_orgs(org_count=3)

    def test_setup_routine(self):
        self.TR = TransferRoutine()

        # has active orgs
        self.sub_test_db_has_active_orgs()

        # verify orgs upload paths exist and if 1 doesn't then drop for active dict
        self.sub_test_verify_organizations_paths()

        # still have active orgs

        # builds content dict

    def test_run_routine(self):
        pass

    def tearDown(self):
        test_helpers.delete_test_orgs(self.orgs)

    def sub_test_db_has_active_orgs(self):
        self.change_all_orgs_in_list_status(self.orgs, False)   # turns all test orgs inactive
        self.assertFalse(self.TR.setup_routine())               # test setup catches inactives
        self.assertTrue(self.TR.has_setup_err)                  # 2nd check that it was an error
        self.change_all_orgs_in_list_status(self.orgs, True)    #reverts back to True

    def sub_test_verify_organizations_paths(self):
        """removes directory from an org and check to see if item removed from active orgs"""
        self.TR.has_active_organizations()          #resets the active orgs
        original_active_count = len(self.TR.active_organizations)
        last_org = self.TR.active_organizations[0]
        last_org_upload_paths = last_org.org_machine_upload_paths()
        random_index = random.randrange(0,len(last_org_upload_paths))
        remove_file_or_dir(last_org_upload_paths[random_index])
        self.TR.verify_organizations_paths()
        self.assertNotEqual(original_active_count,len(self.TR.active_organizations))

    def change_all_orgs_in_list_status(self, orgs ={}, Status=False):
        for org in orgs:
            org.is_active = Status
            org.save()
