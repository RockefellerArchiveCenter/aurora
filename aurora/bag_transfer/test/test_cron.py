import os
import pwd
import random

import bagit
from django.test import TransactionTestCase, Client
from django.conf import settings

from bag_transfer.lib.cron import DiscoverTransfers, DeliverTransfers
from bag_transfer.test import helpers
from bag_transfer.test.setup import bags_ref, TEST_ORG_COUNT
from bag_transfer.models import Archives, User


class CronTestCase(TransactionTestCase):
    def setUp(self):
        self.orgs = helpers.create_test_orgs(org_count=1)
        self.baglogcodes = helpers.create_test_baglogcodes()
        self.groups = helpers.create_test_groups(['managing_archivists'])
        self.user = helpers.create_test_user(username=settings.TEST_USER['USERNAME'], org=random.choice(self.orgs))
        for group in self.groups:
            self.user.groups.add(group)
        self.user.is_staff = True
        self.user.set_password(settings.TEST_USER['PASSWORD'])
        self.user.save()
        self.client = Client()

    def test_cron(self):
        for ref in bags_ref:
            helpers.create_target_bags(ref[0], settings.TEST_BAGS_DIR, self.orgs[0], username=self.user.username)
        discovered = DiscoverTransfers().do()
        self.assertIsNot(False, discovered)

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
            self.assertTrue('Origin' in bag.bag_info)

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
