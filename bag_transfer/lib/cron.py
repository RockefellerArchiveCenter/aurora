import json
from os import mkdir
from os.path import isdir, join

import boto3
from asterism.bagit_helpers import update_bag_info
from asterism.file_helpers import (make_tarfile, move_file_or_dir,
                                   remove_file_or_dir)
from django.conf import settings
from django_cron import CronJobBase, Schedule

import bag_transfer.lib.log_print as Pter
from bag_transfer.api.serializers import TransferSerializer
from bag_transfer.lib.bag_checker import BagChecker
from bag_transfer.lib.mailer import Mailer
from bag_transfer.lib.transfer_routine import TransferRoutine
from bag_transfer.models import BAGLog, Organization, Transfer


class DiscoverTransfers(CronJobBase):
    RUN_EVERY_MINS = 0

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "transfers.discover_transfers"

    def do(self):
        result = True
        Pter.cron_open(self.code)
        BAGLog.log_it("CSTR")

        to_process = TransferRoutine().run_routine()

        for transfer_dict in to_process:
            try:
                email = Mailer()

                org = Organization.is_org_active(transfer_dict["org"])

                email.to = [u.email for u in org.admin_users]

                new_transfer = Transfer.objects.create(
                    organization=org,
                    machine_file_path=transfer_dict["machine_file_path"],
                    machine_file_size=transfer_dict["machine_file_size"],
                    machine_file_upload_time=transfer_dict["machine_file_upload_time"],
                    machine_file_identifier=transfer_dict["machine_file_identifier"],
                    machine_file_type=transfer_dict["machine_file_type"],
                    bag_it_name=transfer_dict["bag_it_name"],
                    process_status=Transfer.TRANSFER_COMPLETED)

                BAGLog.log_it("ASAVE", new_transfer)
                print("\nValidating transfer {}".format(new_transfer.machine_file_identifier))

                if transfer_dict["auto_fail"]:
                    new_transfer.add_autofail_information(transfer_dict)
                    new_transfer.process_status = Transfer.INVALID
                    BAGLog.log_it(transfer_dict["auto_fail_code"], new_transfer)
                    email.setup_message("TRANS_FAIL_VAL", new_transfer)
                    email.send()
                    remove_file_or_dir(new_transfer.machine_file_path)

                else:
                    bag = BagChecker(new_transfer)
                    if bag.bag_passed_all():
                        print("Transfer {} is valid".format(new_transfer.machine_file_identifier))
                        new_transfer.process_status = Transfer.VALIDATED
                        new_transfer.bag_it_valid = True
                        BAGLog.log_it("APASS", new_transfer)
                        email.setup_message("TRANS_PASS_ALL", new_transfer)
                        email.send()
                        update_bag_info(new_transfer.machine_file_path, {"Origin": "aurora"})
                        tar_filename = "{}.tar.gz".format(new_transfer.machine_file_identifier)
                        make_tarfile(
                            new_transfer.machine_file_path,
                            join(settings.TRANSFER_EXTRACT_TMP, tar_filename))
                        if settings.S3_USE:
                            s3_client = boto3.client(
                                's3',
                                aws_access_key_id=settings.S3_ACCESS_KEY,
                                aws_secret_access_key=settings.S3_SECRET_KEY,
                                region_name=settings.S3_REGION)
                            s3_client.upload_file(
                                join(settings.TRANSFER_EXTRACT_TMP, tar_filename),
                                settings.STORAGE_BUCKET,
                                tar_filename)
                            new_transfer.machine_file_path = tar_filename
                        else:
                            move_file_or_dir(
                                join(settings.TRANSFER_EXTRACT_TMP, tar_filename),
                                join(settings.STORAGE_ROOT_DIR, tar_filename))
                            new_transfer.machine_file_path = join(settings.STORAGE_ROOT_DIR, tar_filename)

                        remove_file_or_dir(join(settings.TRANSFER_EXTRACT_TMP, tar_filename))
                    else:
                        print("Transfer {} is invalid".format(new_transfer.machine_file_identifier))
                        new_transfer.process_status = Transfer.INVALID
                        BAGLog.log_it(bag.ecode, new_transfer)
                        email.setup_message("TRANS_FAIL_VAL", new_transfer)
                        email.send()
                        remove_file_or_dir(new_transfer.machine_file_path)

                try:
                    new_transfer.save()
                except Exception as e:
                    print("Error saving new transfer {}: {}".format(new_transfer.machine_file_identifier, str(e)))
                    result = False
                    remove_file_or_dir(join(settings.TRANSFER_EXTRACT_TMP, new_transfer.machine_file_identifier))
            except Exception as e:
                print("Error discovering transfer {}: {}".format(transfer_dict["machine_file_identifier"], str(e)))
                result = False
        Pter.cron_close(self.code)
        return result


class DeliverTransfers(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "transfers.deliver_transfers"

    def do(self):
        result = True
        Pter.cron_open(self.code)
        if not isdir(settings.DELIVERY_QUEUE_DIR):
            mkdir(settings.DELIVERY_QUEUE_DIR)
        transfer = Transfer.objects.filter(process_status=Transfer.ACCESSIONING_STARTED).first()
        if transfer:
            try:
                target_dir = join(settings.DELIVERY_QUEUE_DIR, transfer.machine_file_identifier)
                mkdir(target_dir)
                tar_filename = "{}.tar.gz".format(transfer.machine_file_identifier)
                if settings.S3_USE:
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=settings.S3_ACCESS_KEY,
                        aws_secret_access_key=settings.S3_SECRET_KEY,
                        region_name=settings.S3_REGION)
                    s3_client.download_file(
                        settings.STORAGE_BUCKET,
                        transfer.machine_file_path,
                        join(target_dir, tar_filename))
                else:
                    move_file_or_dir(
                        join(settings.STORAGE_ROOT_DIR, tar_filename),
                        join(target_dir, tar_filename))

                transfer_json = TransferSerializer(transfer, context={"request": None}).data
                with open(join(target_dir, "{}.json".format(transfer.machine_file_identifier)), "w") as f:
                    json.dump(transfer_json, f, indent=4, sort_keys=True, default=str)

                make_tarfile(target_dir, join(settings.DELIVERY_QUEUE_DIR, tar_filename))

                remove_file_or_dir(target_dir)

                transfer.process_status = Transfer.DELIVERED
                print(transfer.machine_file_identifier)
                transfer.save()
            except Exception as e:
                print("Error delivering transfer {}: {}".format(transfer, str(e)))
                result = False

        Pter.cron_close(self.code)
        return result
