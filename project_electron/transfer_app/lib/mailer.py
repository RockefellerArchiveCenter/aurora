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


        if CF.EMAIL_OVERRIDE and CF.EMAIL_OVERRIDE_USERS:

            self.text_content = "TEST EMAIL: SHOULD BE SENT TO {}\r\n{}".format(",".join(self.to), self.text_content)
            self.to = CF.EMAIL_OVERRIDE_USERS

        self.email = EmailMessage(
            self.subject,
            self.text_content,
            self.from_email,
            self.to,
            reply_to = [self.from_email]
        )

        try:
            self.email.send(fail_silently=False)
        except Exception as e:
            print e
            return False
        else:
            return True

    def setup_message(self, mess_code):
        if mess_code == 'TRANS_RECEIPT':
            self.subject = 'Your transfer reciept'
            self.text_content = """
                Your transfer has been recieved, and is being processed.
            """
        elif mess_code == 'TRANS_PASS_ALL':
            self.subject = 'Your transfer passed all validation'
            self.text_content = self.subject
        elif mess_code == 'TRANS_FAIL_VAL':
            self.subject = 'Your Transfer Failed Validation'
            self.text_content = self.subject


