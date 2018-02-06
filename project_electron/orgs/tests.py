# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from orgs.models import Archives, Organization, User
from project_electron import config
from transfer_app.lib import files_helper as FH
from transfer_app.lib.bag_checker import bagChecker

class BagTest(TestCase):
    # TODO: abstract these setup functions
    # TODO: use variable for tmp dir
    # TODO: set up TMP dir

    def create_test_org(self):
        test_org = Organization(name='Ford Foundation', machine_name='org1')
        test_org.save()
        print 'Test organization {} created'.format(test_org)
        return test_org

    def create_test_user(self, org):
        test_user = User(organization=org).save()
        print 'Test user created'
        return test_user

    def set_up_archive_object(self):
        org = self.create_test_org()
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

    def test_bag_is_valid(self):
        # TODO: write loop to test all bags
        archive = self.set_up_archive_object()
        bag = bagChecker(archive)
        bag.archive_path = "/home/va0425/tmp/{}".format(archive.bag_it_name)
        self.assertTrue(bag.bag_passed_all())

#TODO: teardown to delete TMP dir
