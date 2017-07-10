# Project Electron Transfer QA Tests

## Feature: validate bag size and filename

	Scenario: bag size and filename validate successfully
		Given a bag does not contain special characters in the filename
			And the size is less than 500 gigabytes
		When the validation script is run.
		Then log bag info in database
			And success notifications are delivered to system
			And success notifications are delivered to client
			And trigger virus check feature

	Scenario: bag is too big
		Given a bag size exceeds 500 gigabytes
		When the validations script is run
		Then the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client

	Scenario: bag has invalid filename
		Given a bag has a special characters in a filename
		When the validations script is run
		Then the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client

## Feature: check bag for viruses

	Scenario: no virus is found
		Given a bag does not contain a virus
		When virus check script is run
		Then negative results are returned for all files within a bag
			And log bag info in database
			And success notifications are delivered to system
			And trigger validate bag structure feature

	Scenario: virus is found in bag
		Given a bag contains a virus
		When virus check script is run
		Then a positive result is returned for a file within a bag
			And the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client
			And Marist sysadmins are notified

## Feature: validate bag structure

	Scenario: bag is correctly structured
		Given bag contains bag declaration (bagit.txt) in top level of base directory
			And bag contains payload directory (/data)  in top level of base directory
			And bag contains payload manifest (manifest-<alg>.txt)  in top level of base directory
			And bag contains bag manifest (bag-info.txt)  in top level of base directory
		When bag validation script is run
		Then validation results are logged in database
			And success notifications are delivered to system
			And bag fixity validation is triggered

	Scenario: bag is missing bag declaration (bagit.txt)
		Given the bag does not contain the bag declaration with the filename bagit.txt  in top level of base directory
		When bag validation script is run
		Then bagit validation fails
			And the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client

	Scenario: bag is missing payload manifest (manifest-<alg>.txt)
		Given the bag does not contain the payload manifest with the filename manifest-<alg>.txt  in top level of base directory
		When bag validation script is run
		Then bagit validation fails
			And the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client

	Scenario: bag is missing bag manifest (bag-info.txt)
		Given the bag does not contain the bag manifest with the filename bag-info.txt  in top level of base directory
		When bag validation script is run
		Then bagit validation fails
			And the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client

	Scenario: bag is missing payload directory (/data)
		Given the bag does not contain the payload directory with the name "data"  in top level of base directory
		When bag validation script is run
		Then bagit validation fails
			And the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client

	Scenario: payload directory (/data) is empty
		Given bag contains bag declaration (bagit.txt) in top level of base directory
			And bag contains payload directory (/data) in top level of base directory
			And bag contains payload manifest (manifest-<alg>.txt) in top level of base directory
			And bag contains bag manifest (bag-info.txt) in top level of base directory
		When bag validation script is run
		Then validation results are logged in database
			And success notifications are delivered to system
			And bag fixity validation is triggered

## Feature: validate bag fixity

	Scenario: all bitstreams are unchanged
		Given pre and post transfer checksums are identical
		When bag validation script is run
			And checksums are calculated
		Then validation results are logged in database
			And success notifications are delivered to system
			And bag metadata is validated

	Scenario: one or more file has changed
		Given one or more pre-transfer checksum does not match a post-transfer checksum
		When bag validation script is run
			And checksums are calculated
		Then validation results are logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client
			And bag is deleted

## Feature: validate bag metadata

	Scenario: all metadata validation checks pass
		Given bag includes metadata.json file and bag-info.txt contains required information
		When metadata validation scripts are run
		Then metadata validation passes
			And success information is logged in database
			And success notifications are delivered to system

	Scenario: bag is missing the metadata.json file
		Given the bag is missing the required file
		When metadata validation scripts are run
		Then metadata validation fails
		And the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client

	Scenario: the bag-info.txt is missing required fields
		Given the bag-info.txt is missing required fields
		When metadata validation scripts are run
		Then metadata validation fails
			And the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client

	Scenario: non-repeatable fields repeat in bag-info.txt
		Given the bag-info.txt has non-repeatable fields repeating
		When metadata validation scripts are run
		Then metadata validation fails
			And the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client

	Scenario: a field’s data type in bag-info.txt doesn’t meet specifications
		Given data type’s content doesn’t adhere to RAC specification
		When metadata validation scripts are run
		Then metadata validation fails
			And the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client

	Scenario: locally controlled vocabularies in bag-info.txt data types don’t adhere to spec
		Given donor has used unsupported vocabulary in certain data types
		When metadata validation scripts are run
		Then metadata validation fails
			And the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client

## Feature: store valid bags

	Scenario: store bags when all checks pass
		Given all virus check and validation processes complete successfully
		When the validation script is run.
		Then log bag info in database
			And success notifications are delivered to system
			And success notifications are delivered to client

	Scenario: delete bags when one or more checks fail
		Given one or more virus check or validation process fails
		When the validation script is run.
		Then log bag info in database
			And the bag is deleted
			And error information is logged in database
			And error notifications are delivered to system
			And error notifications are delivered to client
