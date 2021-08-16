import json
from os import mkdir
from os.path import isdir, join

import bag_transfer.lib.log_print as Pter
from asterism.bagit_helpers import update_bag_info
from asterism.file_helpers import (make_tarfile, move_file_or_dir,
                                   remove_file_or_dir)
from aurora import settings
from bag_transfer.api.serializers import TransferSerializer
from bag_transfer.lib.bag_checker import BagChecker
from bag_transfer.lib.mailer import Mailer
from bag_transfer.lib.transfer_routine import TransferRoutine
from bag_transfer.models import BAGLog, Organization, Transfer, User
from django_cron import CronJobBase, Schedule


class DiscoverTransfers(CronJobBase):
    RUN_EVERY_MINS = 0

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "transfers.discover_transfers"

    def do(self):
        result = True
        Pter.cron_open(self.code)
        BAGLog.log_it("CSTR")

        transferRoutine = TransferRoutine(1)
        to_process = transferRoutine.transfers
        if to_process:

            for upload_list in to_process:
                try:
                    email = Mailer()

                    machine_file_identifier = Transfer().gen_identifier()
                    org = Organization.is_org_active(upload_list["org"])
                    user = User.is_user_active(upload_list["upload_user"], org)

                    email.to = [user.email]

                    new_transfer = Transfer.objects.create(
                        organization=org,
                        user_uploaded=user,
                        machine_file_path=upload_list["file_path"],
                        machine_file_size=upload_list["file_size"],
                        machine_file_upload_time=upload_list["file_modtime"],
                        machine_file_identifier=machine_file_identifier,
                        machine_file_type=upload_list["file_type"],
                        bag_it_name=upload_list["bag_it_name"],
                        process_status=Transfer.TRANSFER_COMPLETED)

                    BAGLog.log_it("ASAVE", new_transfer)
                    print("\nValidating transfer {}".format(new_transfer.machine_file_identifier))

                    if upload_list["auto_fail"]:
                        new_transfer.add_autofail_information(upload_list)
                        new_transfer.process_status = Transfer.INVALID
                        BAGLog.log_it(upload_list["auto_fail_code"], new_transfer)
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
                            move_file_or_dir(
                                join(settings.TRANSFER_EXTRACT_TMP, new_transfer.bag_it_name),
                                "{}{}".format(
                                    settings.STORAGE_ROOT_DIR,
                                    new_transfer.machine_file_identifier,
                                ),
                            )
                            remove_file_or_dir(new_transfer.machine_file_path)
                            new_transfer.machine_file_path = "{}{}".format(
                                settings.STORAGE_ROOT_DIR, new_transfer.machine_file_identifier
                            )
                        else:
                            print("Transfer {} is invalid".format(new_transfer.machine_file_identifier))
                            new_transfer.process_status = Transfer.INVALID
                            BAGLog.log_it(bag.ecode, new_transfer)
                            email.setup_message("TRANS_FAIL_VAL", new_transfer)
                            email.send()
                            remove_file_or_dir(new_transfer.machine_file_path)

                    new_transfer.save()
                    remove_file_or_dir(join(settings.TRANSFER_EXTRACT_TMP, new_transfer.bag_it_name))
                except Exception as e:
                    print("Error discovering transfer {}: {}".format(machine_file_identifier, str(e)))
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
        for transfer in Transfer.objects.filter(process_status=Transfer.ACCESSIONING_STARTED):
            try:
                update_bag_info(
                    join(settings.STORAGE_ROOT_DIR, transfer.machine_file_identifier),
                    {"Origin": "aurora"})
                tar_filename = "{}.tar.gz".format(transfer.machine_file_identifier)
                make_tarfile(
                    join(settings.STORAGE_ROOT_DIR, transfer.machine_file_identifier),
                    join(settings.STORAGE_ROOT_DIR, tar_filename))

                mkdir(join(settings.DELIVERY_QUEUE_DIR, transfer.machine_file_identifier))

                move_file_or_dir(
                    join(settings.STORAGE_ROOT_DIR, tar_filename),
                    join(settings.DELIVERY_QUEUE_DIR, transfer.machine_file_identifier, tar_filename))

                transfer_json = TransferSerializer(transfer, context={"request": None}).data
                with open(join(
                        settings.DELIVERY_QUEUE_DIR,
                        transfer.machine_file_identifier,
                        "{}.json".format(transfer.machine_file_identifier)), "w") as f:
                    json.dump(transfer_json, f, indent=4, sort_keys=True, default=str)

                make_tarfile(
                    join(settings.DELIVERY_QUEUE_DIR, transfer.machine_file_identifier),
                    join(settings.DELIVERY_QUEUE_DIR, "{}.tar.gz".format(transfer.machine_file_identifier)))

                remove_file_or_dir(join(settings.DELIVERY_QUEUE_DIR, transfer.machine_file_identifier))

                transfer.process_status = Transfer.DELIVERED
                print(transfer.machine_file_identifier)
                transfer.save()
            except Exception as e:
                print("Error delivering transfer {}: {}".format(transfer, str(e)))
                result = False

        Pter.cron_close(self.code)
        return result
