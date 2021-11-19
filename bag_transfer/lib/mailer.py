from django.conf import settings as CF
from django.core.mail import EmailMessage
from django.urls import reverse


class Mailer:
    def __init__(self, subject="", to=[], text_content=""):
        self.subject = subject
        self.from_email = CF.EMAIL_HOST_USER
        self.to = to
        self.text_content = text_content

        self.email = {}

    def send(self):
        if (
            not self.subject or not self.from_email or not self.to or not self.text_content
        ):
            print("All Fields required werent present")
            return False

        send_to = self.to

        footer = "\r\n".join(
            [
                "Rockefeller Archive Center",
                "15 Dayton Avenue, Sleepy Hollow, NY 10591",
                "(914) 366-6300",
                "archive@rockarch.org",
                "https://rockarch.org",
            ]
        )

        self.text_content += "\r\n\r\n\r\n{}".format(footer)

        self.email = EmailMessage(
            self.subject,
            self.text_content,
            self.from_email,
            send_to,
            reply_to=[self.from_email],
        )

        try:
            self.email.send(fail_silently=False)
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def setup_message(self, mess_code, transfer={}):
        if mess_code == "TRANS_PASS_ALL":
            self.subject = "Transfer {} passed all validation".format(
                transfer.bag_or_failed_name
            )

            eparts = [
                "The transfer {} with the bag name {} was received at {} and has passed all automated validation checks:",
                "This transfer is now awaiting archival appraisal and accessioning.",
                "You can view the current status of this transfer at {}",
            ]
            self.text_content = "\r\n\r\n".join(eparts).format(
                transfer.bag_or_failed_name,
                transfer.bag_it_name,
                transfer.machine_file_upload_time,
                CF.BASE_URL + reverse("transfers:detail", kwargs={"pk": transfer.pk}),
            )
        elif mess_code == "TRANS_FAIL_VAL":
            self.subject = "Transfer {} failed validation".format(
                transfer.bag_or_failed_name
            )

            eparts = [
                "An error occurred for the transfer with bag name {} during {} at {}.",
                "The transfer has been deleted from our systems.",
                "Please review the complete error log at {}, correct any errors, and try sending the transfer again.",
            ]

            error_obj = transfer.last_failure

            self.text_content = "\r\n\r\n".join(eparts).format(
                transfer.bag_or_failed_name,
                (error_obj.code.code_desc if error_obj else "--"),
                (error_obj.created_time if error_obj else "--"),
                CF.BASE_URL + reverse("transfers:detail", kwargs={"pk": transfer.pk}),
            )

            if transfer.additional_errors:
                self.text_content += "\r\n\r\nAdditional Error Information:\r\n\r\n"
                for err in transfer.additional_errors:
                    self.text_content += "{}\r\n\r\n".format(err)

        elif mess_code == "TRANS_REJECT":
            self.subject = "Transfer {} was rejected".format(transfer.bag_or_failed_name)

            eparts = [
                "An appraisal archivist rejected transfer {}. The transfer has been deleted from our systems.".format(
                    transfer.bag_or_failed_name
                )
            ]

            if transfer.appraisal_note:
                eparts.append(
                    "The reason for this action was: {}".format(
                        transfer.appraisal_note
                    )
                )

            self.text_content = "\r\n\r\n".join(eparts)
