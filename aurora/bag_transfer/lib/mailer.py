from django.core.mail import EmailMessage
from django.conf import settings as CF

class Mailer():
    def __init__(self,subject ='',to=[],text_content=''):
        self.subject = subject
        self.from_email= CF.EMAIL_HOST_USER
        self.to= to
        self.text_content = text_content

        self.email = {}

    def send(self):
        if not self.subject or not self.from_email or not self.to or not self.text_content:
            print 'All Fields required werent present'
            return False

        send_to = self.to
        if CF.EMAIL_OVERRIDE and CF.EMAIL_OVERRIDE_USERS:

            self.text_content = "TEST EMAIL: SHOULD BE SENT TO {}\r\n\r\n{}".format(",".join(self.to), self.text_content)
            send_to = CF.EMAIL_OVERRIDE_USERS

        self.email = EmailMessage(
            self.subject,
            self.text_content,
            self.from_email,
            send_to,
            reply_to = [self.from_email]
        )

        try:
            self.email.send(fail_silently=False)
        except Exception as e:
            print e
            return False
        else:
            return True

    def setup_message(self, mess_code, archive_obj={}):
        if mess_code == 'TRANS_RECEIPT':
            self.subject = 'Your transfer reciept'
            self.text_content = """Your transfer has been recieved, and is being processed.
            """
        elif mess_code == 'TRANS_PASS_ALL':
            self.subject = 'Your transfer passed all validation'

            lcodes = archive_obj.get_bag_validations()

            eparts = [
                'The transfer {} was received at {} and has passed all automated checks:',
                'bag validation\t\t\t{}',
                'bag profile validation\t\t{}',
                'You can review the status of this transfer at any time by logging into {}'
            ]
            self.text_content =  "\r\n".join(eparts).format(
                archive_obj.bag_or_failed_name(),
                archive_obj.machine_file_upload_time,
                (lcodes['PBAG'] if lcodes else '--'),
                (lcodes['PBAGP'] if lcodes else '--'),
                CF.BASE_URL + 'app'
                   
            )
        elif mess_code == 'TRANS_FAIL_VAL':
            self.subject = 'Your Transfer Failed Validation'



            eparts = [
                'An error occurred for the transfer {} during {} at {}. The transfer has been deleted from our systems.',
                'Please review the complete error log at {}, correct any errors, and try sending the transfer again.'
            ]

            error_obj = archive_obj.get_bag_failure(LAST_ONLY=True)


            self.text_content = "\r\n\r\n".join(eparts).format(
                archive_obj.bag_or_failed_name(),
                (error_obj.code.code_desc if error_obj else '--'),
                (error_obj.created_time if error_obj else '--'),
                CF.BASE_URL + 'app/transfers/'
            )

            #additional errs
            additional_errors = archive_obj.get_additional_errors()
            if additional_errors:
                self.text_content += '\r\n\r\nAdditional Error Information:\r\n\r\n'
                for err in additional_errors:
                    self.text_content += '{}\r\n\r\n'.format(err)


