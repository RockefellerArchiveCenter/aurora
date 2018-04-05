# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast
from os.path import join
import random
from urlparse import urljoin
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from orgs.models import Archives, User
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
        self.user = User.objects.create_user(
            organization=random.choice(self.orgs),
            username=settings.TEST_USER['USERNAME'], email="test@example.com",
            )
        self.user.groups = self.groups

    def create_rights_statement(self, record_type):
        rights_statement = RightsStatement(
            organization=random.choice(self.orgs),
            rights_basis=random.choice(rights_bases),
        )
        rights_statement.save()
        rights_statement.applies_to_type.add(record_type)

    def create_rights_info(self, rights_statement):
        if rights_statement.rights_basis == 'Statute':
            rights_info = RightsStatementStatute(
                statute_citation=test_helpers.random_string(50),
                statute_applicable_start_date=test_helpers.random_date(1960),
                statute_applicable_end_date=test_helpers.random_date(1990),
                statute_end_date_period=20,
                statute_note=test_helpers.random_string(40)
            )
        elif rights_statement.rights_basis == 'Other':
            rights_info = RightsStatementOther(
                other_rights_basis=random.choice(['Donor', 'Policy']),
                other_rights_applicable_start_date=test_helpers.random_date(1978),
                other_rights_end_date_period=20,
                other_rights_end_date_open=True,
                other_rights_note=test_helpers.random_string(50)
            )
        elif rights_statement.rights_basis == 'Copyright':
            rights_info = RightsStatementCopyright(
                copyright_status=random.choice(['copyrighted', 'public domain', 'unknown']),
                copyright_applicable_start_date=test_helpers.random_date(1950),
                copyright_end_date_period=40,
                copyright_note=test_helpers.random_string(70)
            )
        elif rights_statement.rights_basis == 'License':
            rights_info = RightsStatementLicense(
                license_applicable_start_date=test_helpers.random_date(1980),
                license_start_date_period=10,
                license_end_date_open=True,
                license_note=test_helpers.random_string(60)
            )
        rights_info.rights_statement = rights_statement
        rights_info.save()

    def create_rights_granted(self, rights_statement):
        all_rights_granted = []
        for x in xrange(random.randint(1, 2)):
            rights_granted = RightsStatementRightsGranted(
                rights_statement=rights_statement,
                act=random.choice(['publish', 'disseminate','replicate', 'migrate', 'modify', 'use', 'delete']),
                start_date=test_helpers.random_date(1984),
                end_date_period=15,
                rights_granted_note=test_helpers.random_string(100),
                restriction=random.choice(['allow', 'disallow', 'conditional'])
                )
            rights_granted.save()
            all_rights_granted.append(rights_granted)
        return all_rights_granted

    def test_rights(self):
        for record_type in self.record_types:
            self.create_rights_statement(record_type)
        self.assertEqual(len(RightsStatement.objects.all()), len(self.record_types))

        for rights_statement in RightsStatement.objects.all():
            self.create_rights_info(rights_statement)
            self.create_rights_granted(rights_statement)

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
        self.assertEqual(assigned_length, len(record_types)+len(Archives.objects.all()))

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
