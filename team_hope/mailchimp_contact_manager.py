import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from django.conf import settings


class MailchimpContactManager:
    def __init__(self):
        """
        Initialize the MailchimpContactManager.

        :param api_key: Your Mailchimp API key
        :param server_prefix: The prefix of your Mailchimp server (e.g., 'us1', 'us2')
        """
        self.client = MailchimpMarketing.Client()
        self.client.set_config({"api_key": settings.MAILCHIMP_API_KEY})
        self.list_id = settings.MAILCHIMP_LIST_ID

    def add_contact(
        self,
        email,
        first_name=None,
        last_name=None,
        surgery_type=None,
        surgery_date=None,
    ):
        """
        Add a contact to a Mailchimp list.

        :param email: The email address of the contact
        :param first_name: (Optional) First name of the contact
        :param last_name: (Optional) Last name of the contact
        :return: API response or error message
        """
        try:
            # Define the contact data
            member_info = {
                "email_address": email,
                "status": "subscribed",
                "merge_fields": {
                    "FNAME": first_name or "",
                    "LNAME": last_name or "",
                    "SURG_DATE": surgery_date or "",
                    "SURG_TYPE": surgery_type or "",
                },
            }

            # Add contact to the list
            response = self.client.lists.add_list_member(
                list_id=self.list_id, body=member_info
            )
            return response
        except ApiClientError as error:
            return {"error": str(error)}
