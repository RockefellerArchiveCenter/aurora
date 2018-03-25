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

class BagTest(TransactionTestCase):
    def setUp(self):
        self.orgs = create_test_orgs()

    def test_valid_bag(self):
        # grabbing all valid bags (they should start with 'valid_bag')
        valid_bags = [b for b in os.listdir(settings.TEST_BAGS_DIR) if b.startswith('valid_bag')]
        print valid_bags

        index= 0
        for bags in valid_bags:
            print os.path.join(settings.TEST_BAGS_DIR,bags)
            print self.orgs[0].org_machine_upload_paths()[0]

            self.assertTrue(
                anon_extract_all(
                    os.path.join(settings.TEST_BAGS_DIR,bags), 
                    self.orgs[0].org_machine_upload_paths()[0]
                )
            )

            # rename extracted path -- add index suffix to prevent colision
            created_path = os.path.join(self.orgs[0].org_machine_upload_paths()[0],bags.split('.')[0])
            new_path = '{}{}'.format(created_path, index)
            os.rename(created_path,new_path)
            index += 1

        # init trans routine
        tr = TransferRoutine()

        # running setup for 1) make sure env is set 2)build content dict of paths on active
        self.assertTrue(tr.setup_routine())

        # setting ownership of paths to root
        root_uid = pwd.getpwnam('root').pw_uid
        for org,paths_dict in tr.routine_contents_dictionary.iteritems():
            paths = []
            [paths.append(p) for p in paths_dict['files'] if paths_dict['files']]
            [paths.append(p) for p in paths_dict['dirs'] if paths_dict['dirs']]

            for f in paths:
                os.chown(f,root_uid,root_uid)   ## change ownership of files to root

        # running routine which should return a list of tranfers dict, False means it didn't
        self.assertIsNot(False, tr.run_routine())
        
        # testing valid bag still valid up until this point
        for trans in tr.transfers:
            self.assertFalse(trans['auto_fail'])

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

            bag = bagChecker(archive)
            self.assertTrue(bag.bag_passed_all())

            # deleting path in processing and tmp dir
            remove_file_or_dir(os.path.join(settings.TRANSFER_EXTRACT_TMP, archive.bag_it_name))
            remove_file_or_dir(archive.machine_file_path)

    def tearDown(self):
        delete_test_orgs(self.orgs)



