import datetime
from os import listdir, mkdir
from os.path import join
import requests
import subprocess

from django.urls import reverse
from django_cron import CronJobBase, Schedule

from aurora import settings
from bag_transfer.api.serializers import ArchivesSerializer
from bag_transfer.lib import files_helper as FH
from bag_transfer.lib.transfer_routine import *
from bag_transfer.lib.bag_checker import bagChecker
import bag_transfer.lib.log_print as Pter
from bag_transfer.models import Archives, Organization, User, BAGLog
from bag_transfer.lib.mailer import Mailer


class DiscoverTransfers(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'transfers.discover_transfers'

    def do(self):
        Pter.cron_open(self.code)
        BAGLog.log_it('CSTR')

        transferRoutine = TransferRoutine(1)
        to_process = transferRoutine.transfers
        if (to_process):

            for upload_list in to_process:


                # Init Mailer
                email = Mailer()

                # Create a unique HASH
                machine_file_identifier = Archives().gen_identifier()
                if not machine_file_identifier:
                    print 'shouldnt overwrite file, need to make sure this file doesnt get discovered again'
                    continue

                ## IS ORG AND IS ACTIVE ORG
                org = Organization().is_org_active(upload_list['org'])
                if not org:
                    org = None

                ## IS USER / IN ORG / AND ACITVE
                user = User().is_user_active(upload_list['upload_user'],org)
                if not user:
                    user = None
                else:
                    email.to = [user.email]
                    print user.email

                ## Init / Save
                new_arc = Archives.initial_save(
                    org,
                    user,
                    upload_list['file_path'],
                    upload_list['file_size'],
                    upload_list['file_modtime'],
                    machine_file_identifier,
                    upload_list['file_type'],
                    upload_list['bag_it_name']
                )

                print 'archive saved'
                BAGLog.log_it('ASAVE', new_arc)

                if upload_list['auto_fail']:
                    new_arc.setup_save(upload_list)
                    new_arc.process_status = 30
                    BAGLog.log_it(upload_list['auto_fail_code'], new_arc)
                    email.setup_message('TRANS_FAIL_VAL',new_arc)
                    email.send()

                else:

                    ## NOW FOR BAG CHECK
                    bag = bagChecker(new_arc)
                    if bag.bag_passed_all():
                        new_arc.process_status = 40
                        new_arc.bag_it_valid = True
                        BAGLog.log_it('APASS',new_arc)
                        email.setup_message('TRANS_PASS_ALL',new_arc)
                        email.send()
                        # Move bag to storage
                        # Should bags be stored in org directories for security purposes?
                        FH.move_file_or_dir('/data/tmp/{}'.format(new_arc.bag_it_name), '{}{}'.format(settings.STORAGE_ROOT_DIR, new_arc.machine_file_identifier))
                        FH.remove_file_or_dir(new_arc.machine_file_path)
                        new_arc.machine_file_path = '{}{}'.format(settings.STORAGE_ROOT_DIR, new_arc.machine_file_identifier)
                    else:
                        new_arc.process_status = 30
                        BAGLog.log_it(bag.ecode, new_arc)
                        email.setup_message('TRANS_FAIL_VAL',new_arc)
                        email.send()
                        # Delete file
                        FH.remove_file_or_dir(new_arc.machine_file_path)

                new_arc.save()

                # Delete tmp files
                FH.remove_file_or_dir('/data/tmp/{}'.format(new_arc.bag_it_name))

        Pter.cron_close(self.code)


class DeliverTransfers(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'transfers.deliver_transfers'

    def do(self):
        Pter.cron_open(self.code)
        for archive in Archives.objects.filter(process_status=75):
            tar_filename = "{}.tar.gz".format(archive.machine_file_identifier)
            FH.make_tarfile(
                join(settings.STORAGE_ROOT_DIR, tar_filename),
                join(settings.STORAGE_ROOT_DIR, archive.machine_file_identifier))

            mkdir(join(settings.DELIVERY_QUEUE_DIR, archive.machine_file_identifier))

            FH.move_file_or_dir(
                join(settings.STORAGE_ROOT_DIR, tar_filename),
                join(settings.DELIVERY_QUEUE_DIR, archive.machine_file_identifier, tar_filename))

            object = Archives.objects.get(machine_file_identifier=transfer)
            object_json = requests.get(reverse('transfers:detail', pk=object.pk))
            print object_json
            with open(join(transfer, "{}.json".format(archive.machine_file_identifier)), 'w') as f:
                f.write(object_json)

            FH.make_tarfile(
                join(settings.DELIVERY_QUEUE_DIR, "{}.tar.gz".format(archive.machine_file_identifier)),
                join(settings.DELIVERY_QUEUE_DIR, archive.machine_file_identifier))

            FH.remove_file_or_dir(join(settings.DELIVERY_QUEUE_DIR, archive.machine_file_identifier))

            # move it?
            rsynccmd = "rsync -avh --remove-source-files {} {}@{}:{}".format(join(settings.DELIVERY_QUEUE_DIR, transfer),
                                                                             settings.DELIVERY['user'],
                                                                             settings.DELIVERY['host'],
                                                                             settings.DELIVERY['dir'])
            print(rsynccmd)
            rsyncproc = subprocess.Popen(rsynccmd,
                                         shell=True,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,)
            while True:
                next_line = rsyncproc.stdout.readline().decode("utf-8")
                if not next_line:
                    break
                print(next_line)

            ecode = rsyncproc.wait()
            if ecode != 0:
                continue

            archive.process_status = 80
            archive.save()

        Pter.cron_close(self.code)
