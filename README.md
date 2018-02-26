# Aurora

Aurora is a Django web application that can receive, virus check and validate transfers of digital archival records, and allows archivists to appraise and accession those records.

## Installation

1.  Install requirements in `requirements.txt`
2.  Rename `project_electron/config.py.example` to `project_electron/config.py` and update settings as necessary
3.  Run `python project_electron/manage.py migrate`
4.  For a local development server run `python project_electron/manage.py runserver`

Application functionality currently assumes a SLES server and a particular LDAP configuration. Future development will include improving the portability of the application.

## User groups and permissions

Aurora implements the following user groups and associated permissions:

### All Users

All users have a few basic permissions:

*  View all own organization transfers
*  View all own transfers
*  View dashboard for own organization
*  View rights statements for own organization
*  View BagIt Profile for own organization
*  View own organization profile
*  View own profile
*  Change own password

### Archivist Users

In addition to the permissions for **All Users**, users who are archivists have the following additional permissions:

#### All Archivists
*  View all transfers
*  View all organizations
*  View all organization profiles
*  View all rights statements
*  View all BagIt Profiles
*  View appraisal queue
*  View accessioning queue

#### Appraisal Archivists

In addition to the permissions of **All Archivists**, Appraisal Archivists have the following additional permissions:

*  Accept or reject transfers
*  Add appraisal notes to transfers

#### Accessioning Archivists

In addition to the permissions of **All Archivists**, Accessioning Archivists have the following additional permissions:

*  Create accession records

#### Managing Archivists

In addition to the permissions of **All Archivists**, Managing Archivists have the following additional permissions:

*  Accept or reject transfers
*  Add appraisal notes to transfers
*  Create accession records
*  Add/edit organizations
*  Add/edit users
*  Add/edit rights statements
*  Add/edit bag profiles

#### System Administrator

In addition to the permissions of **All Archivists**, System Administrators have the following additional permissions:

*  Accept or reject transfers
*  Add appraisal notes to transfers
*  Create accession records
*  Add/edit organizations
*  Add/edit users
*  Add/edit rights statements
*  Add/edit bag profiles
*  Change system settings

## Scripts

Aurora uses several shell scripts to interact with LDAP for authentication purposes. Brief descriptions are provided below, and full documentation is available [here](https://github.com/RockefellerArchiveCenter/project_electron_transfer/blob/scripts/scripts/Rockefeller%20Archive%20Center%20Bash%20Scripts%20Documentation.pdf) (PDF).

-   **upload.sh**: identifies new uploads, can be configured to run as a cron job on your desired interval. (Bash)
-   **RACaddorg**: creates a new organization on the server (Bash)
-   **RACcreateuser.c**: creates an administrative user (c program)
-   **RACadd2grp**: adds a user to the group that represents the organization. (Bash)
-   **RACdeluser**: removes a user from the server. The user will remain in LDAP. (Bash)

## License

Aurora is released under an [MIT License](LICENSE).

## Why Aurora?

The name of the application is a reference both to the natural light display often seen in the northern hemisphere - sometimes referred to as _aurora borealis_ - as well as the Roman goddess of dawn. In both cases, the name evokes motion and beauty.
