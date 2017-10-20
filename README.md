# Aurora

Aurora is a Django web application that can receive, virus check and validate transfers of digital archival records, and allows archivists to appraise and accession those records.

## Installation

1.  Install requirements in `requirements.txt`
2.  Rename `project_electron/config.py.example` to `project_electron/config.py` and update settings as necessary
3.  Run `python project_electron/manage.py migrate`
4.  For a local development server run `python project_electron/manage.py runserver`

Application functionality currently assumes a SLES server and a particular LDAP configuration. Future development will include improving the portability of the application.

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
