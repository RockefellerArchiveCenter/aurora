# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from os.path import splitext
from orgs.models import Archives, Organization, User
from project_electron import config
from transfer_app.lib import files_helper as FH

def create_test_org():
    test_org = Organization.objects.get_or_create(name='Ford Foundation', machine_name='org1')
    print 'Test organization {} created'.format(test_org)
    return test_org[0]

def create_test_user(org):
    test_user = User(organization=org).save()
    print 'Test user created'
    return test_user

def set_up_archive_object(bag_name):
    org = create_test_org()
    # user = self.create_test_user(org)
    bag_file_path = "{}{}".format(config.PROJECT_ROOT_DIR, bag_name)
    # TODO: this should be replaced with calls to functions, but will require some refactoring
    extension = splitext(bag_file_path)
    tar_accepted_ext = ['.gz', '.tar']
    if extension[-1] in tar_accepted_ext:
        file_type = 'TAR'
    elif extension[-1] == '.zip':
        file_type = 'ZIP'
    else:
        file_type = 'OTHER'

    archive = Archives(
        organization = org,
        # user_uploaded = user,
        machine_file_path = bag_file_path,
        machine_file_size =     FH.file_get_size(bag_file_path, file_type),
        # TODO: fix naive datetime warning
        machine_file_upload_time =  FH.file_modified_time(bag_file_path),
        machine_file_identifier =   "{}{}{}".format(bag_name,org,datetime.now()),
        machine_file_type       =   file_type,
        bag_it_name =               (bag_file_path.split('/')[-1]).split('.')[0],
    )
    archive.save()
    print "Archive {} saved!".format(archive)
    return archive
