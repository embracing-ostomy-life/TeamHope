from django.db.models import Avg, Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
import jwt
from jwt import PyJWKClient
import requests
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpResponseRedirect, HttpResponse
from datetime import datetime
from .forms import RegisterForm
from .models import UserProfile, UserType, UserIdentityInfo  # Updated to use the new model name
from components.cascading_selects.states import state_countries_dict
from .cometchat import CCUser

def azure_b2c_login(request):
    redirect_uri = request.build_absolute_uri(reverse('azure_b2c_callback'))
    return HttpResponseRedirect(settings.AZURE_B2C_AUTH_URL.format(redirect_uri=redirect_uri))

class CustomLogoutView(LogoutView):
    # Add custom logic here if necessary
    pass

def validate_age(birth_year):
    current_year = datetime.now().year
    age = current_year - birth_year
    return age >= 18

def azure_b2c_callback(request):
    token = request.GET.get('id_token')
    if not token:
        return HttpResponse("Token not found in the response", status=400)

    try:
        print(f"Token: {token}")

        # Set the URL for the JWKS (JSON Web Key Set)
        jwks_url = f"https://{settings.AZURE_B2C_TENANT}.b2clogin.com/{settings.AZURE_B2C_TENANT}.onmicrosoft.com/{settings.AZURE_B2C_POLICY_NAME}/discovery/v2.0/keys"
        print(f"Fetching keys from: {jwks_url}")

        # Use PyJWKClient to get the signing key
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Decode the JWT token using the signing key
        payload = jwt.decode(token, signing_key.key, algorithms=['RS256'], audience=settings.AZURE_B2C_CLIENT_ID)

        print(f"Payload: {payload}")

        email = payload.get('emails', [None])[0]  # Extract email from 'emails' list
        username = email.split('@')[0] if email else payload.get('name')  # Use email's local part as username
        first_name = payload.get('extension_FirstName', payload.get('name', ''))  # Use 'name' if 'FirstName' extension is not available
        last_name = payload.get('extension_LastName', payload.get('family_name', ''))
        birth_year = payload.get('birth_year')
        country = payload.get('country', '')  # Optional field
        guid = payload.get('oid')

        print(f"Email: {email}, Username: {username}, First Name: {first_name}, Last Name: {last_name}, Birth Year: {birth_year}, Country: {country}, GUID: {guid}")

        if birth_year and not validate_age(int(birth_year)):
            return render(request, 'team_hope/under_18_no_access.html')

        user, created = User.objects.get_or_create(email=email, defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
        })

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        identity_info, created = UserIdentityInfo.objects.get_or_create(user=user)
        identity_info.date_of_birth = datetime(year=int(birth_year), month=1, day=1) if birth_year else None
        identity_info.uuid = guid
        identity_info.save()

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.country = country
        profile.save()

        if profile.registered:
            ccuser = CCUser(user)
            ccuser.sync()

        login(request, user)
        return redirect('/home')

    except jwt.ExpiredSignatureError:
        return HttpResponse("Token has expired", status=400)
    except jwt.InvalidTokenError:
        return HttpResponse("Invalid token", status=400)
    except Exception as e:
        print(f"Error: {str(e)}")
        return HttpResponse("An error occurred.", status=500)

def user_profile_is_complete(current_user):
    profile = UserProfile.objects.get(user=current_user)
    identity_info = UserIdentityInfo.objects.get(user=current_user)
    if profile is None or profile.agreed is None or not profile.agreed:
        return False
    if profile.country is None or profile.country == "":
        return False
    if identity_info.date_of_birth and not validate_age(identity_info.date_of_birth.year):
        return False
    return profile.registered

def home(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                profile, created = UserProfile.objects.get_or_create(user=current_user)
                profile.subscribed_to_email_updates = form.cleaned_data['subscribe_updates']
                profile.subscribed_to_30_day_recovery = form.cleaned_data['subscribe_recovery']
                profile.agreed = form.cleaned_data['certify']
                profile.registered = True
                profile.save()
                try:
                    ccuser = CCUser(current_user)
                    ccuser.sync()
                except Exception as error:
                    print(f"Failed to sync CometChat user: {error}")

        params = {
            'chat_enabled': user_profile_is_complete(current_user),
            'user_profile_is_complete': user_profile_is_complete(current_user)
        }
        return render(request, 'team_hope/home.html', params)
    else:
        return redirect(azure_b2c_login)

def index(request):
    if request.user.is_authenticated:
        return redirect(home)
    return redirect(azure_b2c_login)

def user_type(request):
    tgt_page = 'registration/user_type.html'
    if request.user.is_authenticated:
        return render(request, 'team_hope/' + tgt_page)
    return redirect(home)

def register_type(request):
    tgt_page = "registration/location.html"
    if request.user.is_authenticated:
        current_user = request.user
        utype = request.GET.get('type')
        if utype == '0':
            tgt_type = UserType.MAYBE
        elif utype == '1':
            tgt_type = UserType.OST
        elif utype == '2':
            tgt_type = UserType.CARE
        elif utype == '3':
            tgt_type = UserType.MEDPRO
        else:
            return render(request, 'team_hope/' + tgt_page)

        profile, created = UserProfile.objects.get_or_create(user=current_user)
        profile.user_type = tgt_type
        profile.save()
        return render(request, 'team_hope/' + tgt_page)
    return redirect(home)

def register_location(request):
    tgt_page = "registration/journey.html"
    if request.user.is_authenticated:
        if request.method == 'POST':
            current_user = request.user
            country = request.POST.get('country')
            if country and country in state_countries_dict:
                profile, created = UserProfile.objects.get_or_create(user=current_user)
                profile.country = country
                state = request.POST.get('state')
                if state and state in state_countries_dict[country]:
                    profile.state = state
                profile.save()
        return render(request, 'team_hope/' + tgt_page)
    return redirect(home)

def register_journey(request):
    tgt_page = "registration/confirm.html"
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            journey = request.POST.get('journey')
            if journey:
                profile, created = UserProfile.objects.get_or_create(user=current_user)
                profile.journey = journey[:4000]
                profile.save()
        return render(request, 'team_hope/' + tgt_page)
    return redirect(home)

def register_confirm(request):
    tgt_page = "registration/confirm.html"
    if request.user.is_authenticated:
        return render(request, 'team_hope/' + tgt_page)
    return redirect(home)

def chat(request):
    tgt_page = "chat.html"
    if request.user.is_authenticated:
        current_user = request.user
        if not user_profile_is_complete(current_user):
            return redirect(home)

        ccuser = CCUser(current_user)
        try:
            ccuser_info = ccuser.get()
            if not ccuser_info:
                ccuser.sync()
                ccuser_info = ccuser.get()
        except Exception as error:
            print(f"Failed to get or create CometChat user: {error}")
            return redirect(home)

        if ccuser_info:
            params = {
                'COMET_APP_ID': settings.COMET_APP_ID,
                'COMET_REGION': settings.COMET_REGION,
                'COMET_AUTH_KEY': settings.COMET_AUTH_KEY,
                'DEPLOYENV': settings.DEPLOYENV,
                'UID': ccuser_info['uid'],
            }
            return render(request, 'team_hope/' + tgt_page, params)
    return redirect(home)
