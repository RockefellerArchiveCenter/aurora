# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pwd

from django.test import TransactionTestCase
from django.conf import settings
from orgs.models import Archives, Organization
from rights.models import *

RECORD_TYPES = [
    "administrative records", "board materials",
    "communications and publications", "grant records",
    "annual reports"]


class RightsTestCase(TransactionTestCase):
    def setUp(self):
        self.orgs = create_test_orgs()
        self.archives = create_test_archives()

    def create_rights_statement(self, record_type):
        pass

    def add_rights_info(self, rights_statement):
        pass

    def add_rights_granted(self, rights_statement):
        pass

    def test_rights(self):
        for record_type in RECORD_TYPES:
            self.create_rights_statement(record_type)
        self.assertTrue(len(RightsStatement.objects.all()) == len(RECORD_TYPES))

        for rights_statement in RightsStatement.objects.all()
            self.add_rights_info(rights_statement)
            self.add_rights_granted(rights_statement)
            self.assertTrue(len(rights_statement.get_rights_info_object()) == 1)
            self.assertTrue(len(rights_statement.get_rights_granted_object()) == 2)

            org = random(self.orgs)
            rights_statement.organization = org
            self.assertTrue(len(org.rights_statements >= 1))

        for archive in self.archives:
            self.assertTrue(archive.assign_rights())

        random(rights_statement).delete()
        self.assertTrue(len(RightsStatement.objects.all()) == len(RECORD_TYPES)-1)
        pass

    def tearDown(self):
        orgs.test.setup_tests.delete_test_orgs(self.orgs)


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
