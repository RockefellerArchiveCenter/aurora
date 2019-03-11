---
layout: docs
title:  "Aurora - Administration Features"
---

Aurora provides the ability to manage organizations and users accounts with those organizations.

## Organizations

Organizations can be created or deleted by archivists with the necessary permissions. In addition, Aurora allows for the management of the BagIt Profile and PREMIS Rights Statements associated with the organizations.


### BagIt Profiles

[BagIt Profiles](https://github.com/bagit-profiles/bagit-profiles) allow for detailed validation of metadata elements included in a transfer. Aurora allows archivists to create, edit, delete and view these profiles, and provides a JSON representation of the Profile against which transfers can be validated. Each organization can only have one BagIt Profile.

### PREMIS Rights

[PREMIS Rights Statements](https://www.loc.gov/standards/premis/understanding-premis.pdf) allow archivists to specify, in a machine-actionable way, what can and cannot be done with digital records based on the donor agreements. Aurora allows archivists to create, edit and delete one or more PREMIS Rights Statements, and associate them with record types. Record types are specified in the organization's BagIt Profile.

For details on PREMIS and the RAC's local implementation, see the [Rockefeller Archive Center PREMIS Rights Statements Guidelines](http://docs.rockarch.org/premis-rights-guidelines/).

## Users

Aurora supports management of user accounts, and allows archivists with appropriate permissions to add users, declare user accounts active or inactive, associate them with an organization, and assign them to groups (to specify their roles and permissions).

### User roles and permissions

Aurora implements the following user roles and associated permissions:

#### Read Only User

All users (including those form donor organizations) have a few basic permissions:

*  View dashboard for own organization
*  View all own organization transfers
*  View all own transfers
*  View own organization profile
*  View rights statements for own organization
*  View BagIt Profile for own organization
*  View own user profile
*  Change own password

#### Archivist Users

In addition to the permissions for **All Users**, users who are archivists have the following additional permissions:

##### All Archivists
*  View all dashboards
*  View all transfers
*  View all organizations
*  View all organization profiles
*  View all rights statements
*  View all BagIt Profiles
*  View appraisal queue
*  View accessioning queue

##### Appraisal Archivist

In addition to the permissions of **All Archivists**, Appraisal Archivists have the following additional permissions:

*  Accept or reject transfers
*  Add appraisal notes to transfers

##### Accessioning Archivist

In addition to the permissions of **All Archivists**, Accessioning Archivists have the following additional permissions:

*  Create accession records

##### Managing Archivist

In addition to the permissions of **All Archivists**, Managing Archivists have the following additional permissions:

*  Accept or reject transfers
*  Add appraisal notes to transfers
*  Create accession records
*  Add/edit organizations
*  Add/edit users
*  Add/edit rights statements
*  Add/edit Bag-It Profiles

##### System Administrator

In addition to the permissions of **All Archivists**, System Administrators have the following additional permissions:

*  Accept or reject transfers
*  Add appraisal notes to transfers
*  Create accession records
*  Add/edit organizations
*  Add/edit users
*  Add/edit rights statements
*  Add/edit Bag-It Profiles
*  Change system settings
