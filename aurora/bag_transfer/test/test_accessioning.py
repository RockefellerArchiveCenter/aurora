# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast
import json
from os.path import join
import random
from urlparse import urljoin

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse

from bag_transfer.test import helpers
from bag_transfer.models import Archives, RecordCreators
from bag_transfer.accession.models import Accession
from bag_transfer.accession.forms import CreatorsFormSet
from bag_transfer.lib.bag_checker import bagChecker


class AccessioningTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.orgs = helpers.create_test_orgs(org_count=1)
        self.record_creators = helpers.create_test_record_creators(count=3)
        self.bags = helpers.create_target_bags('valid_bag', settings.TEST_BAGS_DIR, self.orgs[0])
        tr = helpers.run_transfer_routine()
        self.archives = []
        for transfer in tr.transfers:
            archive = helpers.create_test_archive(transfer, self.orgs[0])
            self.archives.append(archive)
        self.groups = helpers.create_test_groups(['accessioning_archivists'])
        self.user = helpers.create_test_user(username=settings.TEST_USER['USERNAME'], org=random.choice(self.orgs))
        for group in self.groups:
            self.user.groups.add(group)
        self.user.is_staff = True
        self.user.set_password(settings.TEST_USER['PASSWORD'])
        self.user.save()
        self.client.login(username=self.user.username, password=settings.TEST_USER['PASSWORD'])

    def test_accessioning(self):
        transfer_ids = []
        for archive in self.archives:
            archive.process_status = Archives.ACCEPTED
            archive.save()
            transfer_ids.append(str(archive.id))
        id_list = ','.join(transfer_ids)

        # Test GET views
        print "Testing GET views"
        self.get_views(id_list)

        # Test POST view
        print "Testing POST views"
        self.post_views(id_list)

        # Test detail view
        print "Testing detail view"
        self.detail_view()

    def get_views(self, id_list):
        list_response = self.client.get(reverse('accession:list'))
        self.assertEqual(list_response.status_code, 200)

        # These are all the same transfer so there should only be one transfer group
        transfer_group = list_response.context['uploads'][0].transfer_group
        for upload in list_response.context['uploads']:
            self.assertEqual(upload.transfer_group, transfer_group)
        self.assertEqual(len(list_response.context['uploads']), len(self.archives))

        record_response = self.client.get(reverse('accession:add'), {'transfers': id_list})
        self.assertEqual(record_response.status_code, 200)

    def post_views(self, id_list):
        accession_data = helpers.get_accession_data(creator=random.choice(RecordCreators.objects.all()))
        new_request = self.client.post("{}?transfers={}".format(reverse('accession:add'), id_list), accession_data)
        self.assertEqual(new_request.status_code, 302, "Wrong HTTP response code")

    def detail_view(self):
        accession = random.choice(Accession.objects.all())
        accession_response = self.client.get(reverse('accession:detail', kwargs={'pk': accession.pk}))
        self.assertEqual(accession_response.status_code, 200)

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
