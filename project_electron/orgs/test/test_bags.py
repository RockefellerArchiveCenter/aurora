# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pwd
from django.test import TransactionTestCase
from django.conf import settings
from orgs import test_helpers
from orgs.test.setup_tests import *
from transfer_app.lib.transfer_routine import *
from transfer_app.lib.files_helper import *
from transfer_app.lib.bag_checker import bagChecker
from orgs.models import Archives


class BagTestCase(TransactionTestCase):
    def setUp(self):
        self.orgs = test_helpers.create_test_orgs(org_count=TEST_ORG_COUNT)

    def test_bags(self):

        test_on_bagchecker = [r[0] for r in bags_ref if len(r) > 2 and r[2]]
        test_on_transfer_routine = [r[0] for r in bags_ref if len(r) > 3 and r[3]]

        for ref in bags_ref:

            # creates test bags
            test_helpers.create_target_bags(ref[0], settings.TEST_BAGS_DIR, self.orgs[0])

            # init trans routine
            tr = TransferRoutine()

            # running setup for 1) make sure env is set 2) build content dict of paths on active
            self.assertTrue(tr.setup_routine())

            # running routine which should return a list of tranfers dict, False means it didn't
            self.assertIsNot(False, tr.run_routine())

            # testing valid bag still valid up until this point
            for trans in tr.transfers:
                if not trans['file_name'].startswith(ref[0]):
                    continue

                ###############
                # START -- TEST RESULTS OF RUN ROUTINE
                ###############

                # a valid bag should be valid until this point so test
                if ref[0] == 'valid_bag':
                    self.assertFalse(trans['auto_fail'])
                else:

                    if r[0] in test_on_transfer_routine:
                        print ref
                        self.assertTrue(trans['auto_fail'])
                        self.assertEquals(ref[1], trans['auto_fail_code'])

                ###############
                # END --  TEST RESULTS OF RUN ROUTINE
                ###############

                archive = test_helpers.create_test_archive(trans, self.orgs[0])

                # checks if this is unique which it should not already be in the system
                self.assertIsNot(False, archive.machine_file_identifier)

                # okay to stop here since archive saved
                if trans['auto_fail']:
                    continue

                bag = bagChecker(archive)
                passed_all_results = bag.bag_passed_all()

                # deleting path in processing and tmp dir
                remove_file_or_dir(os.path.join(settings.TRANSFER_EXTRACT_TMP, archive.bag_it_name))
                remove_file_or_dir(archive.machine_file_path)


                ###############
                # START -- TEST RESULTS OF Bag Checker
                ###############

                if ref[0] in ['valid_bag', 'no_metadata_file']:
                    self.assertTrue(passed_all_results)

                else:
                    # this should always be false
                    self.assertFalse(passed_all_results)

                    if ref[0] in test_on_bagchecker:
                        print ref
                        self.assertEquals(ref[1],bag.ecode)

                ###############
                # END -- TEST RESULTS OF Bag Checker
                ###############

    def tearDown(self):
        test_helpers.delete_test_orgs(self.orgs)
