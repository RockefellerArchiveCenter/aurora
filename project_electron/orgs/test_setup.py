# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from os import path, makedirs
from shutil import rmtree
from orgs.models import Archives, Organization, User
from project_electron import config
from transfer_app.lib import files_helper as FH

def tearDown():
    print "tearing down"
    FH.remove_file_or_dir(config.TESTING_TMP_DIR)

def set_up_tmp_dir():
    if path.isdir(config.TESTING_TMP_DIR):
        rmtree(config.TESTING_TMP_DIR)
    else:
        makedirs(config.TESTING_TMP_DIR)
    return config.TESTING_TMP_DIR

def create_test_org():
    test_org = Organization(name='Ford Foundation', machine_name='org1')
    test_org.save()
    print 'Test organization {} created'.format(test_org)
    return test_org

def create_test_user(org):
    test_user = User(organization=org).save()
    print 'Test user created'
    return test_user

def set_up_archive_object():
    org = create_test_org()
    # user = self.create_test_user(org)
    bag_file_path = "{}test_bags/valid_bag.zip".format(config.PROJECT_ROOT_DIR)
    print bag_file_path
    archive = Archives(
        organization = org,
        # user_uploaded = user,
        machine_file_path = bag_file_path,
        machine_file_size =     FH.file_get_size(bag_file_path, 'ZIP'),
        # TODO: fix naive datetime warning
        machine_file_upload_time =  FH.file_modified_time(bag_file_path),
        machine_file_identifier =   '12345',
        machine_file_type       =   'ZIP',
        bag_it_name =               (bag_file_path.split('/')[-1]).split('.')[0],
    )
    archive.save()
    print "Archive {} saved!".format(archive)
    return archive
