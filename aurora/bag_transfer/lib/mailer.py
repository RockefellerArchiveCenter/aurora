from django.core.mail import EmailMessage
from django.conf import settings as CF
from django.urls import reverse


class Mailer():
    def __init__(self, subject='', to=[], text_content=''):
        self.subject = subject
        self.from_email = CF.EMAIL_HOST_USER
        self.to = to
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

        footer = "\r\n".join(["Rockefeller Archive Center",
                              "15 Dayton Avenue, Sleepy Hollow, NY 10591",
                              "(914) 366-6300", "archive@rockarch.org",
                              "https://rockarch.org"])

        self.content += "\r\n\r\n\r\n{}".format(footer)

        self.email = EmailMessage(
            self.subject,
            self.text_content,
            self.from_email,
            send_to,
            reply_to=[self.from_email]
        )

        try:
            self.email.send(fail_silently=False)
        except Exception as e:
            print e
            return False
        else:
            return True

    def setup_message(self, mess_code, archive_obj={}):
        if mess_code == 'TRANS_PASS_ALL':
            self.subject = 'Transfer {} passed all validation'.format(archive_obj.bag_or_failed_name())

            lcodes = archive_obj.get_bag_validations()

            eparts = [
                'The transfer {} was received at {} and has passed all automated validation checks:',
                'You can view the current status of this transfer at {}'
            ]
            self.text_content = "\r\n\r\n".join(eparts).format(
                archive_obj.bag_or_failed_name(),
                archive_obj.machine_file_upload_time,
                CF.BASE_URL + reverse('transfers:detail', kwargs={'pk': archive_obj.pk})
            )
        elif mess_code == 'TRANS_FAIL_VAL':
            self.subject = 'Transfer {} failed validation'.format(archive_obj.bag_or_failed_name())

            eparts = [
                'An error occurred for the transfer {} during {} at {}. The transfer has been deleted from our systems.',
                'Please review the complete error log at {}, correct any errors, and try sending the transfer again.'
            ]

            error_obj = archive_obj.get_bag_failure(LAST_ONLY=True)

            self.text_content = "\r\n\r\n".join(eparts).format(
                archive_obj.bag_or_failed_name(),
                (error_obj.code.code_desc if error_obj else '--'),
                (error_obj.created_time if error_obj else '--'),
                CF.BASE_URL + reverse('transfers:detail', kwargs={'pk': archive_obj.pk})
            )

            # additional errs
            additional_errors = archive_obj.get_additional_errors()
            if additional_errors:
                self.text_content += '\r\n\r\nAdditional Error Information:\r\n\r\n'
                for err in additional_errors:
                    self.text_content += '{}\r\n\r\n'.format(err)

        elif mess_code == 'TRANS_REJECT':
            self.subject = 'Transfer {} was rejected'.format(archive_obj.bag_or_failed_name())

            eparts = [
                'An appraisal archivist rejected transfer {}. The transfer has been deleted from our systems.'.format(archive_obj.bag_or_failed_name())
            ]

            if archive_obj.appraisal_note:
                eparts.append('The reason for this action was: {}'.format(archive_obj.appraisal_note))

            self.text_content = "\r\n\r\n".join(eparts)
