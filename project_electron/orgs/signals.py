import pwd
import os

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from orgs.models import Organization

from transfer_app.RAC_CMD import delete_system_group

@receiver(pre_delete, sender=Organization)
def delete_organization(sender,instance,**kwargs):

	# update group of upload path to root
	root_uid = pwd.getpwnam('root').pw_uid
	os.chown(instance.org_machine_upload_paths()[0],root_uid,root_uid)

	# remove system group
	delete_system_group(instance.machine_name)
