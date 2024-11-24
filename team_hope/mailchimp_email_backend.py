# mailchimp_email_backend.py

from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import mailchimp_transactional as MailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError


class MailchimpEmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = settings.MAILCHIMP_TRANSACTIONAL_API_KEY
        print(self.api_key)
        self.client = MailchimpTransactional.Client(self.api_key)
        self.run()

    def run(self):
        try:
            response = self.client.users.ping()
            print("API called successfully: {}".format(response))
        except ApiClientError as error:
            print("An exception occurred: {}".format(error.text))

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0
        for message in email_messages:
            try:
                response = self.client.messages.send(
                    body={
                        "from_email": message.from_email,
                        "subject": message.subject,
                        "text": message.body,
                        "to": [{"email": addr} for addr in message.to],
                    }
                )
                sent_count += 1
                print(response)
            except ApiClientError as error:
                print(f"An error occurred: {error.text}")

        return sent_count
