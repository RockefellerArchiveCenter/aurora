from __future__ import division
from datetime import date
from dateutil.relativedelta import relativedelta
import pwd
import os

from bag_transfer.lib.files_helper import chown_path_to_root

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from bag_transfer.models import Archives, BagInfoMetadata, Organization, DashboardMonthData, DashboardRecordTypeData

from bag_transfer.lib.RAC_CMD import delete_system_group


@receiver(pre_delete, sender=Organization)
def delete_organization(sender, instance, **kwargs):

    # update group of upload path to root
    chown_path_to_root(instance.org_machine_upload_paths()[0])

    # remove system group
    delete_system_group(instance.machine_name)


@receiver(post_save, sender=Archives)
def update_dashboard_data(sender, instance, **kwargs):
    today = date.today()
    current = today - relativedelta(years=1)
    if instance.process_status == sender.TRANSFER_COMPLETED:
        while current <= today:
            for organization in Organization.objects.all():
                data = DashboardMonthData.objects.get_or_create(
                    month_label=current.strftime("%B"),
                    sort_date=int(str(current.year) + str(current.month)),
                    year=current.year,
                    organization=organization
                )[0]
                data.upload_count = Archives.objects.filter(
                    organization=organization,
                    machine_file_upload_time__year=current.year,
                    machine_file_upload_time__month=current.month).count()
                data.upload_size = sum(map(int, Archives.objects.filter(
                    organization=organization,
                    machine_file_upload_time__year=current.year,
                    machine_file_upload_time__month=current.month).values_list('machine_file_size', flat=True)))/1000000000
                data.save()
            current += relativedelta(months=1)
    elif instance.process_status == sender.VALIDATED:
        for organization in Organization.objects.all():
            for label in set(BagInfoMetadata.objects.all().values_list('record_type', flat=True)):
                data = DashboardRecordTypeData.objects.get_or_create(
                    organization=organization,
                    label=label
                )[0]
                data.count = Archives.objects.filter(organization=organization, metadata__record_type=label).count()
                data.save()
