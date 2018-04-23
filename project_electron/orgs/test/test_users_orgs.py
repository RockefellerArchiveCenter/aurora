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
from orgs import test_helpers
from orgs.models import Archives, User
from orgs.test import setup_tests
from orgs.appraise.views import AppraiseView
from orgs.lib.bag_checker import bagChecker

org_count = 1


class UserOrgTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.orgs = test_helpers.create_test_orgs(org_count=org_count)
        self.bags = test_helpers.create_target_bags('valid_bag', settings.TEST_BAGS_DIR, self.orgs[0])
        tr = test_helpers.run_transfer_routine()
        self.archives = []
        for transfer in tr.transfers:
            archive = test_helpers.create_test_archive(transfer, self.orgs[0])
            self.archives.append(archive)

    def test_users(self):
        for user in (('donor', 'ra00001'), ('managing_archivists', 'va0425'), ('appraisal_archivists', 'va0426'), ('accessioning_archivists', 'va0427')):
            group = test_helpers.create_test_groups([user[0]])
            user = test_helpers.create_test_user(username=user[1], org=random.choice(self.orgs))
            user.groups = group

        # Group name, assertTrue methods, assertFalse methods
        user_list = (
            ('donor', [], ['is_archivist', 'can_appraise', 'is_manager'], ''),
            ('managing_archivists', ['is_archivist', 'can_appraise', 'is_manager'], [], 'MANAGING'),
            ('accessioning_archivists', ['is_archivist'], ['can_appraise', 'is_manager'], 'ACCESSIONER'),
            ('appraisal_archivists', ['is_archivist', 'can_appraise'], ['is_manager'], 'APPRAISER'),
        )
        for u in user_list:
            user = User.objects.get(groups__name=u[0])
            for meth in u[1]:
                self.assertTrue(getattr(user, meth)())
            for meth in u[2]:
                self.assertFalse(getattr(user, meth)())
            if len(u[3]) > 1:
                self.assertTrue(user.has_privs(u[3]))

        # Test user views
        self.user_views()

    def test_orgs(self):
        group = test_helpers.create_test_groups(['managing_archivists'])
        user = test_helpers.create_test_user(username=settings.TEST_USER['USERNAME'], org=random.choice(self.orgs))
        user.groups = group
        self.client.login(username=user.username, password=settings.TEST_USER['PASSWORD'])

        # Test Org views
        self.org_views()

    def tearDown(self):
        test_helpers.delete_test_orgs(self.orgs)

    def user_views(self):
        user = User.objects.get(groups__name='managing_archivists')
        self.client.login(username=user.username, password=settings.TEST_USER['PASSWORD'])

        for view in ['users-detail', 'users-add', 'users-edit']:
            response = self.client.get(reverse(view, kwargs={'pk': random.choice(User.objects.all()).pk}))
            self.assertEqual(response.status_code, 200)

        user_data = setup_tests.user_data
        user_data['organization'] = random.choice(self.orgs)
        response = self.client.post(reverse('users-add', kwargs={'pk': random.choice(User.objects.all()).pk}), user_data)
        self.assertTrue(response.status_code, 200)

        # make user inactive
        user_data['active'] = False
        response = self.client.post(reverse('users-edit', kwargs={'pk': random.choice(User.objects.all()).pk}), user_data)
        self.assertTrue(response.status_code, 200)

    def org_views(self):
        response = self.client.get(reverse('orgs-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), org_count)
        for view in ['orgs-detail', 'orgs-edit']:
            response = self.client.get(reverse(view, kwargs={'pk': random.choice(self.orgs).pk}))
            self.assertEqual(response.status_code, 200)

        org_data = setup_tests.org_data
        response = self.client.post(reverse('orgs-add'), org_data)
        self.assertTrue(response.status_code, 200)

        # make org inactive
        org_data['active'] = False
        response = self.client.post(reverse('orgs-edit', kwargs={'pk': random.choice(self.orgs).pk}), org_data)
        self.assertTrue(response.status_code, 200)
