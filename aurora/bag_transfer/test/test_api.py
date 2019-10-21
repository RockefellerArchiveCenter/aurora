import json
import os
import random
import shutil

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from aurora import settings
from bag_transfer.models import Archives, User
from bag_transfer.api.views import ArchivesViewSet
from bag_transfer.test import helpers


class APITest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.process_status = Archives.ACCESSIONING_STARTED
        self.archivesspace_identifier = "/repositories/2/archival_objects/3"
        self.archivesspace_parent_identifier = "/repositories/2/archival_objects/4"
        self.orgs = helpers.create_test_orgs(org_count=1)
        self.user = helpers.create_test_user(username=settings.TEST_USER['USERNAME'], org=random.choice(self.orgs))
        self.user.is_staff = True
        self.user.set_password(settings.TEST_USER['PASSWORD'])
        self.user.save()
        self.bags = helpers.create_target_bags('valid_bag', settings.TEST_BAGS_DIR, self.orgs[0])
        tr = helpers.run_transfer_routine()
        self.archives = []
        for transfer in tr.transfers:
            archive = helpers.create_test_archive(transfer, self.orgs[0])
            self.archives.append(archive)
        for archive in self.archives:
            shutil.copy(
                os.path.join(settings.BASE_DIR, settings.TEST_BAGS_DIR, 'valid_bag.tar.gz'),
                os.path.join(settings.BASE_DIR, settings.DELIVERY_QUEUE_DIR, '{}.tar.gz'.format(archive.machine_file_identifier)))

    def update_transfer(self):
        for archive in Archives.objects.all():
            request = self.factory.get(reverse('archives-detail', kwargs={"pk": archive.pk}), format="json")
            request.user = self.user
            new_transfer = ArchivesViewSet.as_view(actions={"get": "retrieve"})(request, pk=archive.pk).data
            new_transfer['process_status'] = self.process_status
            new_transfer['archivesspace_identifier'] = self.archivesspace_identifier
            new_transfer['archivesspace_parent_identifier'] = self.archivesspace_parent_identifier

            request = self.factory.put(reverse('archives-detail', kwargs={"pk": archive.pk}), data=new_transfer, format="json")
            request.user = self.user
            response = ArchivesViewSet.as_view(actions={"put": "update"})(request, pk=archive.pk)
            self.assertEqual(response.status_code, 200, "Wrong HTTP status code")
            for field in ['process_status', 'archivesspace_identifier', 'archivesspace_parent_identifier']:
                self.assertEqual(response.data[field], getattr(self, field), "{} status not updated".format(field))
            self.assertEqual(False, os.path.isfile(os.path.join(
                settings.BASE_DIR,
                settings.DELIVERY_QUEUE_DIR, "{}.tar.gz".format(new_transfer['identifier']))),
                "File was not removed")

    def schema(self):
        schema = self.client.get(reverse('schema-json', kwargs={"format": ".json"}))
        self.assertEqual(schema.status_code, 200, "Wrong HTTP code")

    def test_api(self):
        self.update_transfer()
        self.schema()

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
