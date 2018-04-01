# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pwd
from datetime import datetime
from django.test import TransactionTestCase
from django.conf import settings
from rights.test.setup_tests import *
from orgs.models import Archives, Organization
from orgs.test import setup_tests as org_setup
from rights.models import *

RECORD_TYPES = [
    "administrative records", "board materials",
    "communications and publications", "grant records",
    "annual reports"]


class RightsTestCase(TransactionTestCase):
    def setUp(self):
        self.record_types = create_record_types(RECORD_TYPES)
        self.orgs = create_test_orgs()
        self.archives = create_test_archives(self.orgs)

    def create_rights_statement(self, record_type):
        rights_bases = ['Copyright', 'Statute', 'License', 'Other']
        rights_statement = RightsStatement(
            organization=random.choice(self.orgs),
            applies_to_type=record_type,
            rights_basis=random.choice(rights_bases),
        )
        rights_statement.save()

    def add_rights_info(self, rights_statement):
        if rights_statement.rights_basis == 'Statute':
            rights_info = RightsStatementStatute(
                statute_citation=random_string(50),
                statute_applicable_start_date=random_date(1960),
                statute_applicable_end_date=random_date(1990),
                statute_end_date_period=20,
                statute_note=random_string(40)
            )
        elif rights_statement.rights_basis == 'Other':
            rights_info = RightsStatementOther(
                other_rights_basis=random.choice(['Donor', 'Policy']),
                other_rights_applicable_start_date=random_date(1978),
                other_rights_end_date_period=20,
                other_rights_end_date_open=True,
                other_rights_note=random_string(50)
            )
        elif rights_statement.rights_basis == 'Copyright':
            rights_info = RightsStatementCopyright(
                copyright_status=random.choice(['copyrighted', 'public domain', 'unknown']),
                copyright_applicable_start_date=random_date(1950),
                copyright_end_date_period=40,
                copyright_note=random_string(70)
            )
        elif rights_statement.rights_basis == 'License':
            rights_info = RightsStatementLicense(
                license_applicable_start_date=random_date(1980),
                license_start_date_period=10,
                license_end_date_open=True,
                license_note=random_string(60)
            )
        rights_info.rights_statement = rights_statement
        rights_info.save()

    def add_rights_granted(self, rights_statement):
        for x in xrange(random.randint(1, 2)):
            rights_granted = RightsStatementRightsGranted(
                rights_statement=rights_statement,
                act=random.choice(['publish', 'disseminate','replicate', 'migrate', 'modify', 'use', 'delete']),
                start_date=random_date(1984),
                end_date_period=15,
                rights_granted_note=random_string(100),
                restriction=random.choice(['allow', 'disallow', 'conditional'])
                )
            rights_granted.save()

    def test_rights(self):
        for record_type in RECORD_TYPES:
            self.create_rights_statement(record_type)
        self.assertEquals(len(RightsStatement.objects.all()), len(RECORD_TYPES))

        for rights_statement in RightsStatement.objects.all():
            self.add_rights_info(rights_statement)
            self.add_rights_granted(rights_statement)

            # Make sure correct rights info objects were assigned
            if rights_statement.rights_basis == 'Statute':
                self.assertIsInstance(rights_statement.get_rights_info_object(), RightsStatementStatute)
            elif rights_statement.rights_basis == 'Other':
                self.assertIsInstance(rights_statement.get_rights_info_object(), RightsStatementOther)
            elif rights_statement.rights_basis == 'Copyright':
                self.assertIsInstance(rights_statement.get_rights_info_object(), RightsStatementCopyright)
            elif rights_statement.rights_basis == 'License':
                self.assertIsInstance(rights_statement.get_rights_info_object(), RightsStatementLicense)

            # Make sure RightsGranted objects were created
            self.assertIsNot(False, rights_statement.get_rights_granted_objects())

            # Assign rights statements to organization
            org = random.choice(self.orgs)
            rights_statement.organization = org
            rights_statement.save()
            self.assertTrue(org.rights_statements)

        # Assign rights statements to archives
        for archive in self.archives:
            bag = bagChecker(archive)

            # this calls assign_rights
            self.assertTrue(bag.bag_passed_all())

            # # deleting path in processing and tmp dir
            remove_file_or_dir(os.path.join(settings.TRANSFER_EXTRACT_TMP, archive.bag_it_name))
            remove_file_or_dir(archive.machine_file_path)

        # Delete rights statement
        previous_length = len(RightsStatement.objects.all())
        to_delete = random.choice(RightsStatement.objects.all())
        self.assertTrue(to_delete.delete())
        self.assertEqual(len(RightsStatement.objects.all()), previous_length-1)

    def tearDown(self):
        org_setup.delete_test_orgs(self.orgs)


class RightsViewsTestCase():
    pass

    def test_rights_views(self):
        pass
        # Get with pk
        # Get without pk
        # Post with pk
        # Post without pk
        # delete
            # non ajax requests
            # action != delete
