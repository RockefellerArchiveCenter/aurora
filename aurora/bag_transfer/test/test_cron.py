import os
import random
import shutil
from unittest.mock import patch

import bagit
from asterism.file_helpers import remove_file_or_dir
from bag_transfer.lib.cron import DeliverTransfers, DiscoverTransfers
from bag_transfer.models import (DashboardMonthData, Organization, Transfer,
                                 User)
from bag_transfer.test import helpers
from bag_transfer.test.helpers import BAGS_REF
from django.conf import settings
from django.test import TestCase


class CronTestCase(TestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        """
        Delete existing Archive and DashboardMonthData objects and remove any
        stray objects from the organization upload directory.
        """
        Transfer.objects.all().delete()
        DashboardMonthData.objects.all().delete()
        self.org = random.choice(Organization.objects.all())
        for d in [settings.DELIVERY_QUEUE_DIR, settings.STORAGE_ROOT_DIR]:
            if os.path.isdir(d):
                remove_file_or_dir(d)
        for d in self.org.org_machine_upload_paths():
            if os.path.exists(d):
                shutil.rmtree(d)
                os.makedirs(d)

    def test_cron(self):
        self.discover_bags()
        self.deliver_bags()

    @patch("bag_transfer.lib.bag_checker.BagChecker.bag_passed_all")
    def discover_bags(self, mock_passed_all):
        bag_name, _ = BAGS_REF[0]
        for bag_passed_all in [True, False]:
            self.bags = helpers.create_target_bags(
                bag_name, settings.TEST_BAGS_DIR,
                self.org, username=random.choice(User.objects.filter(organization=self.org)).username)
            mock_passed_all.return_value = bag_passed_all
            discovered = DiscoverTransfers().do()
            self.assertIsNot(False, discovered)

    def deliver_bags(self):
        for transfer in Transfer.objects.filter(process_status=Transfer.VALIDATED):
            transfer.process_status = Transfer.ACCESSIONING_STARTED
            transfer.save()
        delivered = DeliverTransfers().do()
        self.assertIsNot(False, delivered)
        self.assertEqual(len(Transfer.objects.filter(process_status=Transfer.ACCESSIONING_STARTED)), 0)
        self.assertEqual(
            len(Transfer.objects.filter(process_status=Transfer.DELIVERED)),
            len(os.listdir(settings.DELIVERY_QUEUE_DIR)))
        for bag_path in os.listdir(settings.STORAGE_ROOT_DIR):
            bag = bagit.Bag(os.path.join(settings.STORAGE_ROOT_DIR, bag_path))
            self.assertTrue("Origin" in bag.info)
            self.assertEqual(bag.info["Origin"], "aurora")

    def tearDown(self):
        for d in [settings.DELIVERY_QUEUE_DIR, settings.STORAGE_ROOT_DIR]:
            if os.path.isdir(d):
                remove_file_or_dir(d)
