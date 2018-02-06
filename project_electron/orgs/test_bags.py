# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from project_electron import config
from transfer_app.lib.bag_checker import bagChecker
from orgs.test_setup import *

class BagTest(TestCase):
    def test_bag_is_valid(self):
        # TODO: write loop to test all bags
        tmp_dir_prefix = set_up_tmp_dir()
        archive = set_up_archive_object()
        bag = bagChecker(archive)
        self.assertTrue(bag.bag_passed_all())
