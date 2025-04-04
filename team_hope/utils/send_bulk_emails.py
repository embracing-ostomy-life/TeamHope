import logging

import sendgrid
from django.conf import settings
from django.core.mail import send_mail
from sendgrid.helpers.mail import Mail, Email

logger = logging.getLogger(__name__)  # This will resolve to team_hope.utils.send_bulk_emails


def send_bulk_emails_with_sendgrid(recipients: list, subject: str = None):
    """
    Send bulk personalized emails with sendgrid
    Args:
        recipients(list): list of name,email key-value pairs
        subject(str): The subject of the email

    Returns:
        bool: True if successful, False otherwise
    """
    from_email = Email("patti@embracingostomylife.org")  # settings.DEFAULT_FROM_EMAIL
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    if not recipients:
        return False
    subject = "You've Got a New Message on Team HOPE" if not subject else subject
    mail = Mail()
    mail.from_email = from_email
    mail.template_id = "d-b99b39db665241b5a7a525eef50bc7af"
    mail.subject = subject
    # mail.content = "text/plain"
    recipients = [{"name": "Kalenshi Katebe", "email": "kalenshi@gmail.com"}]
    # Add recipients
    body = "You've Got a New Message on Team HOPE"
    for recipient in recipients:
        send_mail(
            subject,
            body,
            "no-reply@yourdomain.com",
            recipient["email"],
            fail_silently=False,
        )
   
        # personalization = Personalization()
        # personalization.add_to(To(recipient["email"], recipient["name"]))
        # personalization.dynamic_template_data = {
        #     "name": recipient["name"],
        # }
        # mail.add_personalization(personalization)

    # # send the email
    # try:
    #     response = sg.client.mail.send.post(request_body=mail.get())
    #     print("**************************++++++++++++++++++++++++++++++++++++++++++")
    #     print(response)
    #     print("**************************++++++++++++++++++++++++++++++++++++++++++")
    #     return response
    # except Exception as e:
    #     logger.error(f"Failed to send bulk emails: {e.__dict__}")
    #     return False
