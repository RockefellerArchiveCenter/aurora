from django.conf import settings
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver

from bag_transfer.accession.models import Accession
from bag_transfer.lib.files_helper import chown_path_to_root
from bag_transfer.lib.RAC_CMD import delete_system_group
from bag_transfer.models import Organization, Transfer, User


@receiver(pre_delete, sender=Organization)
def delete_organization(sender, instance, **kwargs):
    """Clean up system resources when an organization is deleted."""
    if settings.S3_USE:
        instance.deactivate_iam_user(instance.machine_name)
    else:
        chown_path_to_root(instance.upload_target)
        delete_system_group(instance.machine_name)


@receiver(m2m_changed, sender=User.groups.through)
def set_is_staff(sender, instance, **kwargs):
    """Ensure `is_staff` attribute is correctly set when User instances are saved."""
    is_staff_user = (
        (any(name in ["managing_archivists", "accessioning_archivists", "appraisal_archivists"]
             for name in instance.groups.values_list("name", flat=True)) or (instance.is_superuser)))
    instance.is_staff = is_staff_user
    instance.save()


@receiver(post_save, sender=Transfer)
def update_accession_status(sender, instance, **kwargs):
    """
    Updates Accession status to COMPLETE if all of the transfers in an accession
    have finished processing.
    """
    if instance.process_status == Transfer.ACCESSIONING_COMPLETE:
        accession = instance.accession
        last_update = sorted(
            set([t.process_status for t in accession.accession_transfers.all()]))[0]
        if last_update == Transfer.ACCESSIONING_COMPLETE:
            accession.process_status = Accession.COMPLETE
            accession.save()
