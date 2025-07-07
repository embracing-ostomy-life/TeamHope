import base64
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime

import jwt
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import (
    HttpResponse,
    JsonResponse,
    HttpResponseRedirect,
    HttpResponseBadRequest,
    HttpResponseServerError,
)
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from jwt import PyJWKClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from components.cascading_selects.states import state_countries_dict
from team_hope.utils.email_utils import (
    send_cometchat_admins_new_person_alert_email
)
from .cometchat import CCUser
from .forms import (
    RegisterAliveAndKickingForm,
    RegisterForm,
    ProfileForm,
    ProfilePictureForm,
    RegisterTeamHopeForm,
)
from .helpers.docusign_email_sender import DocuSignEmailSender
from .models import (
    UserProfile, UserIdentityInfo, UserType, UserMethodOfCommunication, TeamHopeMemberRoleChoices
)
from .utils.picture_utils import process_profile_picture
from .utils.send_bulk_emails import notify_users_of_chat

# Create a logger
logger = logging.getLogger(__name__)  # The name resolves to team_hope.views

SENDGRID_API_KEY = settings.SENDGRID_API_KEY


def azure_b2c_login(request):
    redirect_uri = request.build_absolute_uri(reverse("team_hope:azure_b2c_callback"))
    return HttpResponseRedirect(
        settings.AZURE_B2C_AUTH_URL.format(redirect_uri=redirect_uri)
    )


def azure_b2c_callback(request):
    next_page = request.session.get("next", "/")
    token = request.GET.get("id_token")
    if not token:
        logger.error("Token with  was not found in the Response")
        return HttpResponse("Token not found in the response", status=400)
    try:
        jwks_url = f"https://{settings.AZURE_B2C_TENANT}.b2clogin.com/{settings.AZURE_B2C_TENANT}.onmicrosoft.com/{settings.AZURE_B2C_POLICY_NAME}/discovery/v2.0/keys"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.AZURE_B2C_CLIENT_ID,
        )
        email = payload.get("emails", [None])[0]
        username = email.split("@")[0] if email else payload.get("name")
        first_name = payload.get("extension_FirstName", "")
        last_name = payload.get("extension_LastName", "")
        guid = payload.get("oid")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            },
        )

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        identity_info, _ = UserIdentityInfo.objects.get_or_create(user=user)
        identity_info.uuid = guid
        identity_info.save()
        logging.debug(f"Identity Info saved with uuid {guid}")

        profile, created = UserProfile.objects.get_or_create(user=user)

        profile.country = payload.get("country", "")
        profile.save()

        if profile.registration_complete:
            ccuser = CCUser(user)
            ccuser.sync()

        login(request, user)
        if not profile.signup_complete:
            return redirect("team_hope:complete-signup")
        return redirect(f"{next_page}")


    except jwt.ExpiredSignatureError:
        logging.error("Token has expired")
        return HttpResponse("Token has expired", status=400)
    except jwt.InvalidTokenError:
        logging.error("Token is invalid")
        return HttpResponse("Invalid token", status=400)
    except UserProfile.DoesNotExist as e:
        logging.error("UserProfile does not exist")
        return HttpResponseServerError(f"{e}")
    except Exception as e:
        logging.error(f"An unexpected error : {e} occurred ")
        return HttpResponseServerError(f"{e}")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileForm
    template_name = "profile/edit_profile.html"
    success_url = "/profile/"

    def get_object(self, queryset=None):
        return self.request.user.userprofile


class ProfilePictureUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfilePictureForm
    template_name = "profile/edit_profile_picture.html"
    success_url = "/profile/"

    def get_object(self, queryset=None):
        return self.request.user.userprofile


class CustomLogoutView(LogoutView):
    template_name = "registration/logged_out.html"


def logout_view(request):
    django_logout(request)  # Clears the session
    logout_url = settings.AZURE_B2C_LOGOUT_URL
    return redirect(logout_url)


def logout_complete_view(request):
    # You can render a custom logout complete template or redirect to the home page
    return render(request, "team_hope/logout_complete.html")


def verify_hmac_signature(secret, payload, signature):
    """
    Verify the HMAC signature of the payload sent by DocuSign.
    """
    key = bytes(secret, "utf-8")
    payload = bytes(payload, "utf-8")
    hmac_hash = hmac.new(key, payload, hashlib.sha256)
    computed_signature = base64.b64encode(hmac_hash.digest()).decode("utf-8")
    return hmac.compare_digest(computed_signature, signature)


