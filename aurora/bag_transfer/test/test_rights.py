# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast
from os.path import join
import random
from urlparse import urljoin

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse

from bag_transfer.test import helpers, setup
from bag_transfer.rights.forms import *
from bag_transfer.rights.models import *
from bag_transfer.rights.views import *
from bag_transfer.lib.bag_checker import bagChecker


class RightsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.record_types = helpers.create_test_record_types(setup.record_types)
        self.baglogcodes = helpers.create_test_baglogcodes()
        self.orgs = helpers.create_test_orgs(org_count=1)
        self.bags = helpers.create_target_bags('valid_bag', settings.TEST_BAGS_DIR, self.orgs[0])
        tr = helpers.run_transfer_routine()
        self.archives = []
        for transfer in tr.transfers:
            archive = helpers.create_test_archive(transfer, self.orgs[0])
            self.archives.append(archive)
        self.groups = helpers.create_test_groups(['managing_archivists'])
        self.user = helpers.create_test_user(username=settings.TEST_USER['USERNAME'], org=random.choice(self.orgs))
        for group in self.groups:
            self.user.groups.add(group)
        self.user.is_staff = True
        self.user.set_password(settings.TEST_USER['PASSWORD'])
        self.user.save()

    def test_rights(self):
        for record_type in self.record_types:
            helpers.create_rights_statement(
                record_type=record_type, org=random.choice(self.orgs),
                rights_basis=random.choice(setup.rights_bases))
        self.assertEqual(len(RightsStatement.objects.all()), len(self.record_types))

        for rights_statement in RightsStatement.objects.all():
            self.assemble_rights_statement(rights_statement)

        # Assign rights statements to archives
        for archive in self.archives:
            bag = bagChecker(archive)

            # this calls assign_rights
            self.assertTrue(bag.bag_passed_all())

        # Rights statements are cloned when assigned, so we should have more of them now
        assigned_length = len(RightsStatement.objects.all())
        self.assertEqual(assigned_length, len(setup.record_types)+len(self.archives))

        # Test GET views
        self.get_requests()

        # Test POST views
        self.post_requests()

        # Delete rights statements via AJAX
        self.ajax_requests()

        # Delete rights statement
        to_delete = random.choice(RightsStatement.objects.all())
        self.assertTrue(to_delete.delete())
        self.assertEqual(len(RightsStatement.objects.all()), assigned_length-1)

    #############################################
    # Functions used in Rights Statements tests #
    #############################################

    def assemble_rights_statement(self, rights_statement):
        helpers.create_rights_info(rights_statement=rights_statement)
        helpers.create_rights_granted(
            rights_statement=rights_statement, granted_count=random.randint(1, 2))

        # Make sure correct rights info objects were assigned
        rights_basis_type = setup.get_rights_basis_type(rights_statement)
        self.assertIsInstance(rights_statement.get_rights_info_object(), rights_basis_type)

        # Make sure RightsGranted objects were created
        self.assertIsNot(False, rights_statement.get_rights_granted_objects())

        # Assign rights statements to organization
        org = random.choice(self.orgs)
        rights_statement.organization = org
        rights_statement.save()
        self.assertTrue(org.rights_statements)

    def get_requests(self):
        self.client.login(username=self.user.username, password=settings.TEST_USER['PASSWORD'])
        for view in ['rights:edit', 'rights:detail']:
            rights_statement = random.choice(RightsStatement.objects.all())
            response = self.client.get(reverse(view, kwargs={'pk': rights_statement.pk}))
            self.assertEqual(response.status_code, 200)
        add_response = self.client.get(reverse('rights:add'), {'org': self.orgs[0].pk})
        self.assertEqual(add_response.status_code, 200)

        resp = self.client.get(reverse('organization-rights-statements', kwargs={'pk': self.orgs[0].pk}))
        self.assertEqual(resp.status_code, 200)

    def post_requests(self):
        # Creating new RightsStatements
        post_organization = random.choice(self.orgs)
        new_basis_data = random.choice(setup.basis_data)
        new_basis_data['organization'] = post_organization.pk
        new_basis_data.update(setup.grant_data)
        previous_length = len(RightsStatement.objects.all())
        new_request = self.client.post(
            urljoin(reverse('rights:add'), '?org={}'.format(post_organization.pk)), new_basis_data)
        self.assertEqual(
            new_request.status_code, 302, "Request was not successful")
        self.assertEqual(
            len(RightsStatement.objects.all()), previous_length+1,
            "{} Rights Statements were created, correct number is 1".format(len(RightsStatement.objects.all())-previous_length))
        self.assertEqual(
            RightsStatement.objects.last().rights_basis, new_basis_data['rights_basis'],
            "Rights bases do not match")

        # Updating RightsStatements
        rights_statement = RightsStatement.objects.last()
        updated_basis_data = new_basis_data
        if updated_basis_data['rights_basis'] == 'Other':
            basis_set = 'rightsstatementother_set'
            note_key = 'other_rights_note'
        else:
            basis_set = 'rightsstatement{}_set'.format(updated_basis_data['rights_basis'].lower())
            note_key = '{}_note'.format(updated_basis_data['rights_basis'].lower())
        updated_basis_data[basis_set+'-0-'+note_key] = 'Revised test note'
        basis_objects = getattr(rights_statement, basis_set).all()
        updated_basis_data[basis_set+'-0-id'] = basis_objects[0].pk
        update_request = self.client.post(
            reverse('rights:edit', kwargs={'pk': rights_statement.pk}),
            updated_basis_data)
        self.assertEqual(
            update_request.status_code, 302, "Request was not redirected")
        self.assertEqual(
            len(RightsStatement.objects.all()), previous_length+1,
            "Another rights statement was mistakenly created")

    def ajax_requests(self):
        rights_statement = RightsStatement.objects.last()
        delete_request = self.client.get(
            reverse('rights:api', kwargs={'pk': rights_statement.pk, 'action': 'delete'}),
            {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(delete_request.status_code, 200)
        resp = ast.literal_eval(delete_request.content)
        self.assertEqual(resp['success'], 1)
        non_ajax_request = self.client.get(
            reverse('rights:api', kwargs={'pk': rights_statement.pk, 'action': 'delete'}))
        self.assertEqual(non_ajax_request.status_code, 404)

    def tearDown(self):
        helpers.delete_test_orgs(self.orgs)
