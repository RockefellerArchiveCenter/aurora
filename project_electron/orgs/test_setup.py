# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from os import path, chdir, makedirs
from orgs.models import Archives, Organization, User, BAGLogCodes
from project_electron import config, settings
from transfer_app.lib import files_helper as FH


def setup_tmp_dir():
    if path.isdir(config.TESTING_TMP_DIR):
        FH.remove_file_or_dir(config.TESTING_TMP_DIR)
    else:
        makedirs(config.TESTING_TMP_DIR)


def remove_tmp_dir():
    FH.remove_file_or_dir(config.TESTING_TMP_DIR)


def create_test_baglog_code(code):
    baglog_code = BAGLogCodes(
        code_short=code,
        code_type='T',
        code_desc='Test code',
    )
    baglog_code.save()
    print "BAGLogCode {} created".format(baglog_code)


def create_test_org():
    test_org = Organization.objects.get_or_create(
        name='Ford Foundation',
        machine_name='org1'
    )
    print 'Test organization {} created'.format(test_org[0].name)
    return test_org[0]


def create_test_user(org):
    test_user = User(organization=org).save()
    print 'Test user created'
    return test_user


def create_test_archive(bag_name, org):
    # user = self.create_test_user(org)
    bag_file_path = path.join(path.split(settings.BASE_DIR)[0], 'test_bags', bag_name)
    # TODO: this should be replaced with calls to functions, but will require some refactoring
    extension = path.splitext(bag_file_path)
    tar_accepted_ext = ['.gz', '.tar']
    if extension[-1] in tar_accepted_ext:
        file_type = 'TAR'
    elif extension[-1] == '.zip':
        file_type = 'ZIP'
    else:
        file_type = 'OTHER'

    archive = Archives(
        organization=org,
        # user_uploaded = user,
        machine_file_path=bag_file_path,
        machine_file_size=FH.file_get_size(bag_file_path, file_type),
        # TODO: fix naive datetime warning
        machine_file_upload_time=FH.file_modified_time(bag_file_path),
        machine_file_identifier="{}{}{}".format(bag_name, org, datetime.now()),
        machine_file_type=file_type,
        bag_it_name=(bag_file_path.split('/')[-1]).split('.')[0],
    )
    archive.save()
    print "Archive {} saved!".format(archive)
    return archive


def get_bag_extensions(bag_names):
    extensions = ['.tar', '.tar.gz', '.zip']
    bag_list = []
    for name in bag_names:
        bag_list.append(name)
        for e in extensions:
            bag_list.append('{}{}'.format(name, e))
    return bag_list
