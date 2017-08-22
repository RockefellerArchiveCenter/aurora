# Project Electron Transfer QA Tests

These tests are written in [Gherkin](https://github.com/cucumber/cucumber/wiki/Gherkin), a structured language that can be used for both documentation and automated testing of software.

## Feature: create and delete accounts

	Scenario: Create a new RAC user
		Given a valid RAC email address is provided
			And a valid password is provided
		When the email and password are entered
		Then the email and password are assigned to an LDAP user id
			And the user information is logged in database
			And success notification is delivered to the RAC user

	Scenario: Create a new organization
		Given a RAC user logs in with a valid email and password
			And a valid organization email is provided
			And an organization name is provided
			And the organization name does not already exist
		When the organization name and email are entered
		Then the organization name and email are assigned to an LDAP organization id
			And new directories are created for the organization
			And the organization information is logged in database
			And success notification is delivered to the RAC user

	Scenario: create a new organization user
		Given a RAC user logs in with a valid email and password
			And a valid org user email is provided
			And a valid org user password is provided
		When the org user email and password are entered
		Then the org user email and password are assigned to an LDAP user id
			And success notification is delivered to the RAC user
			And the changelog is updated

	Scenario: delete a RAC or org user
		Given a RAC user logs in with a valid email and password
			And a given RAC or org user exists
		When a RAC user deletes a user
		Then user is deleted from the system
			And success notification is delivered to the RAC user

## Feature: manage accounts

	Scenario: add an organization user to an organization
		Given a RAC user logs in with a valid email and password
			And a specified org user exists
			And a specified organization exists
		When a RAC user adds an org user to an organization
		Then org user is added to organization
			And organization assignment is logged in database
			And success notification is delivered to the RAC user

	Scenario: change a user password
		Given a user is logged in with valid email_1 and password_1
		When a user changes their password_1 to password_2
		Then a user can log in with the email_1 and password_2
			And a user can no longer log in with email_1 and password_1
			And password change is logged in database
			And success notification is delivered to the user

	Scenario: account is inactive
		[expand this]

## Feature: user login results

	Scenario: RAC user logs in
		Given a RAC user logs in with a valid email and password
		When login is successful
		Then RAC user can access Organization Admin IU
			And RAC user can access User Admin UI
			And RAC user can access Transfer Log, Detail View, and Error Message UIs for a specified organization

	Scenario: org user logs in
		Given: an org user logs in with a valid email and password
		When login is successful
		Then org user can access Transfer Log, Detail View, and Error Message UIs for their organization
			And user org can initiate transfers

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

	Scenario: virus definitions are out of date
		Given virus definitions are outdated
		When virus check script is triggered
		Then virus definitions are updated
			And the virus check script is run

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
		Given bag includes valid metadata.json file and bag-info.txt contains required information
		When metadata validation scripts are run
		Then metadata validation passes
			And success information is logged in database
			And success notifications are delivered to system

	Scenario: metadata.json is invalid
		Given a file named metadata.json exists in payload directory (/data)
			And metadata.json is not valid JSON or JSON-LD
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
