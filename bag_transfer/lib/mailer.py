from django.conf import settings as CF
from django.core.mail import EmailMessage
from django.urls import reverse


class Mailer:
    def __init__(self, subject="", to_emails=[], text_content=""):
        self.subject = subject
        self.from_email = CF.EMAIL_HOST_USER
        self.to_emails = to_emails
        self.text_content = text_content
        self.footer = "\r\n".join(
            [
                "Rockefeller Archive Center",
                "15 Dayton Avenue, Sleepy Hollow, NY 10591",
                "(914) 366-6300",
                "archive@rockarch.org",
                "https://rockarch.org",
            ]
        )

    def send(self):
        if not all([self.subject, self.from_email, self.to_emails, self.text_content]):
            raise Exception("Unable to send email. One or more of the following fields were missing: subject, from email, to email or text content.")

        self.text_content += f"\r\n\r\n\r\n{self.footer}"
        email = EmailMessage(
            self.subject,
            self.text_content,
            self.from_email,
            self.to_emails,
            reply_to=[self.from_email],
        )
        email.send(fail_silently=False)

    def setup_message(self, mess_code, transfer={}):
        if mess_code == "TRANS_PASS_ALL":
            self.subject = f"Transfer {transfer.bag_or_failed_name} passed all validation"

            eparts = [
                f"The transfer {transfer.bag_or_failed_name} with the bag name {transfer.bag_it_name} was received at {transfer.machine_file_upload_time} and has passed all automated validation checks:",
                "This transfer is now awaiting archival appraisal and accessioning.",
                f"You can view the current status of this transfer at {CF.BASE_URL + reverse('transfers:detail', kwargs={'pk': transfer.pk})}",
            ]
            self.text_content = "\r\n\r\n".join(eparts)
        elif mess_code == "TRANS_FAIL_VAL":
            error_obj = transfer.last_failure
            self.subject = f"Transfer {transfer.bag_or_failed_name} failed validation"
            eparts = [
                f"An error occurred for the transfer with bag name {transfer.bag_or_failed_name,} during {error_obj.code.code_desc if error_obj else '--'} at {error_obj.created_time if error_obj else '--'}.",
                "The transfer has been deleted from our systems.",
                f"Please review the complete error log at {CF.BASE_URL + reverse('transfers:detail', kwargs={'pk': transfer.pk})}, correct any errors, and try sending the transfer again.",
            ]
            self.text_content = "\r\n\r\n".join(eparts)
            if transfer.additional_errors:
                self.text_content += "\r\n\r\nAdditional Error Information:\r\n\r\n"
                for err in transfer.additional_errors:
                    self.text_content += f"{err}\r\n\r\n"

        elif mess_code == "TRANS_REJECT":
            self.subject = f"Transfer {transfer.bag_or_failed_name} was rejected"

            eparts = [
                f"An appraisal archivist rejected transfer {transfer.bag_or_failed_name}. The transfer has been deleted from our systems."
            ]

            if transfer.appraisal_note:
                eparts.append(
                    f"The reason for this action was: {transfer.appraisal_note}"
                )

            self.text_content = "\r\n\r\n".join(eparts)
