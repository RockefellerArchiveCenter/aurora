# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pwd

from django.test import TransactionTestCase
from django.conf import settings

from orgs.test.setup_tests import *
from transfer_app.lib.transfer_routine import *
from transfer_app.lib.files_helper import *
from transfer_app.lib.bag_checker import bagChecker

from orgs.models import Archives

class BagTestCase(TransactionTestCase):
    def setUp(self):
        self.orgs = create_test_orgs()

    def test_bags(self):

        # tuple of tuples 
        # (str that test bag starts with, ecode, test on bag checker, test on transfer routine)
        bags_ref = (
            ('invalid<filename','BFNM', False, True),

            ('valid_bag', ''),

            ('changed_file', 'GBERR', True),
            ('missing_bag_manifest', 'GBERR', True),
            ('missing_bag_declaration', 'GBERR', True),
            ('missing_payload_directory', 'GBERR', True),
            ('missing_payload_manifest', 'GBERR', True),
            
            # ('empty_payload_directory', 'GBERR', True),
            ('missing_description', 'RBERR', True),
            # ('missing_bag_manifest', 'RBERR', True),
            ('missing_record_type', 'RBERR', True),
            ('missing_source_organization', 'RBERR', True),
            ('missing_title', 'RBERR', True),
            ('repeating_record_type', 'RBERR', True),
            ('repeating_source_organization', 'RBERR', True),
            ('repeating_title', 'RBERR', True),
            ('unauthorized_record_type', 'RBERR', True),
            ('unauthorized_source_organization', 'RBERR', True),
           
            # ('no_metadata_file', '', ''),

            ('invalid_metadata_file','MDERR', True),
            ('invalid_datatype_date','DTERR', True),
            ('invalid_datatype_language','DTERR', True),
            
        )
        test_on_bagchecker = [r[0] for r in bags_ref if len(r) > 2 and r[2]]
        test_on_transfer_routine = [r[0] for r in bags_ref if len(r) > 3 and r[3]]

        for ref in bags_ref:

            # creates test bags 
            self.create_target_bags(ref[0], settings.TEST_BAGS_DIR, self.orgs[0])

            # init trans routine
            tr = TransferRoutine()

            # running setup for 1) make sure env is set 2)build content dict of paths on active
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

                # building machine ident
                machine_file_identifier = Archives().gen_identifier(
                    trans['file_name'],
                    trans['org'],
                    trans['date'],
                    trans['time']
                )
                # checks if this is unique which it should not already be in the system
                self.assertIsNot(False, machine_file_identifier)

                # creates archive from dict
                archive = Archives.initial_save(
                    self.orgs[0],
                    None,
                    trans['file_path'],
                    trans['file_size'],
                    trans['file_modtime'],
                    machine_file_identifier,
                    trans['file_type'],
                    trans['bag_it_name']
                )
                
                # updating the name since the bag info reflects ford
                archive.organization.name = 'Ford Foundation'
                archive.organization.save()

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

                if ref[0] in ['valid_bag','no_metadata_file']:
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
        delete_test_orgs(self.orgs)

    def create_target_bags(self, target_str, test_bags_dir, org):
        target_bags = [b for b in os.listdir(test_bags_dir) if b.startswith(target_str)]
        self.assertTrue( (len(target_bags) > 0) )

        # setting ownership of paths to root
        root_uid = pwd.getpwnam('root').pw_uid
        index= 0

        for bags in target_bags:
            self.assertTrue(
                anon_extract_all(
                    os.path.join(test_bags_dir,bags), 
                    org.org_machine_upload_paths()[0]
                )
            )

            # rename extracted path -- add index suffix to prevent colision
            created_path = os.path.join(org.org_machine_upload_paths()[0],bags.split('.')[0])
            new_path = '{}{}'.format(created_path, index)
            os.rename(created_path,new_path)
            index += 1

            # trying to update the path
            os.chown(new_path,root_uid,root_uid)   ## change ownership of files to root