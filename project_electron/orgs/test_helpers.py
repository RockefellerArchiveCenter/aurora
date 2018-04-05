# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from os import path, chdir, makedirs, listdir, rename
import pwd
import random
import string
from django.contrib.auth.models import Group
from orgs.models import Archives, Organization, User, BAGLogCodes
from rights.models import RecordType
from project_electron import config, settings
from transfer_app.lib import files_helper as FH
from transfer_app.lib.transfer_routine import TransferRoutine

# General variables and setup routines


# still used??
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


# Returns a random string of specified length
def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))


# Feturns a random date in a given year
def random_date(year):
    try:
        return datetime.datetime.strptime('{} {}'.format(random.randint(1, 366), year), '%j %Y')
    # accounts for leap year values
    except ValueError:
        random_date(year)


####################################
# CREATE TEST OBJECTS
####################################

# Creates a RecordType object for each value in list provided.
# If no list is given, RecordTypes created from a default list
def create_test_record_types(record_types=None):
    objects = []
    if record_types is None:
        record_types = [
            "administrative records", "board materials",
            "communications and publications", "grant records",
            "annual reports"]
    for record_type in record_types:
        object = RecordType.objects.create(
            name=record_type
        )
        objects.append(object)
    return objects


# Creates a Group for each value in a list of names.
# If no list is given, Groups are created from a default list
def create_test_groups(names=None):
    groups = []
    if names is None:
        names = ['appraisal_archivists', 'accessioning_archivists', 'managing_archivists']
    for name in names:
        group = Group(name=name)
        group.save()
        groups.append(group)
    return groups


# Review
def create_test_org():
    test_org = Organization.objects.get_or_create(
        name='Ford Foundation',
        machine_name='org1'
    )
    print 'Test organization {} created'.format(test_org[0].name)
    return test_org[0]


# review
def create_test_user(org):
    test_user = User(organization=org).save()
    print 'Test user created'
    return test_user

# Review
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
        machine_file_identifier="{}{}{}".format(bag_name, org, datetime.datetime.now()),
        machine_file_type=file_type,
        bag_it_name=(bag_file_path.split('/')[-1]).split('.')[0],
    )
    archive.save()
    print "Archive {} saved!".format(archive)
    return archive

# Review (From RightsStatement tests)
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


# review (From RightsStatement tests)
def create_target_bags(target_str, test_bags_dir, org):
    target_bags = [b for b in listdir(test_bags_dir) if b.startswith(target_str)]

    # setting ownership of paths to root
    root_uid = pwd.getpwnam('root').pw_uid
    index = 0

    for bags in target_bags:
        FH.anon_extract_all(
            path.join(test_bags_dir,bags),
            org.org_machine_upload_paths()[0]
        )
        # rename extracted path -- add index suffix to prevent colision
        created_path = path.join(org.org_machine_upload_paths()[0], bags.split('.')[0])
        new_path = '{}{}'.format(created_path, index)
        rename(created_path, new_path)
        index += 1

        # chowning path to root
        FH.chown_path_to_root(new_path)


# Review
def get_bag_extensions(bag_names):
    extensions = ['.tar', '.tar.gz', '.zip']
    bag_list = []
    for name in bag_names:
        bag_list.append(name)
        for e in extensions:
            bag_list.append('{}{}'.format(name, e))
    return bag_list
