# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pwd
import string
import random

from django.conf import settings
from transfer_app.lib.transfer_routine import *
from transfer_app.lib.files_helper import *
from transfer_app.lib.bag_checker import bagChecker

from orgs.models import Archives, Organization

def create_test_orgs():
    orgs = orgs.test.setup_tests.create_test_orgs()
    # add record types


def create_test_archives():
    # tuple of tuples
    # (str that test bag starts with, ecode, test on bag checker, test on transfer routine)
    bags_ref = (

        ('valid_bag', ''),

    )

    for ref in bags_ref:

        # creates test bags
        self.create_target_bags(ref[0], settings.TEST_BAGS_DIR, self.orgs[0])

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

            bag = bagChecker(archive)
            passed_all_results = bag.bag_passed_all()

            # deleting path in processing and tmp dir
            remove_file_or_dir(os.path.join(settings.TRANSFER_EXTRACT_TMP, archive.bag_it_name))
            remove_file_or_dir(archive.machine_file_path)

def create_target_bags(self, target_str, test_bags_dir, org):
    target_bags = [b for b in os.listdir(test_bags_dir) if b.startswith(target_str)]
    self.assertTrue( (len(target_bags) > 0) )

    # setting ownership of paths to root
    root_uid = pwd.getpwnam('root').pw_uid
    index = 0

    for bags in target_bags:
        self.assertTrue(
            anon_extract_all(
                os.path.join(test_bags_dir,bags),
                org.org_machine_upload_paths()[0]
            )
        )

        # rename extracted path -- add index suffix to prevent colision
        created_path = os.path.join(org.org_machine_upload_paths()[0], bags.split('.')[0])
        new_path = '{}{}'.format(created_path, index)
        os.rename(created_path, new_path)
        index += 1

        # chowning path to root
        chown_path_to_root(new_path)


def delete_test_archives():
    pass
