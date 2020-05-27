import os
import random

import bagit
from bag_transfer.lib.cron import DeliverTransfers, DiscoverTransfers
from bag_transfer.models import Archives
from bag_transfer.test import helpers
from bag_transfer.test.setup import BAGS_REF
from django.conf import settings
from django.test import Client, TransactionTestCase


class CronTestCase(TransactionTestCase):
    def setUp(self):
        self.orgs = helpers.create_test_orgs(org_count=1)
        self.user = helpers.create_test_user(
            username=settings.TEST_USER['USERNAME'],
            password=settings.TEST_USER['PASSWORD'],
            org=random.choice(self.orgs),
            groups=helpers.create_test_groups(['managing_archivists']),
            is_staff=True)
        self.client = Client()

    def test_cron(self):
        self.discover_bags()
        self.deliver_bags()

    def discover_bags(self):
        for ref in BAGS_REF:
            helpers.create_target_bags(ref[0], settings.TEST_BAGS_DIR, self.orgs[0], username=self.user.username)
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
            len(os.listdir(settings.DELIVERY_QUEUE_DIR))
        )
        for bag_path in os.listdir(settings.DELIVERY_QUEUE_DIR):
            bag = bagit.Bag(os.path.join(settings.DELIVERY_QUEUE_DIR, bag_path))
            self.assertTrue("Origin" in bag.bag_info)
            self.assertEqual(bag.bag_info["Origin"], "aurora")

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
