from pathlib import Path

from django.test import TestCase

from aurora import settings
from bag_transfer.lib.cleanup import CleanupRoutine


class CleanupRoutineTestCase(TestCase):

    def setUp(self):
        if not Path(settings.DELIVERY_QUEUE_DIR).exists():
            Path(settings.DELIVERY_QUEUE_DIR).mkdir()

    def test_cleanup(self):
        """Asserts that the CleanupRoutine finds and deletes a file given an identifier"""
        identifier = "foo"
        Path(settings.DELIVERY_QUEUE_DIR, "{}.tar.gz".format(identifier)).touch()
        self.assertTrue(CleanupRoutine().run(identifier), "Transfer {} was found".format(identifier))
        self.assertTrue(CleanupRoutine().run(identifier), "Transfer {} was not found".format(identifier))
