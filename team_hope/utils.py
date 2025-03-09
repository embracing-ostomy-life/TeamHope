import logging
from datetime import datetime, date

import sendgrid
from django.core.mail import send_mail, EmailMultiAlternatives

from .mailchimp_contact_manager import MailchimpContactManager
from .models import UserProfile, UserIdentityInfo

# Create a logger
logger = logging.getLogger(__name__)  # resolves to team_hope.utils

COMETCHAT_ADMINS = [
    "patti@embracingostomylife.org",
    "margaret@embracingostomylife.org"
]


def user_profile_is_complete(user):
    profile = UserProfile.objects.filter(user=user).first()
    if not profile:
        return False

    # Example: Assuming 'country' and 'registered' are required for a complete profile
    if not profile.country or not profile.registration_complete:
        return False

    # Assuming 'date_of_birth' is required and needs to be validated
    identity_info = UserIdentityInfo.objects.filter(user=user).first()
    if identity_info and identity_info.date_of_birth:
        if not validate_age(identity_info.date_of_birth.year):
            return False

    return True


def send_team_hope_welcome_email(user, custom_message=None):
    try:
        default_message = (
            f"Welcome, {user.first_name}!\n\n"
            "Thank you for registering with Team Hope. We are excited to have you on board!"
        )

        message = custom_message if custom_message else default_message

        send_mail(
            "Welcome to Team Hope!",
            message,
            "Team Hope <contact@embracingostomylife.org>",
            [user.email],
            fail_silently=False,
        )

    except Exception as e:
        logging.error(f"Failed  sending email to {user.email}: {e}")


