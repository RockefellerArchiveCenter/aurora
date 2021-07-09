import random

from bag_transfer.accession.models import Accession
from bag_transfer.models import Archives, DashboardMonthData
from django.test import TestCase


class SignalsTestCase(TestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        DashboardMonthData.objects.all().delete()

    def test_update_accession_status(self):
        """
        Ensures that Accession process status is updated when process status for
        all associated archives is updated.
        """
        accession = random.choice(Accession.objects.all())
        for archive in accession.accession_transfers.all():
            archive.process_status = Archives.ACCESSIONING_COMPLETE
            archive.save()
        accession.refresh_from_db()
        self.assertEqual(accession.process_status, Accession.COMPLETE)
