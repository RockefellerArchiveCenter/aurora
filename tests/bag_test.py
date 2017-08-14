from django.test import TestCase
from app.models import Bag
from app.models import BagProfile
from app.models import User
from app.models import Notification

class SizeTestCase(TestCase):
    def setUp(self):
        Bag.objects.create() # Add bag data
        User.objects.create() # Add users
        Notification.objects.create() # Add notifications

    def test_valid_size_bag(self):
        """Bag within size limit is processed"""
		# Given the size is less than 500 gigabytes
		# When the validation script is run.
		# Then log bag info in database
		# 	And success notifications are delivered to system
		# 	And success notifications are delivered to client
		# 	And trigger virus check feature

    def test_large_bag(self):
        """Bag larger than size limit is rejected"""
		# Given a bag size exceeds 500 gigabytes
		# When the validations script is run
		# Then the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

class FilenameTestCase(TestCase)
    def setUp(self):
        Bag.objects.create() # Add bag data
        User.objects.create() # Add users
        Notification.objects.create() # Add notifications

    def test_valid_filename(self):
        """Bag with no special characters in filename is processed"""
        # Given a bag does not special characters in a filename
		# When the validations script is run
		# Then log bag info in database
		# 	And success notifications are delivered to system
		# 	And success notifications are delivered to client
		# 	And trigger virus check feature

    def test_invalid_filename(self):
        """Bag with special characters in filename is rejected"""
		# Given a bag has a special characters in a filename
		# When the validations script is run
		# Then the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

class VirusCheckTestCase(TestCase)
    def setUp(self):
        Bag.objects.create() # Add bag data
        User.objects.create() # Add users
        Notification.objects.create() # Add notifications

	def pass_virus_check(self):
        """Bag without a virus is processed"""
		# Given a bag does not contain a virus
		# When virus check script is run
		# Then negative results are returned for all files within a bag
		# 	And log bag info in database
		# 	And success notifications are delivered to system
		# 	And trigger validate bag structure feature

	def fail_virus_check(self):
        """Bag with a virus is rejected"""
		# Given a bag contains a virus
		# When virus check script is run
		# Then a positive result is returned for a file within a bag
		# 	And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client
		# 	And Marist sysadmins are notified

	def update_definitions(self):
        """Virus definitions are updated before script is run"""
		# Given virus definitions are outdated
		# When virus check script is triggered
		# Then virus definitions are updated
		# 	And the virus check script is run

class BagStructureTestCase(TestCase)
    def setUp(self):
        Bag.objects.create() # Add bag data
        User.objects.create() # Add users
        Notification.objects.create() # Add notifications

	def test_valid bag(self):
        """Correctly structured bag is processed"""
		# Given bag contains bag declaration (bagit.txt) in top level of base directory
		# 	And bag contains payload directory (/data)  in top level of base directory
		# 	And bag contains payload manifest (manifest-<alg>.txt)  in top level of base directory
		# 	And bag contains bag manifest (bag-info.txt)  in top level of base directory
		# When bag validation script is run
		# Then validation results are logged in database
		# 	And success notifications are delivered to system
		# 	And bag fixity validation is triggered

	def missing_bag_declaration(self):
        """Bag missing bag declaration is rejected"""
        # Scenario: bag is missing bag declaration (bagit.txt)
		# Given the bag does not contain the bag declaration with the filename bagit.txt  in top level of base directory
		# When bag validation script is run
		# Then bagit validation fails
		# 	And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

	def missing_payload_manifest(self):
        """Bag missing payload manifest is rejected"""
		# Given the bag does not contain the payload manifest with the filename manifest-<alg>.txt  in top level of base directory
		# When bag validation script is run
		# Then bagit validation fails
		# 	And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

	def missing_bag_manifest(self):
        """Bag missing bag manifest is rejected"""
		# Given the bag does not contain the bag manifest with the filename bag-info.txt  in top level of base directory
		# When bag validation script is run
		# Then bagit validation fails
		# 	And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

	def missing_payload_directory(self):
        """Bag missing payload directory is rejected"""
		# Given the bag does not contain the payload directory with the name "data"  in top level of base directory
		# When bag validation script is run
		# Then bagit validation fails
		# 	And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

	def empty_payload_directory(self):
        """Bag with empty payload directory is rejected"""
		# Given bag contains bag declaration (bagit.txt) in top level of base directory
		# 	And bag contains payload directory (/data) in top level of base directory
		# 	And bag contains payload manifest (manifest-<alg>.txt) in top level of base directory
		# 	And bag contains bag manifest (bag-info.txt) in top level of base directory
		# When bag validation script is run
		# Then validation results are logged in database
		# 	And success notifications are delivered to system
		# 	And bag fixity validation is triggered

