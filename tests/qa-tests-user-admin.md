# Project Electron Transfer QA Tests for User Admin

These tests are written in [Gherkin](https://github.com/cucumber/cucumber/wiki/Gherkin), a structured language that can be used for both documentation and automated testing of software.

## Feature: create user and organization accounts

	Scenario: Create a new user
		Given a RAC admin user is logged in
			And a valid email address is provided
			And a valid password is provided
			And a first name is provided
			And a last name is provided
		When user information is entered
		Then user information is assigned an LDAP user id
			And user information is added to LDAP
			And user id is added to transfer app
			And success notification is logged in transfer app
			And success notification is displayed
			And email notification is sent to new user with link to reset password

	Scenario: Create a new organization
		Given a RAC admin user is logged in
			And a valid organization email address is provided
			And an organization name is provided
			And an organization description is provided
			And the organization name does not already exist
		When organization information is entered
		Then organization information is assigned to an LDAP group id
			And directories are created for the organization
			And organization information is added to LDAP
			And organization id is added to transfer app
			And organization status is marked as active
			And success notification is logged in transfer app
			And success notification is displayed

## Feature: manage accounts

	Scenario: add a user to an organization
		Given a RAC admin user is logged in
			And a specified user exists
			And a specified organization exists
			And a specified organization status is active
		When RAC admin user adds user to organization
		Then organization assignment is applied in LDAP
			And success notification is logged in transfer app
			And success notification is displayed

	Scenario: change a user password
		Given a user is logged in with valid email_1 and password_1
		When a user changes password_1 to password_2
		Then user can log in with the email_1 and password_2
			And user can no longer log in with email_1 and password_1
			And password change is applied in LDAP
			And success notification is logged in transfer app
			And success notification is displayed

	Scenario: reset a user password
		Given a user enters a valid email address
		When a user selects to reset password
		Then an email notification is sent to user with a link to reset password
		When user follows email link to reset password
			And user enters a new password
		Then success notification is displayed
			And user is logged in to account
			And password change is applied in LDAP
			And success notification is logged in transfer app

	Scenario: change a user status to inactive
		Given a RAC admin user is logged in
			And a given user exists
			And the user status is active
		When RAC admin user marks a user as inactive
		Then user status is designated as inactive in transfer app
			And success notification is logged in transfer app
			And success notification is displayed

	Scenario: change an organization status to inactive
		Given a RAC admin user is logged in
			And a given organization exists
			And the organization status is active
		When RAC admin user marks an organization as inactive
		Then organization status is designated as inactive in transfer app
			And users that have been added to organization are designated as inactive in transfer app
			And success notification is logged in transfer app
			And success notification is displayed

## Feature: user login results

	Scenario: RAC admin user logs in
		Given a user status is active
			And user has been added to the RAC admin organization
		When RAC admin user enters a valid email address and password
		Then RAC admin user can access Organization Admin UI
			And RAC admin user can access User Admin UI
			And RAC admin user can access Transfer Log, Detail View, and Error Message UIs for all organizations
			And login action is logged in transfer app

	Scenario: non-admin user logs in
		Given a user status is active
			And user has been added to an organization
		When non-admin user logs in with a valid email address and password
		Then non-admin user can access Transfer Log, Detail View, and Error Message UIs for their organization
			And non-admin user can initiate transfers
			And login action is logged in transfer app

	Scenario: a user who has not been added to an organization attempts to log in
		Given a user status is active
			And user has not been added to an organization
		When user enters a valid email address and password
		Then transfer app rejects the login attempt
			And error notification is displayed

	Scenario: an inactive user attempts to login
		Given a user status is inactive
		When user enters a valid email address and password
		Then transfer app rejects the login attempt
		 	And error notification is displayed

	Scenario: a user attempts to login with invalid email address
		Given a user status is active
			And user has been added to an organization
		When user enters an invalid email address
		Then transfer app rejects the login attempt
			And error notification is displayed

	Scenario: a user attempts to login with invalid password
		Given a user status in active
			And user has been added to an organization
		When user enters an invalid password
		Then transfer app rejects the login attempt
			And error notification is displayed
