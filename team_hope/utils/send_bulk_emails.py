import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)  # This will resolve to team_hope.utils.send_bulk_emails


# def send_bulk_emails_with_sendgrid(recipients: list, subject: str = None):
#     """
#     Send bulk personalized emails with sendgrid
#     Args:
#         recipients(list): list of name,email key-value pairs
#         subject(str): The subject of the email
#
#     Returns:
#         bool: True if successful, False otherwise
#     """
#     from_email = Email("patti@embracingostomylife.org")  # settings.DEFAULT_FROM_EMAIL
#     sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
#     if not recipients:
#         return False
#     subject = "You've Got a New Message on Team HOPE" if not subject else subject
#     mail = Mail()
#     mail.from_email = from_email
#     mail.template_id = "d-b99b39db665241b5a7a525eef50bc7af"
#     mail.subject = subject
#     # mail.content = "text/plain"
#     recipients = [{"name": "Kalenshi Katebe", "email": "kalenshi@gmail.com"}]
#     # Add recipients
#     body = "You've Got a New Message on Team HOPE"
#     for recipient in recipients:
#         send_mail(
#             subject,
#             body,
#             "no-reply@yourdomain.com",
#             recipient["email"],
#             fail_silently=False,
#         )
#
#         personalization = Personalization()
#         personalization.add_to(To(recipient["email"], recipient["name"]))
#         personalization.dynamic_template_data = {
#             "name": recipient["name"],
#         }
#         mail.add_personalization(personalization)
#
#     # send the email
#     try:
#         response = sg.client.mail.send.post(request_body=mail.get())
#         print("**************************++++++++++++++++++++++++++++++++++++++++++")
#         print(response)
#         print("**************************++++++++++++++++++++++++++++++++++++++++++")
#         return response
#     except Exception as e:
#         logger.error(f"Failed to send bulk emails: {e.__dict__}")
#         return False


def notify_users_of_chat(recipients: list, subject=None):
    """
   Once a group participant sends a message in the group, the other participants of the group
   should get an email notification of this.

    Args:
        subject (str):
        recipients: list of name,email key-value pairs

    Returns:
        None
    Raises:
        Exception : Whenever sending the email fails
    """
    subject = "You've Got a New Message on Team HOPE" if subject is None else subject

    try:
        for recipient in recipients:
            context = {
                "email": recipient["email"],
                "name": recipient["name"],
                "link": "https://app.embracingostomylife.org/chat"
            }
            html_message = render_to_string(
                "email_templates/chat_notification.html", context
            )
            plain_msg = strip_tags(html_message)
            logger.debug("----------------------------------------------------------------")
            logger.debug(f"sending email to : {recipient['email']}")
            logger.debug("----------------------------------------------------------------")
            email = EmailMultiAlternatives(
                subject,
                plain_msg,
                settings.DEFAULT_FROM_EMAIL,
                [recipient["email"]],
            )
            email.attach_alternative(html_message, "text/html")
            sent = email.send()
            logger.debug(f"sent email to : {recipient['email']} with response: {sent}")
    except Exception as e:
        logging.error(f"Failed  sending email to {recipients}:FROM {settings.DEFAULT_FROM_EMAIL}  Because: {e}")
        return False
