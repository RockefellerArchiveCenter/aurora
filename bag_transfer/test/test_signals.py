import random

from django.test import TestCase

from bag_transfer.accession.models import Accession
from bag_transfer.models import DashboardMonthData, Transfer


class SignalsTestCase(TestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        DashboardMonthData.objects.all().delete()

    def test_update_accession_status(self):
        """
        Ensures that Accession process status is updated when process status for
        all associated transfers is updated.
        """
        accession = random.choice(Accession.objects.all())
        for transfer in accession.accession_transfers.all():
            transfer.process_status = Transfer.ACCESSIONING_COMPLETE
            transfer.save()
        accession.refresh_from_db()
        self.assertEqual(accession.process_status, Accession.COMPLETE)
