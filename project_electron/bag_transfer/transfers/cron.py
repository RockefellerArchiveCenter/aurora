import datetime

from django_cron import CronJobBase, Schedule

from bag_transfer.lib import files_helper as FH
from bag_transfer.lib.transfer_routine import *
from bag_transfer.lib.bag_checker import bagChecker

from bag_transfer.models import Archives, Organization, User, BAGLog
from bag_transfer.lib.mailer import Mailer

import bag_transfer.lib.log_print as Pter

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'transfers.my_cron_job'    # a unique code

    def do(self):
        Pter.cron_open()
        BAGLog.log_it('CSTR')

        transferRoutine = TransferRoutine(1)
        to_process = transferRoutine.transfers
        if (to_process):

            for upload_list in to_process:


                # Init Mailer
                email = Mailer()

                # Create a unique HASH
                machine_file_identifier = Archives().gen_identifier(
                    upload_list['file_name'],upload_list['org'],upload_list['date'],upload_list['time']
                )
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
                    else:
                        new_arc.process_status = 30
                        BAGLog.log_it(bag.ecode, new_arc)
                        email.setup_message('TRANS_FAIL_VAL',new_arc)
                        email.send()

                new_arc.save()


                ## CLEAN UP
                # TMP DIR
                FH.remove_file_or_dir('/data/tmp/{}'.format(new_arc.bag_it_name))
                ## ORIG PATH
                FH.remove_file_or_dir(new_arc.machine_file_path)

        print '############################'
        print 'CRON END'
        print datetime.datetime.now()
        print '############################'
        print '\n\n\n'
        BAGLog.log_it('CEND')
