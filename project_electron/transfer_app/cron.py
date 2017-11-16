import datetime

from django_cron import CronJobBase, Schedule

from transfer_app.lib import files_helper as FH
from transfer_app.lib.bag_checker import bagChecker

from orgs.models import Archives, Organization, User, BAGLog, ProcessingStatus
from transfer_app.lib.mailer import Mailer

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'transfer_app.my_cron_job'    # a unique code

    def do(self):

        print '############################'
        print 'CRON START'
        print datetime.datetime.now()
        print '############################\n'
        BAGLog.log_it('CSTR')

        to_process = FH.has_files_to_process()
        if (to_process):

            for upload_list in to_process:

                ## FILE ALREADY IN ARCHIVE / FIRST to prevent other processing
                new_arc = Archives()
                machine_file_identifier = new_arc.gen_identifier(
                    upload_list['file_name'],upload_list['org'], upload_list['date'], upload_list['time']
                )
                archive_exist = Archives.objects.filter(machine_file_identifier = machine_file_identifier)
                if archive_exist:
                    print 'shouldnt overwrite file, need to make sure this file doesnt get discovered again'
                    continue

                # Init Mailer
                email = Mailer()

                new_arc.process_status = ProcessingStatus.objects.get(status_short=10)

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
                new_arc.organization =          org
                new_arc.user_uploaded =         user
                new_arc.machine_file_path =     upload_list['file_path']
                new_arc.machine_file_size =     upload_list['file_size']
                new_arc.machine_file_upload_time =  upload_list['file_modtime']
                new_arc.machine_file_identifier =   machine_file_identifier
                new_arc.machine_file_type       =   upload_list['file_type']
                new_arc.bag_it_name =               upload_list['bag_it_name']

                new_arc.process_status = ProcessingStatus.objects.get(status_short=20)
                new_arc.save()

                ## EMAIL: Receipt of transfer
                # email.setup_message('TRANS_RECEIPT')
                # email.send()


                print 'archive saved'
                BAGLog.log_it('ASAVE', new_arc)

                if upload_list['auto_fail']:
                    new_arc.process_status = ProcessingStatus.objects.get(status_short=30)
                    BAGLog.log_it(upload_list['auto_fail_code'], new_arc)
                    email.setup_message('TRANS_FAIL_VAL',new_arc)
                    email.send()

                else:

                    ## NOW FOR BAG CHECK
                    bag = bagChecker(new_arc)
                    if bag.bag_passed_all():
                        new_arc.process_status = ProcessingStatus.objects.get(status_short=40)
                        new_arc.bag_it_valid = True
                        BAGLog.log_it('APASS',new_arc)
                        email.setup_message('TRANS_PASS_ALL',new_arc)
                        email.send()
                    else:
                        new_arc.process_status = ProcessingStatus.objects.get(status_short=30)
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
