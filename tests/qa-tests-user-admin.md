# Project Electron Transfer QA Tests for User Admin

These tests are written in [Gherkin](https://github.com/cucumber/cucumber/wiki/Gherkin), a structured language that can be used for both documentation and automated testing of software.

## Feature: create and delete accounts

	Scenario: Create a new user
		Given a valid email address is provided
			And a valid password is provided
			And a first name is provided
			And a last name is provided
		When user information is entered
		Then user information is assigned an LDAP user id
			And user information is added to ldap
			And user id is added to system
			And success notification is logged in system
			And success notification is displayed

	Scenario: Create a new organization
		Given a RAC admin user is logged in
			And a valid organization email address is provided
			And an organization name is provided
			And an organization description is provided
			And the organization name does not already exist
		When organization information is entered
		Then organization information is assigned to an LDAP group id
			And directories are created for the organization
			And organization information is added to ldap
			And organization id is added to system
			And organization status is marked as active
			And success notification is logged in system
			And success notification is displayed

## Feature: manage accounts

	Scenario: add a user to an organization
		Given a RAC admin user is logged in
			And a specified user exists
			And a specified organization exists
			And a specified organization status is active
		When RAC admin user adds user to organization
		Then organization assignment is applied in ldap
			And success notification is logged in system
			And success notification is displayed

	Scenario: change a user password
		Given a user is logged in with valid email_1 and password_1
		When a user changes their password_1 to password_2
		Then user can log in with the email_1 and password_2
			And user can no longer log in with email_1 and password_1
			And password change is applied in ldap
			And success notification is logged in system
			And success notification is displayed

	Scenario: change a user status to inactive
		Given a RAC admin user is logged in
			And a given user exists
			And the user status is active
		When RAC admin user marks a user as inactive
		Then user status is designated as inactive in system
			And success notification is logged in system
			And success notification is displayed

	Scenario: change an organization status to inactive
		Given a RAC admin user is logged in
			And a given organization exists
			And the organization status is active
		When RAC admin user marks an organization as inactive
		Then organization status is designated as inactive in system
			And success notification is logged in system
			And success notification is displayed

	Scenario: manage the status of a user in an organization marked as inactive
		Given a user status is active
			And a user has been added to an organization
			And user has not been added to another organization with an active status
		When RAC admin user marks a user's organization as inactive
		Then user is designated as inactive in system
			And success notification is logged in system
			And success notification is displayed

## Feature: user login results

	Scenario: RAC admin user logs in
		Given a user status is active
			And user has been added to the RAC admin organization
		When RAC admin user enters a valid email address and password
		Then RAC admin user can access Organization Admin UI
			And RAC admin user can access User Admin UI
			And RAC admin user can access Transfer Log, Detail View, and Error Message UIs for all organizations
			And login action is logged in system

	Scenario: non-admin user logs in
		Given a user status is active
			And user has been added to an organization
		When non-admin user logs in with a valid email address and password
		Then non-admin user can access Transfer Log, Detail View, and Error Message UIs for their organization
			And non-admin user can initiate transfers
			And login action is logged in system

	Scenario: a user who has not been added to an organization attempts to log in
		Given a user status is active
			And user has not been added to an organization
		When user enters a valid email address and password
		Then system rejects the login attempt
			And error notification is displayed

	Scenario: an inactive user attempts to login
		Given a user status is inactive
		When user enters a valid email address and password
		Then system rejects the login attempt
		 	And error notification is displayed

	Scenario: a user attempts to login with invalid email address
		Given a user status is active
			And user has been added to an organization
		When user enters an invalid email address
		Then system rejects the login attempt
			And error notification is displayed

	Scenario: a user attempts to login with invalid password
	  Given a user status in active
		  And user has been added to an organization
	  When user enters an invalid password
	  Then system rejects the login attempt
		  And error notification is displayed
