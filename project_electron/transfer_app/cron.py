from django_cron import CronJobBase, Schedule

from transfer_app.lib import files_helper as FH
from orgs.models import Archives, Organization, User

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'transfer_app.my_cron_job'    # a unique code

    def do(self):


        to_process = FH.has_files_to_process()
        if (to_process):
            for upload_list in to_process:
                
                ## FILE ALREADY IN ARCHIVE / FIRST to prevent other processing
                new_arc = Archives()
                machine_file_identifier = new_arc.gen_identifier(
                    upload_list['org'], upload_list['date'], upload_list['time']
                )
                archive_exist = Archives.objects.filter(machine_file_identifier = machine_file_identifier)
                if archive_exist:
                    print 'shouldnt overwrite file, need to make sure this file doesnt get discovered again'
                    ### log it
                    continue

                ## IS ORG AND IS ACTIVE ORG
                org = Organization().is_org_active(upload_list['org'])
                if not org: continue

                ## IS USER / IN ORG / AND ACITVE
                user = User().is_user_active(upload_list['upload_user'],org)
                if not user: continue

                ## Init / Save
                new_arc.organization =          org
                new_arc.user_upload =           user
                new_arc.machine_file_path =     upload_list['file_path']
                new_arc.machine_file_size =     upload_list['file_size']
                new_arc.machine_file_upload_time =  upload_list['file_modtime']
                new_arc.machine_file_identifier =   machine_file_identifier

                new_arc.save()
                print 'archive saved'
                ####LOG SAVE


        


