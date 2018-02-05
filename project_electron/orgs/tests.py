# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from orgs.models import Archives, Organization, User
from project_electron import config
from transfer_app.lib import files_helper
from transfer_app.lib.bag_checker import bagChecker

class BagTest(TestCase):
    # TODO: abstract these setup functions
    def create_test_org(self):
        test_org = Organization(name='Rockefeller Archive Center', machine_name='org1')
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
            machine_file_size =     files_helper.file_get_size(bag_file_path, 'ZIP'),
            machine_file_upload_time =  files_helper.file_modified_time(bag_file_path),
            machine_file_identifier =   '12345',
            machine_file_type       =   'ZIP',
            bag_it_name =               bag_file_path.split('/')[-1],
        )
        archive.save()
        print "Archive {} saved!".format(archive)
        return archive

    def test_bag_is_valid(self):
        archive = self.set_up_archive_object()
        bag = bagChecker(archive)
        bag.archive_path = archive.machine_file_path
        self.assertTrue(bag.bag_passed_all())