def send_aliveandkicking_welcome_email(user, custom_message=None):
    try:
        default_message = (
            f"Welcome, {user.first_name}!\n\n"
            "Thank you for registering with Alive & Kicking. We are excited to have you on board!"
        )

        message = custom_message if custom_message else default_message

        send_mail(
            "Welcome to Alive & Kicking!",
            message,
            "Alive & Kicking <contact@embracingostomylife.org>",
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        logging.error(f"Failed  sending email to {user.email}: {e}")


def send_embracingostomylife_welcome_email(user, custom_message=None):
    try:
        # Default message if no custom message is provided
        default_message = (
            f"Welcome, {user.first_name}!\n\n"
            "Thank you for registering with Embracing Ostomy Life. We are excited to have you on board!"
        )

        message = custom_message if custom_message else default_message

        send_mail(
            "Welcome to Embracing Ostomy Life!",
            message,
            "Embracing Ostomy Life <contact@embracingostomylife.org>",
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        logging.error(f"Failed  sending email to {user.email}: {e}")


def sendgrid_unsubscribe_user(email):
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    response = sg.client.asm.suppressions.delete(request_body={"emails": [email]})
    return response.status_code == 204  # Check if the unsubscription was successful


def validate_age(birth_year):
    current_year = datetime.now().year
    age = current_year - birth_year
    return age >= 18


from django.conf import settings


def send_team_hope_welcome_email_html(user, custom_message=None):
    try:
        # Default message if no custom message is provided
        default_message = (
            f"Welcome, {user.first_name}!\n\n"
            "Thank you for registering with Team Hope. We are excited to have you on board!"
        )

        message = custom_message if custom_message else default_message

        # Create the HTML content using the create_email_content function
        html_content = create_email_content("Welcome to Team Hope!", message)

        # Set up the email
        email = EmailMultiAlternatives(
            subject="Welcome to Team Hope!",
            body=message,  # Fallback for plain text
            from_email="Team Hope <contact@embracingostomylife.org>",
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")  # Attach the HTML version

        # Send the email
        email.send(fail_silently=False)
    except Exception as e:
        logging.error(f"Failed  sending email to {user.email}: {e}")


def send_cometchat_admins_new_person_alert_email(user_profile, custom_message=None):
    """
    Once a user has completed the team hope docusing, an email is sent out to the
    cometchat admins.
     ["patti@embracingostomylife.org - Patti McCord","margaret@embracingostomylife.org - Margaret Cypher"]

    Args:
        user_profile (UserProfile): the user profile object
        custom_message (str): A message to include in the email

    Returns:
        None
    """
    msg = f"""
        A new user ({user_profile.user.first_name},{user_profile.user.last_name})
        has signed up for Team HOPE and completed the Docusign. They are ready to be matched in CometChat.
    """
    subject = "New User Signup for Team HOPE"
    try:
        return send_mail(
            subject=subject,
            message=msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=COMETCHAT_ADMINS,
            fail_silently=False,
        )
    except Exception as e:
        logging.error(f"Failed  sending email to {COMETCHAT_ADMINS}:FROM {settings.DEFAULT_FROM_EMAIL}  Because: {e}")
        return False


def add_to_aliveandkicking_journey(user, userprofile):
    print(type(user))
    first_name = user.first_name
    last_name = user.last_name
    email = user.email
    surgery_type = userprofile.surgery_type

    if userprofile.surgery_date and userprofile.surgery_date < date.today():
        surgery_date = date.today().strftime("%m/%d/%Y")
    else:
        surgery_date = (
            userprofile.surgery_date.strftime("%m/%d/%Y")
            if userprofile.surgery_date
            else ""
        )

    mailchimp = MailchimpContactManager()
    response = mailchimp.add_contact(
        first_name=first_name,
        last_name=last_name,
        email=email,
        surgery_date=surgery_date,
        surgery_type=surgery_type,
    )


def add_to_teamhope_journey(user, userprofile):
    first_name = user.first_name
    last_name = user.last_name
    email = user.email

    mailchimp = MailchimpContactManager()
    response = mailchimp.add_contact(
        first_name=first_name,
        last_name=last_name,
        email=email,
        team_hope_member_role=userprofile.teamhope_member_role,
    )


def send_aliveandkicking_welcome_email_html(user, custom_message=None):
    try:
        # Default message if no custom message is provided
        default_message = (
            f"Welcome, {user.first_name}!\n\n"
            "Thank you for registering with Alive & Kicking. We are excited to have you on board!"
        )

        message = custom_message if custom_message else default_message

        # Create the HTML content using the create_email_content function
        html_content = create_email_content("Welcome to Alive & Kicking!", message)

        # Set up the email
        email = EmailMultiAlternatives(
            subject="Welcome to Alive & Kicking!",
            body=message,  # Fallback for plain text
            from_email="Alive & Kicking <contact@embracingostomylife.org>",
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")  # Attach the HTML version

        # Send the email
        email.send(fail_silently=False)
    except Exception as e:
        logging.error(f"Failed  sending email to {user.email}: {e}")


def send_embracingostomylife_welcome_email_html(user, custom_message=None):
    try:
        # Default message if no custom message is provided
        default_message = (
            f"Welcome, {user.first_name}!<br<br>"
            "Thank you for registering with Embracing Ostomy Life. <br<br>We are excited to have you on board!"
        )

        message = custom_message if custom_message else default_message

        # Create the HTML content using the create_email_content function
        html_content = create_email_content(
            "Welcome to Embracing Ostomy Life!", message
        )

        # Set up the email
        email = EmailMultiAlternatives(
            subject="Welcome to Embracing Ostomy Life!",
            body=message,  # Fallback for plain text
            from_email="Embracing Ostomy Life <contact@embracingostomylife.org>",
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")  # Attach the HTML version

        # Send the email
        email.send(fail_silently=False)
    except Exception as e:
        logging.error(f"Failed  sending email to {user.email}: {e}")


def create_email_content(title, message_content):
    """
    Generates the HTML content for an email.

    :param title: The title or heading of the email.
    :param message_content: The main content or body of the email.
    :return: A string containing the HTML content of the email.
    """

    # HTML email template
    email_content = f"""
    <html>
    <body id="body" class="es-wrapper-color">
    <table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0">
        <tbody>
        <tr>
            <td class="esd-email-paddings" valign="top">
                <table cellpadding="0" cellspacing="0" class="es-content esd-header-popover" align="center">
                    <tbody>
                    <tr>
                        <td class="esd-stripe" align="center" bgcolor="#ffffff" style="background-color: #ffffff;">
                            <table bgcolor="#ffffff" class="es-content-body" align="center" cellpadding="0" cellspacing="0" width="600">
                                <tbody>
                                <tr>
                                    <td class="esd-structure" align="left">
                                        <table cellpadding="0" cellspacing="0" width="100%">
                                            <tbody>
                                            <tr>
                                                <td width="600" class="esd-container-frame" align="center" valign="top" esd-custom-block-id="452">
                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                        <tbody>
                                                        <tr>
                                                            <td align="center" class="esd-block-image logo" style="padding:20px 10px 20px 10px;font-size: 0px;">
                                                                <a target="_blank" href="https://embracingostomylife.org/">
                                                                    <img class="adapt-img" src="https://webdevcloud.cc/newsletter/assets/logo.jpg" alt="Embracing Ostomy Life" style="display: block;" width="350" title="Embracing Ostomy Life">
                                                                </a>
                                                            </td>
                                                        </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                    </tbody>
                </table>
                <table cellpadding="0" cellspacing="0" class="es-content esd-footer-popover" align="center">
                    <tbody>
                    <tr>
                        <td class="esd-stripe" align="center">
                            <table bgcolor="#ffffff" class="es-content-body" align="center" cellpadding="0" cellspacing="0" width="600">
                                <tbody>
                                <tr>
                                    <td class="esd-structure" align="left">
                                        <table class="bg-image" style="background-image: url('https://webdevcloud.cc/newsletter/assets/bg-wave-top.png'); background-size: 600px 490px; background-repeat: no-repeat; background-position: top; height: 490px;" cellpadding="0" cellspacing="0" width="100%">
                                            <tbody>
                                            <tr>
                                                <td class="esd-container-frame" align="center" valign="middle" style="height: 490px; display: table-cell; vertical-align: middle; padding: 20px;">
                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                        <tbody>
                                                        <tr>
                                                            <td align="center" class="esd-block-text-h1">
                                                                <h1 style="font-family:'CircularStd-Bold',sans-serif;font-size:40px;line-height:50px;color:#282828;font-weight:700">
                                                                     {title}
                                                                </h1>
                                                                <p style="font-family:'CircularStd-Book',sans-serif;font-size:16px;line-height:24px;color:#282828;font-weight:bold; margin: 20px 0;">
                                                                    {message_content}
                                                                </p>
                                                            </td>
                                                        </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </td>
        </tr>
        </tbody>
    </table>
    </body>
    </html>
    """

    return email_content
