# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import pwd
import string
import random
import datetime

from django.conf import settings
from transfer_app.lib.transfer_routine import *
from transfer_app.lib.files_helper import *
from transfer_app.lib.bag_checker import bagChecker
from orgs.models import Archives, Organization
from orgs.test import setup_tests as org_setup


def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))


def random_date(year):
    try:
        return datetime.datetime.strptime('{} {}'.format(random.randint(1, 366), year), '%j %Y')
    except ValueError:
        random_date(year)

def create_record_types(record_types):
    # waiting for previous PR
    for type in record_types:
        pass


def create_test_orgs():
    orgs = org_setup.create_test_orgs(org_count=1)
    for org in orgs:
        # add record type to bagit profile
        pass
    return orgs


def create_test_archives(orgs):
    bags_ref = ['valid_bag']
    bags = []

    for ref in bags_ref:
        create_target_bags(ref, settings.TEST_BAGS_DIR, orgs[0])
        tr = TransferRoutine()
        tr.setup_routine()
        tr.run_routine()
        for trans in tr.transfers:
            machine_file_identifier = Archives().gen_identifier(
                trans['file_name'],
                trans['org'],
                trans['date'],
                trans['time']
            )
            archive = Archives.initial_save(
                orgs[0],
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

            bags.append(archive)

    return bags


def create_target_bags(target_str, test_bags_dir, org):
    target_bags = [b for b in os.listdir(test_bags_dir) if b.startswith(target_str)]

    # setting ownership of paths to root
    root_uid = pwd.getpwnam('root').pw_uid
    index = 0

    for bags in target_bags:
        anon_extract_all(
            os.path.join(test_bags_dir,bags),
            org.org_machine_upload_paths()[0]
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
