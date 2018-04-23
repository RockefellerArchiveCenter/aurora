import pwd
import os
from orgs.lib.files_helper import chown_path_to_root

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from orgs.models import Organization

from orgs.transfer_app.RAC_CMD import delete_system_group

@receiver(pre_delete, sender=Organization)
def delete_organization(sender,instance,**kwargs):

	# update group of upload path to root
	chown_path_to_root(instance.org_machine_upload_paths()[0])

	# remove system group
	delete_system_group(instance.machine_name)
