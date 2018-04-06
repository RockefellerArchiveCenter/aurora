# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast
from os.path import join
import random
from urlparse import urljoin
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from orgs import test_helpers
from orgs.form import BagItProfileForm, BagItProfileBagInfoForm, BagItProfileBagInfoValuesForm, ManifestsRequiredForm, AcceptSerializationForm, AcceptBagItVersionForm, TagFilesRequiredForm, TagManifestsRequiredForm, BagItProfileBagInfoFormset, BaseBagInfoFormset, BagItProfileBagInfoFormset, ManifestsRequiredFormset, AcceptSerializationFormset, AcceptBagItVersionFormset, TagFilesRequiredFormset, TagManifestsRequiredFormset
from orgs.models import BagItProfile, ManifestsRequired, AcceptSerialization, AcceptBagItVersion, TagFilesRequired, TagManifestsRequired, BagItProfileBagInfo, BagItProfileBagInfoValues
from orgs.test.setup_tests import *
from orgs.views import BagItProfileManageView, BagItProfileAPIAdminView
from transfer_app.lib.bag_checker import bagChecker


class BagItProfileTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.orgs = test_helpers.create_test_orgs(org_count=1)
        self.bags = test_helpers.create_target_bags('valid_bag', settings.TEST_BAGS_DIR, self.orgs[0])
        tr = test_helpers.run_transfer_routine()
        self.archives = []
        for transfer in tr.transfers:
            archive = test_helpers.create_test_archive(transfer, self.orgs[0])
            self.archives.append(archive)
        self.groups = test_helpers.create_test_groups(['managing_archivists'])
        self.user = test_helpers.create_test_user(username=settings.TEST_USER['USERNAME'], org=random.choice(self.orgs))
        self.user.groups = self.groups
        self.bagitprofiles = []
        self.baginfos = []

    def test_bagitprofiles(self):
        for org in self.orgs:
            profile = test_helpers.create_test_bagitprofile(applies_to_organization=org)
            self.bagitprofiles.append(profile)
        self.assertEqual(len(self.bagitprofiles), len(self.orgs))

        for profile in self.bagitprofiles:
            test_helpers.create_test_manifestsrequired(bagitprofile=profile)
            test_helpers.create_test_acceptserialization(bagitprofile=profile)
            test_helpers.create_test_acceptbagitversion(bagitprofile=profile)
            test_helpers.create_test_tagmanifestsrequired(bagitprofile=profile)
            test_helpers.create_test_tagfilesrequired(bagitprofile=profile)
            for field in BAGINFO_FIELD_CHOICES:
                baginfo = test_helpers.create_test_bagitprofilebaginfo(bagitprofile=profile, field=field)
                self.baginfos.append(baginfo)

            for info in self.baginfos:
                test_helpers.create_test_bagitprofilebaginfovalues(baginfo=info)


            # Get org's bagit profiles

        # Validate against BagIt Profiles
        for archive in self.archives:
            bag = bagChecker(archive)

            # this calls assign_rights
            self.assertTrue(bag.bag_passed_all())

        # Test GET views
        self.client.login(username=self.user.username, password=settings.TEST_USER['PASSWORD'])
        profile = random.choice(self.bagitprofiles)
        org = profile.applies_to_organization
        response = self.client.get(reverse('bagit-profiles-edit', kwargs={'pk': org.pk, 'profile_pk': profile.pk}))
        self.assertEqual(response.status_code, 200)
        add_response = self.client.get(reverse('bagit-profiles-add', kwargs={'pk': self.orgs[0].pk}))
        self.assertEqual(add_response.status_code, 200)

        # Creating new RightsStatements
        # post_organization = random.choice(self.orgs)
        # new_basis_data = random.choice(basis_data)
        # new_request = self.client.post(
        #     urljoin(reverse('rights-add'), '?org={}'.format(post_organization.pk)), new_basis_data)
        # self.assertEqual(
        #     new_request.status_code, 302, "Request was not redirected")
        # self.assertEqual(
        #     len(RightsStatement.objects.all()), assigned_length+1,
        #     "Another rights statement was mistakenly created")
        # self.assertEqual(
        #     RightsStatement.objects.last().rights_basis, new_basis_data['rights_basis'],
        #     "Rights bases do not match")

        # Updating RightsStatements
        # rights_statement = RightsStatement.objects.last()
        # updated_basis_data = new_basis_data
        # if updated_basis_data['rights_basis'] == 'Other':
        #     basis_set = 'rightsstatementother_set'
        #     note_key = 'other_rights_note'
        # else:
        #     basis_set = 'rightsstatement{}_set'.format(updated_basis_data['rights_basis'].lower())
        #     note_key = '{}_note'.format(updated_basis_data['rights_basis'].lower())
        # updated_basis_data[basis_set+'-0-'+note_key] = 'Revised test note'
        # basis_objects = getattr(rights_statement, basis_set).all()
        # updated_basis_data[basis_set+'-0-id'] = basis_objects[0].pk
        # update_request = self.client.post(
        #     reverse('rights-update', kwargs={'pk': rights_statement.pk}),
        #     updated_basis_data)
        # self.assertEqual(
        #     update_request.status_code, 302, "Request was not redirected")
        # self.assertEqual(
        #     len(RightsStatement.objects.all()), assigned_length+1,
        #     "Another rights statement was mistakenly created")

        # RightsStatementRightsGranted
        # grant_request = self.client.post(
        #     reverse('rights-grants', kwargs={'pk': rights_statement.pk}), grant_data)
        # self.assertEqual(
        #     grant_request.status_code, 302, "Request was not redirected")

        # Delete rights statements
        # delete_request = self.client.get(
        #     reverse('rights-api', kwargs={'pk': rights_statement.pk, 'action': 'delete'}),
        #     {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # self.assertEqual(delete_request.status_code, 200)
        # resp = ast.literal_eval(delete_request.content)
        # self.assertEqual(resp['success'], 1)
        # non_ajax_request = self.client.get(
        #     reverse('rights-api', kwargs={'pk': rights_statement.pk, 'action': 'delete'}))
        # self.assertEqual(non_ajax_request.status_code, 404)

        # Delete bagit profile
        previous_len = len(self.bagitprofiles)
        to_delete = random.choice(self.bagitprofiles)
        self.assertTrue(to_delete.delete())
        self.assertEqual(len(BagItProfile.objects.all()), previous_len-1)

    def tearDown(self):
        test_helpers.delete_test_orgs(self.orgs)