@csrf_exempt
def docusign_webhook(request):
    """
    Handle DocuSign Connect webhook POST requests.
    """
    docusign_webhook_secret = settings.DS_CALLBACK_SECRET
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")

    # Retrieve the HMAC signature from the headers
    signature = request.headers.get("X-DocuSign-Signature-1")
    if not signature:
        return HttpResponseBadRequest("Missing HMAC signature")

    # Get the payload from the request body
    try:
        payload = request.body.decode("utf-8")
        payload_data = json.loads(payload)
    except Exception as e:
        logger.warning("Invalid Payload!")
        return HttpResponseBadRequest(f"Invalid payload: {str(e)}")

    # Verify the HMAC signature
    if not verify_hmac_signature(docusign_webhook_secret, payload, signature):
        return HttpResponseBadRequest("Invalid HMAC signature")

    # Process the payload (customize as per your requirements)
    logging.debug(f"Webhook received: {payload_data}", )

    if "data" in payload_data and "envelopeId" in payload_data["data"]:
        # search the user by envelopeId
        try:
            envelope_id = str(payload_data["data"].get("envelopeId"))
            logging.info(f"Finding User with  envelope ID {envelope_id}.")
            profile = UserProfile.objects.filter(
                Q(docusign_aliveandkicking_envelope_id=envelope_id)
                | Q(docusign_teamhope_envelope_id=envelope_id)
            ).first()

            if profile:
                logging.info(f"Found User {profile}")
                if profile.docusign_aliveandkicking_envelope_id == envelope_id:
                    profile.aliveandkicking_waiver_complete = True
                elif profile.docusign_teamhope_envelope_id == envelope_id:
                    profile.team_hope_docusign_complete = True

                    # Only after signing the team hope docusing should the user be added to cometchat
                    try:
                        ccuser = CCUser(profile.user)
                        resp = ccuser.sync()
                        logging.debug(f"CCUser Response: ({resp})")
                        if "createdAt" in resp or "updatedAt" in resp:
                            # The profile is being created or updated
                            # either way, the profile can be marked as complete
                            profile.registration_complete = True
                        if "createdAt" in resp and "updatedAt" not in resp:
                            # Send email to chat admins
                            send_cometchat_admins_new_person_alert_email(profile)

                    except Exception as error:
                        logging.error(f"Failed to sync CometChat user: {error}")

                profile.save()
            else:
                raise UserProfile.DoesNotExist
        except UserProfile.DoesNotExist:
            logging.error(f"No profile found with the specified envelope ID {envelope_id}.")
            return JsonResponse(
                {
                    "message": f"No profile found with the specified envelope ID {envelope_id}"
                },
                status=404,
            )
        except UserProfile.MultipleObjectsReturned:
            logging.warning(f"Unexpected multiple profiles found with the same envelope ID. {envelope_id}")
            return JsonResponse(
                {
                    "message": "Unexpected multiple profiles found with the same envelope ID"
                },
                status=400,
            )
    # Return a success response
    return JsonResponse({"message": "Webhook received successfully"}, status=200)


