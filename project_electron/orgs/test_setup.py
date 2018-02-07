# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from orgs.models import Archives, Organization, User
from project_electron import config
from transfer_app.lib import files_helper as FH

def create_test_org():
    test_org = Organization(name='Ford Foundation', machine_name='org1')
    test_org.save()
    print 'Test organization {} created'.format(test_org)
    return test_org

def create_test_user(org):
    test_user = User(organization=org).save()
    print 'Test user created'
    return test_user

def set_up_archive_object(bag_name):
    org = create_test_org()
    # user = self.create_test_user(org)
    bag_file_path = "{}{}".format(config.PROJECT_ROOT_DIR, bag_name)
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
