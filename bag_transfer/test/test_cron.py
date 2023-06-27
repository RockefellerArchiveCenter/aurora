import os
import random
import shutil
from unittest.mock import patch

import bagit
from asterism.file_helpers import remove_file_or_dir, tar_extract_all
from django.conf import settings
from django.test import TransactionTestCase

from bag_transfer.lib.cron import DeliverTransfers, DiscoverTransfers
from bag_transfer.models import (DashboardMonthData, Organization, Transfer,
                                 User)
from bag_transfer.test import helpers


class CronTestCase(helpers.TestMixin, TransactionTestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        """
        Delete existing Archive and DashboardMonthData objects and remove any
        stray objects from the organization upload directory.
        """
        Transfer.objects.all().delete()
        DashboardMonthData.objects.all().delete()
        self.org = random.choice(Organization.objects.all())
        self.remove_delivery_queue()
        self.empty_org_upload_paths()

    @patch('bag_transfer.lib.virus_scanner.VirusScan.is_ready')
    def test_cron(self, mock_ready):
        mock_ready.return_value = True
        self.sub_test_discover_transfers()
        self.sub_test_deliver_transfers()

    @patch("bag_transfer.lib.bag_checker.BagChecker.bag_passed_all")
    def sub_test_discover_transfers(self, mock_passed_all):
        bag_name, _ = helpers.BAGS_REF[0]
        for bag_passed_all in [True, False]:
            self.empty_org_upload_paths()
            helpers.create_target_bags(
                bag_name, settings.TEST_BAGS_DIR,
                self.org, username=random.choice(User.objects.filter(organization=self.org)).username)
            mock_passed_all.return_value = bag_passed_all
            discovered = DiscoverTransfers().do()
            self.assertIsNot(False, discovered)
        for transfer in Transfer.objects.filter(process_status=Transfer.VALIDATED):
            self.assertTrue(os.path.isfile(transfer.machine_file_path))
            tar_extract_all(transfer.machine_file_path, settings.STORAGE_ROOT_DIR)
            bag = bagit.Bag(os.path.join(settings.STORAGE_ROOT_DIR, transfer.machine_file_identifier))
            self.assertTrue("Origin" in bag.info)
            self.assertEqual(bag.info["Origin"], "aurora")

    def sub_test_deliver_transfers(self):
        for transfer in Transfer.objects.filter(process_status=Transfer.VALIDATED):
            transfer.process_status = Transfer.ACCESSIONING_STARTED
            transfer.save()
        awaiting_delivery = len(Transfer.objects.filter(process_status=Transfer.ACCESSIONING_STARTED))
        delivered = DeliverTransfers().do()
        self.assertIsNot(False, delivered)
        self.assertEqual(len(Transfer.objects.filter(process_status=Transfer.ACCESSIONING_STARTED)), awaiting_delivery - 1)
        self.assertEqual(
            len(Transfer.objects.filter(process_status=Transfer.DELIVERED)),
            len(os.listdir(settings.DELIVERY_QUEUE_DIR)))

    def empty_org_upload_paths(self):
        if os.path.exists(self.org.upload_target):
            shutil.rmtree(self.org.upload_target)
        os.makedirs(self.org.upload_target)

    def remove_delivery_queue(self):
        if os.path.isdir(settings.DELIVERY_QUEUE_DIR):
            remove_file_or_dir(settings.DELIVERY_QUEUE_DIR)

    def tearDown(self):
        self.remove_delivery_queue()
