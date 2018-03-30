# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pwd

from django.test import TransactionTestCase
from django.conf import settings

from orgs.test.setup_tests import *
from transfer_app.lib.transfer_routine import *
from transfer_app.lib.files_helper import *
from transfer_app.lib.bag_checker import bagChecker

from orgs.models import Archives

class RightsTestCase(TransactionTestCase):
    def setUp(self):
        self.orgs = create_test_orgs()
        self.archives = create_test_archives()

    def test_rights(self):
        # create
        # model methods
        # edit
        # delete
        pass
