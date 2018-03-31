# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pwd

from django.test import TransactionTestCase
from django.conf import settings


class RightsTestCase(TransactionTestCase):
    def setUp(self):
        self.orgs = create_test_orgs()
        self.archives = create_test_archives()

    def test_rights(self):
        # create
            # model methods
                # get_rights_info_object
                # get_rights_granted_objects
        # edit
        # delete
        pass

    def test_rights_views(self):
        pass
        # create
        # edit
        # delete
            # non ajax requests
            # action != delete

    def tearDown(self):
        orgs.test.setup_tests.delete_test_orgs(self.orgs)
