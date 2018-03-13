from django.test import TestCase

from orgs.test.setup_test import *

class FilesHelperTestCase(TestCase):

    def setup(self):
        self.organizations = create_test_orgs()

        # build uploads dir