@login_required
def home(request):
    if not request.user.is_authenticated:
        return redirect("team_hope:azure_b2c_login")

    current_user = request.user
    profile = UserProfile.objects.get(user=current_user)
    is_profile_complete = (
        profile.registration_complete
    )  # user_profile_is_complete(current_user)
    if not profile.signup_complete:
        return redirect("team_hope:complete-signup")
    if request.method == "POST":
        form = RegisterForm(request.POST, instance=current_user.userprofile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.registration_complete = True
            profile.save()
            try:
                ccuser = CCUser(current_user)
                _ = ccuser.sync()
                is_profile_complete = True
            except Exception as error:
                logging.error(f"Failed to sync CometChat user: {error}")
    else:
        form = RegisterForm(instance=current_user.userprofile)

    params = {
        "chat_enabled": is_profile_complete,
        "user_profile_is_complete": is_profile_complete,
        "form": form,
        "team_hope_complete": profile.team_hope_all_complete,  # Using team_hope_all_complete directly from profile
        "alive_and_kicking_subscribed": profile.subscribed_to_aliveandkicking,
        "teamhope_subscribed": profile.subscribed_to_teamhope,
        "a_k_docusign_waiting": (
            True
            if not profile.subscribed_to_aliveandkicking
               and profile.docusign_aliveandkicking_envelope_id
            else False
        ),  # Using subscribed_to_aliveandkicking directly from profile
        "t_h_docusign_waiting": (
            True
            if not profile.subscribed_to_teamhope
               and profile.docusign_teamhope_envelope_id
            else False
        ),  # Using subscribed_to_teamhope directly from profile
    }
    logging.debug(f"Welcome Home {request.user.first_name}: {request.user.email}", )
    return render(request, "team_hope/home.html", params)


def index(request):
    if request.GET.get("next"):
        request.session["next"] = request.GET["next"]
    if request.user.is_authenticated:
        return redirect("team_hope:home")
    return redirect("team_hope:azure_b2c_login")


def user_type(request):
    if not request.user.is_authenticated:
        return redirect("team_hope:home")
    return render(request, "team_hope/registration/user_type.html")


def register_type(request):
    if not request.user.is_authenticated:
        return redirect("team_hope:home")

    current_user = request.user
    profile, created = UserProfile.objects.get_or_create(user=current_user)

    if request.method == "GET":
        utype = request.GET.get("type")
        if utype in [
            UserType.CONSIDERING_SURGERY,
            UserType.OSTOMATE,
            UserType.CAREGIVER,
            UserType.MEDICAL_PROFESSIONAL,
            UserType.SUPPORTER,
        ]:
            profile.user_type = utype
            profile.save()
            return render(request, "team_hope/registration/location.html")

    return render(request, "team_hope/registration/user_type.html")


def register_team_hope(request):
    if not request.user.is_authenticated:
        return redirect("team_hope:azure_b2c_login")

    current_user = request.user
    profile, created = UserProfile.objects.get_or_create(user=current_user)

    if request.method == "POST":
        form = RegisterTeamHopeForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            image_file = form.cleaned_data.get("profile_picture")
            communication_method = form.cleaned_data.pop("communication_method")
            if communication_method:

                try:
                    if len(communication_method) == 1:
                        _, _ = UserMethodOfCommunication.objects.update_or_create(
                            user=current_user,
                            communication_method=communication_method[0]
                        )
                    else:
                        bulk = [
                            UserMethodOfCommunication(
                                user=current_user,
                                communication_method=method
                            )
                            for method in communication_method
                        ]
                        UserMethodOfCommunication.objects.bulk_create(
                            bulk,
                            update_conflicts=True,
                            unique_fields=["user", "communication_method"],
                            update_fields=["communication_method"]
                        )
                    if form.data.get("phone-number"):
                        profile.phone = form.data.get("phone-number")
                except IntegrityError as error:
                    logger.debug(error)
                    logger.debug(f"Communication method: {communication_method} already exists")
                except Exception:
                    logger.debug("Exception occurred: During Communication method creation")
            profile = form.save(commit=False)

            if image_file:
                try:
                    profile.profile_picture = process_profile_picture(image_file)
                except Exception as error:
                    logging.error(f"Failed to process Profile Picture: {error}")
                    profile.profile_picture = None
            profile.team_hope_docusign_complete = False
            profile.team_hope_training_complete = True
            profile.team_hope_all_complete = True
            docusign = DocuSignEmailSender()
            if profile.teamhope_member_role == TeamHopeMemberRoleChoices.PARTICIPANT:
                template_id = settings.DS_TEAM_HOPE_MEMBER_TEMPLATE_ID
            else:
                template_id = settings.DS_TEAM_HOPE_VOLUNTEER_TEMPLATE_ID

            response = docusign.send_email(
                customer_email=current_user.email,
                customer_name=current_user.get_full_name(),
                template_id=template_id,
            )
            profile.docusign_teamhope_envelope_id = response.get("envelope_id", "")
            profile.registration_complete = False
            profile.signup_complete = True
            profile.registered_th = True
            profile.save()
            if not profile.registered_ak:
                msg = ("Looking for more support? "
                       "You can also join the Alive and Kicking program at any time.")
                messages.add_message(request, messages.INFO, msg)
            return redirect("team_hope:home")
        else:
            logging.error(f"Error filling up the form: {form.errors}", )

    else:
        form = RegisterTeamHopeForm(instance=profile)

    return render(request, "team_hope/register_team_hope.html", {"form": form})


def schedule_sendgrid_subscription(email, surgery_date):
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        # Determine the send_at timestamp
        if surgery_date and surgery_date > datetime.now().date():
            send_at = int(
                time.mktime(surgery_date.timetuple())
            )  # Schedule for the surgery date
        else:
            send_at = int(time.time())  # Send immediately

        # Create the email
        message = Mail(
            from_email="rolf@embracingostomylife.org",  # Ensure this email is verified in SendGrid
            to_emails=email,
            subject="Alive & Kicking - Post Surgery Support",
            html_content="<strong>Your post-surgery support emails will start soon.</strong>",
        )

        # Set the send_at parameter for scheduling
        message.send_at = send_at

        # Send the email
        response = sg.send(message)

        return response.status_code in [200, 202]
    except Exception as e:
        logging.error(f"Error in sendgrid subscription schedule: {str(e)}")  # Log the error for debugging
        return False


def register_alive_and_kicking(request):
    if not request.user.is_authenticated:
        return redirect("team_hope:azure_b2c_login")

    current_user = request.user
    profile = UserProfile.objects.get(user=current_user)

    if request.method == "POST":
        form = RegisterAliveAndKickingForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            docusign = DocuSignEmailSender()
            response = docusign.send_email(
                customer_email=current_user.email,
                customer_name=current_user.get_full_name(),
            )
            profile.docusign_aliveandkicking_envelope_id = response.get(
                "envelope_id", ""
            )
            profile.signup_complete = True
            profile.registered_ak = True
            profile.save()
            if not profile.registered_th:
                msg = ("Looking for more support? "
                       "You can also join the Team Hope program"
                       "at any time")
                messages.add_message(request, messages.INFO, msg)
            return redirect("team_hope:home")
    else:
        form = RegisterAliveAndKickingForm(instance=profile)
    return render(request, "team_hope/register_alive_and_kicking.html", {"form": form})


def unsubscribe_alive_and_kicking(request):
    if not request.user.is_authenticated:
        return redirect(azure_b2c_login)

    current_user = request.user
    profile = UserProfile.objects.get(user=current_user)

    if request.method == "POST":
        profile.aliveandkicking_waiver_complete = False
        profile.subscribed_to_aliveandkicking = False
        profile.docusign_aliveandkicking_envelope_id = ""
        profile.save()

        # Unsubscribe the user from the SendGrid list
        success = True  # sendgrid_unsubscribe_user(profile.user.email)
        if success:
            messages.success(
                request, "You have successfully unsubscribed from Alive & Kicking."
            )
        else:
            messages.error(
                request, "There was an issue unsubscribing you. Please try again later."
            )

        return redirect("team_hope:home")

    return render(request, "team_hope/unsubscribe_alive_and_kicking.html")


def unsubscribe_teamhope(request):
    if not request.user.is_authenticated:
        return redirect(azure_b2c_login)

    current_user = request.user
    profile = UserProfile.objects.get(user=current_user)

    if request.method == "POST":
        profile.subscribed_to_teamhope = False
        profile.team_hope_docusign_complete = False
        profile.docusign_teamhope_envelope_id = ""
        profile.save()

        # Unsubscribe the user from the SendGrid list
        success = True  # sendgrid_unsubscribe_user(profile.user.email)
        if success:
            messages.success(
                request, "You have successfully unsubscribed from Team Hope."
            )
        else:
            messages.error(
                request, "There was an issue unsubscribing you. Please try again later."
            )

        return redirect("team_hope:home")

    return render(request, "team_hope/unsubscribe_teamphope.html")


def register_location(request):
    if not request.user.is_authenticated:
        return redirect("team_hope:home")

    current_user = request.user
    profile, created = UserProfile.objects.get_or_create(user=current_user)

    if request.method == "POST":
        country = request.POST.get("country")
        if country and country in state_countries_dict:
            profile.country = country
            state = request.POST.get("state")
            if state and state in state_countries_dict[country]:
                profile.state = state
            profile.save()
            return render(request, "team_hope/registration/journey.html")

    return render(request, "team_hope/registration/location.html")


def register_journey(request):
    if not request.user.is_authenticated:
        return redirect("team_hope:home")

    current_user = request.user
    profile, created = UserProfile.objects.get_or_create(user=current_user)

    if request.method == "POST":
        journey = request.POST.get("journey")
        if journey:
            profile.journey = journey[:4000]
            profile.save()
            return redirect("register_confirm")

    return render(request, "team_hope/registration/journey.html")


def register_confirm(request):
    if not request.user.is_authenticated:
        return redirect("team_hope:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Process the form data here
            pass

    return render(request, "team_hope/registration/confirm.html")


@login_required
def chat(request):
    if (
            not request.user.is_authenticated
    ):  # or not user_profile_is_complete(request.user):
        return redirect("team_hope:home")

    user_identity = UserIdentityInfo.objects.get(user=request.user)
    logging.info(f"Initiating chat by user with identity: {user_identity}")
    current_user = request.user
    ccuser = CCUser(current_user)

    try:
        ccuser_info = ccuser.get()
        if not ccuser_info:
            ccuser.sync()
            ccuser_info = ccuser.get()
    except Exception as error:
        logging.error(f"Failed to get or create CometChat user: {error}")
        return redirect("team_hope:home")

    if ccuser_info:
        params = {
            "COMET_APP_ID": settings.COMET_APP_ID,
            "COMET_REGION": settings.COMET_REGION,
            "COMET_AUTH_KEY": settings.COMET_AUTH_KEY,
            "DEPLOYENV": settings.DEPLOYENV,
            "UID": ccuser_info["uid"],
        }
        return render(request, "team_hope/chat.html", params)

    return redirect("team_hope:home")


@csrf_exempt
def cometchat_webhook(request):  # TODO in the future, we want to use all the fields in the email
    if request.method == "POST":
        data = json.loads(request.body).get("data")
        if data:
            # Extract message details
            try:
                sender_details = data["message"]["data"]["entities"]["sender"]["entity"]
                sender_name = sender_details["name"]
                sender_email = sender_details["metadata"]["@private"]["email"]
                sender_role = sender_details["role"]
                receiver_details = data["message"]["data"]["entities"]["receiver"]["entity"]
                receiver_type = data["message"]["data"]["entities"]["receiver"]["entityType"]
                sent_at = data["message"]["sentAt"]
                category = data["message"]["category"]
                group_id = None
                if receiver_type == "group":
                    group_id = receiver_details["guid"]
                    group_name = receiver_details["name"]
                    # get all the member emails from the group
                    group_url = (
                        f"https://{settings.COMET_APP_ID}.api-{settings.COMET_REGION}."
                        f"cometchat.io/v3/groups/{group_id}/members?perPage=100&page=1"
                    )  # TODO page must be dynamic in cases where there are many  members
                    headers = {
                        "accept": "application/json",
                        "apikey": settings.COMET_REST_API_KEY,
                    }

                    resp = requests.get(group_url, headers=headers)
                    users = resp.json().get("data", [])
                    # Retrieve the members of the group for email
                    user_details = [
                        {"email": user.get("metadata", {}).get("@private", {}).get("email"),
                         "name": user.get("name"),
                         }
                        for user in users if
                        user.get("metadata", {}).get("@private", {}).get("email") and
                        user.get("metadata", {}).get("@private", {}).get("email") != sender_email
                    ] if users else []
                    # send the email to the recipients in the group
                    logger.debug(f"Sending emails to :{user_details}\n From: {sender_email}")
                    notify_users_of_chat(recipients=user_details)

            except (KeyError, Exception) as error:
                logger.error(f"Failed to Generate message data due to : {error}")
                return {}

        return JsonResponse({"status": "success"})

    return JsonResponse({"error": "Invalid request"}, status=400)


# def handler500(request, *args, **kwargs):
#     """View for handling server errors that occur"""
#     return render(request, "500.html", status=500)
#
#
# def handler400(request, *args, **kwargs):
#     """View for handling bad requests"""
#     return render(request, "400.html", status=400)


def complete_signup(request, *ags, **kwargs):
    if request.method == "POST":
        register_choice = request.POST.get("register-choice")
        if register_choice:
            if register_choice == "alive_and_kicking":
                return redirect("team_hope:register_alive_and_kicking")
            elif register_choice == "team_hope":
                return redirect("team_hope:register_team_hope")
        else:
            msg = _("Pick one of the programs to proceed.")
            messages.add_message(request, messages.WARNING, msg)
    # messages.add_message(request, messages.SUCCESS, "Welcome to this page")
    return render(request, "team_hope/complete-signup.html")
