# This script executes system commands to set up Linux groups and users needed
# by Aurora. It should be used when you have User and Organization objects in
# the Aurora database which need to be linked to a new system, such as the
# process of migrating to a new server.

# This script should be run from the Django shell.

from bag_transfer.lib import RAC_CMD
from bag_transfer.models import Organization, User

for org in Organization.objects.all():
    RAC_CMD.add_org(org.machine_name)

for usr in User.objects.all():
    RAC_CMD.add_user(usr.username)
    RAC_CMD.add2grp(usr.organization.machine_name, usr.username)