class BagFixityTestCase(TestCase)
    def setUp(self):
        Bag.objects.create() # Add bag data
        User.objects.create() # Add users
        Notification.objects.create() # Add notifications

	def valid_bag(self):
        """Bag with unchanged bitstreams is processed"""
		# Given pre and post transfer checksums are identical
		# When bag validation script is run
		# 	And checksums are calculated
		# Then validation results are logged in database
		# 	And success notifications are delivered to system
		# 	And bag metadata is validated

	def changed_file(self):
        """Bag with a changed file is rejected"""
		# Given one or more pre-transfer checksum does not match a post-transfer checksum
		# When bag validation script is run
		# 	And checksums are calculated
		# Then validation results are logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client
		# 	And bag is deleted

class BagMetadataCheckTestCase(TestCase)
    def setUp(self):
        Bag.objects.create() # Add bag data
        BagProfile.objects.create() # Add bag profile
        User.objects.create() # Add users
        Notification.objects.create() # Add notifications

	def valid_bag(self):
        """Bag including metadata.json file and bag-info.txt with required elements is processed"""
		# Given bag includes metadata.json file and bag-info.txt contains required information
		# When metadata validation scripts are run
		# Then metadata validation passes
		# 	And success information is logged in database
		# 	And success notifications are delivered to system

	def missing_metadata_file(self):
        """Bag with invalid metadata.json file is rejected"""
		# Given a file named metadata.json exists in payload directory (/data)
        #   And metadata.json is not valid JSON or JSON-LD
		# When metadata validation scripts are run
		# Then metadata validation fails
		#   And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

	def missing_required_fields(self):
        """Bag with missing fields in bag-info.txt is rejected"""
		# Given the bag-info.txt is missing required fields
		# When metadata validation scripts are run
		# Then metadata validation fails
		# 	And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

	def repeating_fields(self):
        """Bag containing repeating non-repeatable metadata fields in bag-info.txt is rejected"""
		# Given the bag-info.txt has non-repeatable fields repeating
		# When metadata validation scripts are run
		# Then metadata validation fails
		# 	And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

	def invalid_data_type(self):
        """A bag with a metadata element who's data type does not match specification is rejected"""
		# Given data type’s content doesn’t adhere to RAC specification
		# When metadata validation scripts are run
		# Then metadata validation fails
		# 	And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

	def unauthorized_term(self):
        """Bag containing metadata elements which do not adhere to locally controlled vocabularies is rejected"""
		# Given donor has used unsupported vocabulary in certain data types
		# When metadata validation scripts are run
		# Then metadata validation fails
		# 	And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client

class BagStorageTestCase(TestCase)
    def setUp(self):
        Bag.objects.create() # Add bag data
        User.objects.create() # Add users
        Notification.objects.create() # Add notifications

	def valid bag(self):
        """Bag which passes all checks is stored"""
		# Given all virus check and validation processes complete successfully
		# When the validation script is run.
		# Then log bag info in database
		# 	And success notifications are delivered to system
		# 	And success notifications are delivered to client

	def invalid_bag(self):
        """Bag which fails one or more test is rejected"""
		# Given one or more virus check or validation process fails
		# When the validation script is run.
		# Then log bag info in database
		# 	And the bag is deleted
		# 	And error information is logged in database
		# 	And error notifications are delivered to system
		# 	And error notifications are delivered to client
