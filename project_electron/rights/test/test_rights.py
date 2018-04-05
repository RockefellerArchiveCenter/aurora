# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast
from os.path import join
import random
from urlparse import urljoin
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from orgs.test import setup_tests as org_setup
from orgs import test_helpers
from rights.forms import *
from rights.models import *
from rights.test.setup_tests import *
from rights.views import *
from transfer_app.lib import files_helper as FH
from transfer_app.lib.bag_checker import bagChecker


class RightsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.record_types = test_helpers.create_test_record_types(record_types)
        self.orgs = org_setup.create_test_orgs(org_count=1)
        self.archives = test_helpers.create_test_archives(self.orgs)
        self.groups = test_helpers.create_test_groups(['managing_archivists'])
        self.user = test_helpers.create_test_user(username=settings.TEST_USER['USERNAME'], org=random.choice(self.orgs))
        self.user.groups = self.groups

    def test_rights(self):
        for record_type in self.record_types:
            test_helpers.create_rights_statement(
                record_type=record_type, org=random.choice(self.orgs),
                rights_basis=random.choice(rights_bases))
        self.assertEqual(len(RightsStatement.objects.all()), len(self.record_types))

        for rights_statement in RightsStatement.objects.all():
            test_helpers.create_rights_info(rights_statement=rights_statement)
            test_helpers.create_rights_granted(rights_statement=rights_statement, granted_count=random.randint(1, 2))

            # Make sure correct rights info objects were assigned
            if rights_statement.rights_basis == 'Statute':
                self.assertIsInstance(rights_statement.get_rights_info_object(), RightsStatementStatute)
            elif rights_statement.rights_basis == 'Other':
                self.assertIsInstance(rights_statement.get_rights_info_object(), RightsStatementOther)
            elif rights_statement.rights_basis == 'Copyright':
                self.assertIsInstance(rights_statement.get_rights_info_object(), RightsStatementCopyright)
            elif rights_statement.rights_basis == 'License':
                self.assertIsInstance(rights_statement.get_rights_info_object(), RightsStatementLicense)

            # Make sure RightsGranted objects were created
            self.assertIsNot(False, rights_statement.get_rights_granted_objects())

            # Assign rights statements to organization
            org = random.choice(self.orgs)
            rights_statement.organization = org
            rights_statement.save()
            self.assertTrue(org.rights_statements)

        # Assign rights statements to archives
        for archive in self.archives:
            bag = bagChecker(archive)

            # this calls assign_rights
            self.assertTrue(bag.bag_passed_all())

            # # deleting path in processing and tmp dir
            FH.remove_file_or_dir(join(settings.TRANSFER_EXTRACT_TMP, archive.bag_it_name))
            FH.remove_file_or_dir(archive.machine_file_path)

        # Rights statements are cloned when assigned, so we should have more of them now
        assigned_length = len(RightsStatement.objects.all())
        self.assertEqual(assigned_length, len(record_types)+len(self.archives))

        # Test GET views
        self.client.login(username=self.user.username, password=settings.TEST_USER['PASSWORD'])
        for view in ['rights-update', 'rights-grants', 'rights-detail']:
            rights_statement = random.choice(RightsStatement.objects.all())
            response = self.client.get(reverse(view, kwargs={'pk': rights_statement.pk}))
            self.assertEqual(response.status_code, 200)
        add_response = self.client.get(reverse('rights-add'), {'org': self.orgs[0].pk})
        self.assertEqual(add_response.status_code, 200)

        # Creating new RightsStatements
        post_organization = random.choice(self.orgs)
        new_basis_data = random.choice(basis_data)
        new_request = self.client.post(urljoin(reverse('rights-add'), '?org={}'.format(post_organization.pk)), new_basis_data)
        self.assertEqual(new_request.status_code, 302, "Request was not redirected")
        self.assertEqual(len(RightsStatement.objects.all()), assigned_length+1, "Another rights statement was mistakenly created")
        self.assertEqual(RightsStatement.objects.last().rights_basis, new_basis_data['rights_basis'], "Rights bases do not match")

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
        update_request = self.client.post(reverse('rights-update', kwargs={'pk': rights_statement.pk}), updated_basis_data)
        self.assertEqual(update_request.status_code, 302, "Request was not redirected")
        self.assertEqual(len(RightsStatement.objects.all()), assigned_length+1, "Another rights statement was mistakenly created")

        # RightsStatementRightsGranted
        grant_request = self.client.post(reverse('rights-grants', kwargs={'pk': rights_statement.pk}), grant_data)
        self.assertEqual(grant_request.status_code, 302, "Request was not redirected")

        # Delete rights statements
        delete_request = self.client.get(reverse('rights-api', kwargs={'pk': rights_statement.pk, 'action': 'delete'}), {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(delete_request.status_code, 200)
        resp = ast.literal_eval(delete_request.content)
        self.assertEqual(resp['success'], 1)
        non_ajax_request = self.client.get(reverse('rights-api', kwargs={'pk': rights_statement.pk, 'action': 'delete'}))
        self.assertEqual(non_ajax_request.status_code, 404)

        # Delete rights statement
        to_delete = random.choice(RightsStatement.objects.all())
        self.assertTrue(to_delete.delete())
        self.assertEqual(len(RightsStatement.objects.all()), assigned_length-1)

    def tearDown(self):
        org_setup.delete_test_orgs(self.orgs)
