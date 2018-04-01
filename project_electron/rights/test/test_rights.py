# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pwd
from datetime import datetime
from django.test import TransactionTestCase, RequestFactory
from django.conf import settings
from django.urls import reverse
from rights.test.setup_tests import *
from orgs.models import Archives, Organization, User
from orgs.test import setup_tests as org_setup
from rights.models import *
from rights.views import *

RECORD_TYPES = [
    "administrative records", "board materials",
    "communications and publications", "grant records",
    "annual reports"]


class RightsTestCase(TransactionTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.record_types = create_record_types(RECORD_TYPES)
        self.orgs = create_test_orgs()
        self.archives = create_test_archives(self.orgs)
        self.groups = create_test_groups(['managing_archivists'])
        print self.groups
        self.user = User.objects.create_user(
            organization=random.choice(self.orgs),
            username='Test User', email="test@example.com",
            )
        self.user.groups = self.groups

    def create_rights_statement(self, record_type):
        rights_bases = ['Copyright', 'Statute', 'License', 'Other']
        rights_statement = RightsStatement(
            organization=random.choice(self.orgs),
            applies_to_type=record_type,
            rights_basis=random.choice(rights_bases),
        )
        rights_statement.save()

    def create_rights_info(self, rights_statement):
        if rights_statement.rights_basis == 'Statute':
            rights_info = RightsStatementStatute(
                statute_citation=random_string(50),
                statute_applicable_start_date=random_date(1960),
                statute_applicable_end_date=random_date(1990),
                statute_end_date_period=20,
                statute_note=random_string(40)
            )
        elif rights_statement.rights_basis == 'Other':
            rights_info = RightsStatementOther(
                other_rights_basis=random.choice(['Donor', 'Policy']),
                other_rights_applicable_start_date=random_date(1978),
                other_rights_end_date_period=20,
                other_rights_end_date_open=True,
                other_rights_note=random_string(50)
            )
        elif rights_statement.rights_basis == 'Copyright':
            rights_info = RightsStatementCopyright(
                copyright_status=random.choice(['copyrighted', 'public domain', 'unknown']),
                copyright_applicable_start_date=random_date(1950),
                copyright_end_date_period=40,
                copyright_note=random_string(70)
            )
        elif rights_statement.rights_basis == 'License':
            rights_info = RightsStatementLicense(
                license_applicable_start_date=random_date(1980),
                license_start_date_period=10,
                license_end_date_open=True,
                license_note=random_string(60)
            )
        rights_info.rights_statement = rights_statement
        rights_info.save()

    def create_rights_granted(self, rights_statement):
        for x in xrange(random.randint(1, 2)):
            rights_granted = RightsStatementRightsGranted(
                rights_statement=rights_statement,
                act=random.choice(['publish', 'disseminate','replicate', 'migrate', 'modify', 'use', 'delete']),
                start_date=random_date(1984),
                end_date_period=15,
                rights_granted_note=random_string(100),
                restriction=random.choice(['allow', 'disallow', 'conditional'])
                )
            rights_granted.save()

    def test_rights(self):
        for record_type in RECORD_TYPES:
            self.create_rights_statement(record_type)
        self.assertEqual(len(RightsStatement.objects.all()), len(RECORD_TYPES))

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
            remove_file_or_dir(os.path.join(settings.TRANSFER_EXTRACT_TMP, archive.bag_it_name))
            remove_file_or_dir(archive.machine_file_path)

        # Rights statements are cloned when assigned, so we should have more of them now
        assigned_length = len(RightsStatement.objects.all())
        self.assertEqual(assigned_length, len(RECORD_TYPES)+len(Archives.objects.all()))

        # Test GET requests in views
        for view in (
                ('rights-update', RightsManageView),
                ('rights-grants', RightsGrantsManageView),
                ('rights-detail', RightsDetailView),
                ('rights-add', 'RightsManageView'),
                ):
            rights_statement = random.choice(RightsStatement.objects.all())
            request = self.factory.get(reverse(view[0], kwargs={"pk": rights_statement.pk}))
            request.user = self.user
            response = view[1].as_view()(request, pk=rights_statement.pk)
            self.assertEqual(response.status_code, 200)
            # test rights-detail and rights-grants get_context_data function

        # Test POST requests in views
        rights_statement = random.choice(RightsStatement.objects.all())

        # Create new rights statement
        new_request = self.factory.post(reverse('rights-add'), rights_statement)
        new_request.user = self.user
        update_response = RightsManageView.as_view()(new_request)
        self.assertEqual(update_response.status_code, 200)

        # Update rights statement
        update_request = self.factory.post(reverse('rights-update', kwargs={"pk": rights_statement.pk}), rights_statement)
        update_request.user = self.user
        update_response = RightsManageView.as_view()(update_request, pk=rights_statement.pk)
        self.assertEqual(update_response.status_code, 200)

        # Add rights granted
        grant_request = self.factory.post(reverse('rights-grants', kwargs={"pk": rights_statement.pk}), rights_statement)
        grant_request.user = self.user
        grant_response = RightsGrantsManageView.as_view()(grant_request, pk=rights_statement.pk)
        self.assertEqual(grant_response.status_code, 200)

        # Delete rights statements
        delete_request = self.factory.post(reverse('rights-delete', kwargs={"pk": rights_statement.pk}), rights_statement)
        delete_request.user = self.user
        delete_response = RightsGrantsManageView.as_view()(delete_request, pk=rights_statement.pk, action='delete')
        self.assertEqual(delete_response.status_code, 200)

        # non ajax requests
        # action != delete

        # Delete rights statement
        to_delete = random.choice(RightsStatement.objects.all())
        self.assertTrue(to_delete.delete())
        self.assertEqual(len(RightsStatement.objects.all()), assigned_length-1) # this is going to fail

    def tearDown(self):
        org_setup.delete_test_orgs(self.orgs)
