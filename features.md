---
layout: docs
title:  "Rockefeller Archive Center - Aurora Features"
---

## Dashboard

The homepage of Aurora provides a dashboard

## Transfers

Aurora provides a searchable, sortable table to view all transfers and information about them. A button allows the download of a CSV file containing the data from the transfer table. Users can view the status of each transfer, which is updated as it moves through the process. There are 9 possible statuses:

1. Transfer Started
2. Transfer Complete
3. Invalid
4. Validated
5. Rejected
6. Accepted
7. Accessioning Started
8. In Accession Queue
9. Accession Complete

### Transfer details

Aurora allows users to view more details by clicking on a row for a particular transfer on the table. Details provide, as applicable:
- Error messages
- Metadata associated with the digital records
- Manifest
- Log
- Rights statements associated with transfer
- Appraisal note

## Appraise

The application allows archivists to review a queue of the valid transfers to ensure they are relevant to the collecting scope before accessioning. The upfront validation provided by Aurora (particularly the BagIt Profile validation) should prevent most out-of-scope records from being received, but this step allows a manual check by users with the appropriate permissions (see Users section) who will:

1. View transfer details
2. Add an appraisal note (optional)
3. Accept or reject transfers

## Accession

Once transfers have been accepted in the appraisal queue, they are moved to the accessioning queue, where multiple transfers can be grouped together into a single accession if they have the same organization, record creators and record type. Archivists with the necessary permissions can create accession records, which represent data about one or (usually) more transfers.


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


## Developer Resources
