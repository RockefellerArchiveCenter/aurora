# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pwd

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
        pass

    def add_rights_granted(self, rights_statement):
        pass

    def test_rights(self):
        for record_type in RECORD_TYPES:
            self.create_rights_statement(record_type)
        self.assertTrue(len(RightsStatement.objects.all()) == len(RECORD_TYPES))

        for rights_statement in RightsStatement.objects.all():
            self.add_rights_info(rights_statement)
            self.add_rights_granted(rights_statement)
            self.assertTrue(len(rights_statement.get_rights_info_object()) == 1)
            self.assertTrue(len(rights_statement.get_rights_granted_object()) == 2)

            org = random.choice(self.orgs)
            rights_statement.organization = org
            self.assertTrue(len(org.rights_statements >= 1))

        for archive in self.archives:
            self.assertTrue(archive.assign_rights())

        to_delete = random.choice(rights_statement)
        to_delete.delete()
        self.assertTrue(len(RightsStatement.objects.all()) == len(RECORD_TYPES)-1)
        # test there aren't orphaned things?
        pass

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
