from django.core.mail import send_mail
import sendgrid
from sendgrid.helpers.mail import Mail
from django.conf import settings
from datetime import datetime
from .models import UserProfile, UserIdentityInfo

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

def send_team_hope_welcome_email(user):
    try:
        send_mail(
            'Welcome to Team Hope!',
            'Thank you for registering with Team Hope. We are excited to have you on board!',
            'Team Hope <contact@embracingostomylife.org>',  
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")

def send_aliveandkicking_welcome_email(user):
    try:
        send_mail(
            'Welcome to Alive & Kicking!',
            'Thank you for registering with Alive & Kicking. We are excited to have you on board!',
            'Alive & Kicking <contact@embracingostomylife.org>',  
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")


def send_embracingostomylife_welcome_email(user):
    try:
        send_mail(
            'Welcome to Embracing Ostomy Life!',
            'Thank you for registering with Embracing Ostomy Life. We are excited to have you on board!',
            'Embracing Ostomy Life <contact@embracingostomylife.org>',  
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")


def sendgrid_unsubscribe_user(email):
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    response = sg.client.asm.suppressions.delete(request_body={'emails': [email]})
    return response.status_code == 204  # Check if the unsubscription was successful



def validate_age(birth_year):
    current_year = datetime.now().year
    age = current_year - birth_year
    return age >= 18


import requests
from django.conf import settings

# def sendgrid_unsubscribe_user(email):
#     headers = {
#         'Authorization': f'Bearer {settings.SENDGRID_API_KEY}',
#         'Content-Type': 'application/json'
#     }

#     data = {
#         "recipient_emails": [email]
#     }

#     response = requests.post(
#         'https://api.sendgrid.com/v3/asm/suppressions/global',
#         headers=headers,
#         json=data
#     )

#     return response.status_code == 201  # Return True if the unsubscribe was successful
