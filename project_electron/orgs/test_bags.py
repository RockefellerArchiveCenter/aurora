# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import path, makedirs
from django.test import TestCase
from project_electron import config
from transfer_app.lib.bag_checker import bagChecker
from orgs.test_setup import *

class BagTest(TestCase):
    def setUp():
        if path.isdir(config.TESTING_TMP_DIR):
            FH.remove_file_or_dir(config.TESTING_TMP_DIR)
        else:
            makedirs(config.TESTING_TMP_DIR)

    def tearDown():
        print "tearing down"
        FH.remove_file_or_dir(config.TESTING_TMP_DIR)

    def test_large_bag(self):
        """Bag larger than size limit is rejected"""
        pass
		# Given a bag size exceeds size limit
		# When the validations script is run
		# Then the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

    def test_invalid_filename(self):
        """Bag with special characters in filename is rejected"""
        pass
		# Given a bag has a special characters in a filename
		# When the validations script is run
		# Then the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

	def test_virus_check(self):
        """Bag with a virus is rejected"""
        pass
		# Given a bag contains a virus
		# When virus check script is run
		# Then a positive result is returned for a file within a bag
		# 	And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client
		# 	And Marist sysadmins are notified

	def test_update_definitions(self):
        """Virus definitions are updated before script is run"""
        pass
		# Given virus definitions are outdated
		# When virus check script is triggered
		# Then virus definitions are updated
		# 	And the virus check script is run

	def test_missing_bag_declaration(self):
        """Bag missing bag declaration is rejected"""
        bag_names = ['missing_bag_declaration', 'missing_bag_declaration.zip', 'missing_bag_declaration.tar', 'missing_bag_declaration.tar.gz']
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertFalse(bag._is_generic_bag())

	def test_missing_payload_manifest(self):
        """Bag missing payload manifest is rejected"""
        bag_names = ['missing_payload_manifest', 'missing_payload_manifest.zip', 'missing_payload_manifest.tar', 'missing_payload_manifest.tar.gz']
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertFalse(bag._is_generic_bag())

	def test_missing_bag_manifest(self):
        """Bag missing bag manifest is rejected"""
        bag_names = ['missing_bag_manifest', 'missing_bag_manifest.zip', 'missing_bag_manifest.tar', 'missing_bag_manifest.tar.gz']
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertFalse(bag._is_generic_bag())

	def test_missing_payload_directory(self):
        """Bag missing payload directory is rejected"""
        bag_names = ['missing_payload_directory', 'missing_payload_directory.zip', 'missing_payload_directory.tar', 'missing_payload_directory.tar.gz']
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertFalse(bag._is_generic_bag())

	def test_empty_payload_directory(self):
        """Bag with empty payload directory is rejected"""
        bag_names = ['empty_payload_directory', 'empty_payload_directory.zip', 'empty_payload_directory.tar', 'empty_payload_directory.tar.gz']
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertFalse(bag._is_generic_bag())

	def test_changed_file(self):
        """Bag with a changed file is rejected"""
        bag_names = ['changed_file', 'changed_file.zip', 'changed_file.tar', 'changed_file.tar.gz']
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertFalse(bag._is_generic_bag())

	def test_invalid_metadata_file(self):
        """Bag with invalid metadata.json file is rejected"""
        bag_names = ['invalid_metadata_file', 'invalid_metadata_file.zip', 'invalid_metadata_file.tar', 'invalid_metadata_file.tar.gz']
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertFalse(bag._has_valid_metadata_file())

	def test_no_metadata_file(self):
        """Bag with invalid metadata.json file is rejected"""
        bag_names = ['no_metadata_file', 'no_metadata_file.zip', 'no_metadata_file.tar', 'no_metadata_file.tar.gz']
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertTrue(bag._has_valid_metadata_file())

	def test_missing_required_fields(self):
        """Bag with missing fields in bag-info.txt is rejected"""
        bag_names = ['missing_description', 'missing_description.zip', 'missing_description.tar', 'missing_description.tar.gz', 'missing_record_type', 'missing_record_type.zip', 'missing_record_type.tar', 'missing_record_type.tar.gz', 'missing_source_organization', 'missing_source_organization.zip', 'missing_source_organization.tar', 'missing_source_organization.tar.gz', 'missing_title', 'missing_title.zip', 'missing_title.tar', 'missing_title.tar.gz', ]
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertFalse(bag._is_rac_bag())

	def test_repeating_fields(self):
        """Bag containing repeating non-repeatable metadata fields in bag-info.txt is rejected"""
        bag_names = ['repeating_record_type', 'repeating_record_type.zip', 'repeating_record_type.tar', 'repeating_record_type.tar.gz', 'repeating_source_organization', 'repeating_source_organization.zip', 'repeating_source_organization.tar', 'repeating_source_organization.tar.gz', 'repeating_title', 'repeating_title.zip', 'repeating_title.tar', 'repeating_title.tar.gz', ]
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertFalse(bag._is_rac_bag())

	def test_invalid_data_type(self):
        """A bag containing a metadata element that does not conform to datatype specification is rejected"""
		bag_names = ['invalid_datatype_date', 'invalid_datatype_date.zip', 'invalid_datatype_date.tar', 'invalid_datatype_date.tar.gz', 'invalid_datatype_language', 'invalid_datatype_language.zip', 'invalid_datatype_language.tar', 'invalid_datatype_language.tar.gz']
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertFalse(bag._has_valid_datatypes())

	def test_unauthorized_term(self):
        """Bag containing metadata elements which do not adhere to locally controlled vocabularies is rejected"""
        bag_names = ['unauthorized_record_type', 'unauthorized_record_type.zip', 'unauthorized_record_type.tar', 'unauthorized_record_type.tar.gz', 'unauthorized_source_organization', 'unauthorized_source_organization.zip', 'unauthorized_source_organization.tar', 'unauthorized_source_organization.tar.gz']
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertFalse(bag._is_rac_bag())

	def test_valid_bag(self):
        """Bag which passes all checks is stored"""
        bag_names = ['valid_bag', 'valid_bag.zip', 'valid_bag.tar', 'valid_bag.tar.gz']
        for name in bag_names:
            archive = set_up_archive_object('test_bags/{}'.format(name))
            bag = bagChecker(archive)
            self.assertTrue(bag.bag_passed_all())
