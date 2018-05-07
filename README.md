# Aurora

Aurora is a Django web application that can receive, virus check and validate transfers of digital archival records, and allows archivists to appraise and accession those records.

The name of the application is a reference both to the natural light display often seen in the northern hemisphere - sometimes referred to as _aurora borealis_ - as well as the Roman goddess of dawn.


## Installation

1.  Install requirements in `requirements.txt` by running `pip install -r requirements.txt`.
2.  Rename `aurora/config.py.example` to `aurora/config.py` and update settings as necessary.
3.  Run `python aurora/manage.py migrate`.
4.  For a local development server run `python aurora/manage.py runserver`.

Application functionality currently assumes a SLES server and a specific LDAP configuration. Future development will include improving the portability of the application through containerization.


## Transferring digital records

Aurora scans subdirectories at the location specified by the `TRANSFER_UPLOADS_ROOT` setting. It expects each organization to have its own directory, containing three subdirectories: `uploads`, `processing` and `logs`. Any new files or directories in the `uploads` subdirectory are submitted Aurora's queue for processing.

At a high level, transfers are processed as follows:
- Transfers are checked to ensure they have a valid filename, in other words that the top-level directory (for unserialized bags) or filename (for serialized bags) does not contain illegal characters.
- Transfers are checked for viruses.
- Transfers are checked to ensure they have only one top-level directory.
- Size of transfers is checked to ensure it doesn't exceed `TRANSFER_FILESIZE_MAX`.
- Transfers are validated against the BagIt specification using `bagit-python`.
- Transfers are validated against the BagIt Profile specified in their `bag-info.txt` file using `bagit-profiles-validator`.
- Relevant PREMIS rights statements are assigned to transfers (see Organization Management section for details).


## Appraising Digital Records

Although the upfront validation provided by Aurora (particularly the BagIt Profile validation) should prevent many out-of-scope records from being accessioned, Aurora also allows archivists to review a queue of valid transfers to ensure they are relevant to collecting scope. Users with the appropriate permissions (see User Management section) can accept or reject transfers, and optionally can add an appraisal note.


## Accessioning Digital Records

Once transfers have been accepted, they are moved to the accessioning queue, where they are grouped by organization, record creators and record type. Archivists with the necessary permissions can create accession records, which represent data about one or (usually) more transfers.


## Organization Management

Organizations can be created or deleted by archivists with the necessary permissions (see User Management section). In addition, Aurora allows for the management of two additional types of objects associated with organizations.

### BagIt Profiles

[BagIt Profiles](https://github.com/bagit-profiles/bagit-profiles) allow for detailed validation of metadata elements included in a transfer. Aurora allows archivists to create, edit and delete these profiles, and provides a JSON representation of the Profile against which transfers can be validated. Each organization can only have one BagIt Profile.

### PREMIS Rights Statements

[PREMIS Rights Statements](https://www.loc.gov/standards/premis/understanding-premis.pdf) allow archivists to specify, in a machine-actionable way, what can and cannot be done with digital records. Aurora allows archivists to create, edit and delete one or more PREMIS Rights Statements, and associate them with record types.


## User Management

Aurora supports management of user accounts, and allows certain archivists to declare user accounts active or inactive, associate them with an organization, and assign groups to them.

### User groups and permissions

Aurora implements the following user groups and associated permissions:

#### All Users

All users have a few basic permissions:

*  View all own organization transfers
*  View all own transfers
*  View dashboard for own organization
*  View rights statements for own organization
*  View BagIt Profile for own organization
*  View own organization profile
*  View own profile
*  Change own password

#### Archivist Users

In addition to the permissions for **All Users**, users who are archivists have the following additional permissions:

##### All Archivists
*  View all transfers
*  View all organizations
*  View all organization profiles
*  View all rights statements
*  View all BagIt Profiles
*  View appraisal queue
*  View accessioning queue

##### Appraisal Archivists

In addition to the permissions of **All Archivists**, Appraisal Archivists have the following additional permissions:

*  Accept or reject transfers
*  Add appraisal notes to transfers

##### Accessioning Archivists

In addition to the permissions of **All Archivists**, Accessioning Archivists have the following additional permissions:

*  Create accession records

##### Managing Archivists

In addition to the permissions of **All Archivists**, Managing Archivists have the following additional permissions:

*  Accept or reject transfers
*  Add appraisal notes to transfers
*  Create accession records
*  Add/edit organizations
*  Add/edit users
*  Add/edit rights statements
*  Add/edit bag profiles

##### System Administrator

In addition to the permissions of **All Archivists**, System Administrators have the following additional permissions:

*  Accept or reject transfers
*  Add appraisal notes to transfers
*  Create accession records
*  Add/edit organizations
*  Add/edit users
*  Add/edit rights statements
*  Add/edit bag profiles
*  Change system settings

## API

Aurora comes with a RESTful API, built using the Django Rest Framework. In addition to interacting with the API via your favorite command-line client, you can also use the browsable API interface available in the application.

### Authentication

Aurora uses JSON Web Tokens for validation. As with all token-based authentication, you should ensure the application is only available over SSL/TLS in order to avoid token tampering and replay attacks.

To get your token, send a POST request to the `/get-token/` endpoint, passing your username and password:

      $ curl -X POST -d "username=admin&password=password123" http://localhost:8000/api/get-token/

Your token will be returned in the response. You can then use the token in requests such as:

      $ curl -H "Authorization: JWT <your_token>" http://localhost:8000/api/orgs/1/


## Scripts

Aurora uses several shell scripts to interact with LDAP for authentication purposes. Brief descriptions are provided below, and full documentation is available [here](https://github.com/RockefellerArchiveCenter/aurora/blob/master/scripts/Rockefeller%20Archive%20Center%20Bash%20Scripts%20Documentation.pdf) (PDF).

-   **upload.sh**: identifies new uploads, can be configured to run as a cron job on your desired interval. (Bash)
-   **RACaddorg**: creates a new organization on the server (Bash)
-   **RACcreateuser.c**: creates an administrative user (c program)
-   **RACadd2grp**: adds a user to the group that represents the organization. (Bash)
-   **RACdeluser**: removes a user from the server. The user will remain in LDAP. (Bash)

## License

Aurora is released under an [MIT License](LICENSE).
