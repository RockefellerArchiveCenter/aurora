# project_electron_transfer

Full documentation available [here](https://github.com/RockefellerArchiveCenter/project_electron_transfer/blob/scripts/scripts/Rockefeller%20Archive%20Center%20Bash%20Scripts%20Documentation.pdf) (PDF)

### upload.sh

Script to identify new file uploads, which runs every 30 minutes (Bash)

### RACaddorg

This script will create the new organization on the server (Bash)

### RACcreateuser.c

Creates administrative user (c program)

### RACadd2grp

This script will add a user to the group that is representing the organization. (Bash)

### RACdeluser

This script will remove a user from the server. The user will remain in LDAP. (Bash)
## Installation

1.  Install requirements in `requirements.txt`
2.  Rename `project_electron/config.py.example` to `project_electron/config.py` and update settings as necessary
3.  Run `python project_electron/manage.py migrate`
4.  For a local development server run `python project_electron/manage.py runserver`
