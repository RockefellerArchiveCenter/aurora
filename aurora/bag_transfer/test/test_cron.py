import os
import random
from unittest.mock import patch

import bagit
from asterism.file_helpers import remove_file_or_dir
from bag_transfer.lib.cron import DeliverTransfers, DiscoverTransfers
from bag_transfer.models import Archives
from bag_transfer.test import helpers
from bag_transfer.test.setup import BAGS_REF
from django.conf import settings
from django.test import Client, TestCase


class CronTestCase(TestCase):
    def setUp(self):
        self.orgs = helpers.create_test_orgs(org_count=1)
        self.user = helpers.create_test_user(
            username=settings.TEST_USER['USERNAME'],
            password=settings.TEST_USER['PASSWORD'],
            org=random.choice(self.orgs),
            groups=helpers.create_test_groups(['managing_archivists']),
            is_staff=True)
        self.client = Client()
        for d in [settings.DELIVERY_QUEUE_DIR, settings.STORAGE_ROOT_DIR]:
            if os.path.isdir(d):
                remove_file_or_dir(d)

    def test_cron(self):
        self.discover_bags()
        self.deliver_bags()

    @patch("bag_transfer.lib.bag_checker.BagChecker.bag_passed_all")
    def discover_bags(self, mock_bag_check):
        bag_name, _ = BAGS_REF[0]
        helpers.create_target_bags(bag_name, settings.TEST_BAGS_DIR, self.orgs[0], username=self.user.username)
        mock_bag_check.return_value = True
        discovered = DiscoverTransfers().do()
        self.assertIsNot(False, discovered)

    def deliver_bags(self):
        for archive in Archives.objects.filter(process_status=Archives.VALIDATED):
            archive.process_status = Archives.ACCESSIONING_STARTED
            archive.save()
        delivered = DeliverTransfers().do()
        self.assertIsNot(False, delivered)
        self.assertEqual(len(Archives.objects.filter(process_status=Archives.ACCESSIONING_STARTED)), 0)
        self.assertEqual(
            len(Archives.objects.filter(process_status=Archives.DELIVERED)),
            len(os.listdir(settings.DELIVERY_QUEUE_DIR)))
        for bag_path in os.listdir(settings.STORAGE_ROOT_DIR):
            bag = bagit.Bag(os.path.join(settings.STORAGE_ROOT_DIR, bag_path))
            self.assertTrue("Origin" in bag.info)
            self.assertEqual(bag.info["Origin"], "aurora")

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
