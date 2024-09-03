from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from datetime import datetime
import jwt
from jwt import PyJWKClient
from .forms import RegisterForm, ProfileForm, ProfilePictureForm, RegisterTeamHopeForm
from .models import UserProfile, UserIdentityInfo, UserType
from .cometchat import CCUser
from .utils import sendgrid_unsubscribe_user, user_profile_is_complete, validate_age
from components.cascading_selects.states import state_countries_dict



def azure_b2c_login(request):
    redirect_uri = request.build_absolute_uri(reverse('azure_b2c_callback'))
    return HttpResponseRedirect(settings.AZURE_B2C_AUTH_URL.format(redirect_uri=redirect_uri))

def azure_b2c_callback(request):
    token = request.GET.get('id_token')
    if not token:
        return HttpResponse("Token not found in the response", status=400)

    try:
        jwks_url = f"https://{settings.AZURE_B2C_TENANT}.b2clogin.com/{settings.AZURE_B2C_TENANT}.onmicrosoft.com/{settings.AZURE_B2C_POLICY_NAME}/discovery/v2.0/keys"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(token, signing_key.key, algorithms=['RS256'], audience=settings.AZURE_B2C_CLIENT_ID)

        email = payload.get('emails', [None])[0]
        username = email.split('@')[0] if email else payload.get('name')
        first_name = payload.get('extension_FirstName', '')
        last_name = payload.get('extension_LastName', '')
        guid = payload.get('oid')

        user, created = User.objects.get_or_create(email=email, defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
        })

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        identity_info, created = UserIdentityInfo.objects.get_or_create(user=user)
        identity_info.uuid = guid
        identity_info.save()

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.country = payload.get('country', '')
        profile.save()

        if profile.registration_complete:
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

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileForm
    template_name = 'profile/edit_profile.html'
    success_url = '/profile/'

    def get_object(self):
        return self.request.user.userprofile

class ProfilePictureUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfilePictureForm
    template_name = 'profile/edit_profile_picture.html'
    success_url = '/profile/'

    def get_object(self):
        return self.request.user.userprofile

class CustomLogoutView(LogoutView):
    template_name = 'registration/logged_out.html'

def home(request):
    if not request.user.is_authenticated:
        return redirect('azure_b2c_login')

    current_user = request.user
    is_profile_complete = user_profile_is_complete(current_user)

    if request.method == 'POST':
        form = RegisterForm(request.POST, instance=current_user.userprofile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.registration_complete = True  # Mark as registered if applicable
            profile.save()

            try:
                ccuser = CCUser(current_user)
                ccuser.sync()
            except Exception as error:
                print(f"Failed to sync CometChat user: {error}")

    else:
        form = RegisterForm(instance=current_user.userprofile)

    params = {
        'chat_enabled': is_profile_complete,
        'user_profile_is_complete': is_profile_complete,
        'form': form
    }
    return render(request, 'team_hope/home.html', params)

def index(request):
    if request.user.is_authenticated:
        return redirect('home')
    return redirect(azure_b2c_login)

def user_type(request):
    if not request.user.is_authenticated:
        return redirect('home')
    return render(request, 'team_hope/registration/user_type.html')

def register_type(request):
    if not request.user.is_authenticated:
        return redirect('home')

    current_user = request.user
    profile, created = UserProfile.objects.get_or_create(user=current_user)

    if request.method == 'GET':
        utype = request.GET.get('type')
        if utype in [UserType.CONSIDERING_SURGERY, UserType.OSTOMATE, UserType.CAREGIVER, UserType.MEDICAL_PROFESSIONAL, UserType.SUPPORTER]:
            profile.user_type = utype
            profile.save()
            return render(request, 'team_hope/registration/location.html')

    return render(request, 'team_hope/registration/user_type.html')

def register_team_hope(request):
    if not request.user.is_authenticated:
        return redirect('azure_b2c_login')

    current_user = request.user
    profile, created = UserProfile.objects.get_or_create(user=current_user)

    if request.method == 'POST':
        form = RegisterTeamHopeForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.team_hope_all_complete = True
            profile.save()
            return redirect('home')
    else:
        form = RegisterTeamHopeForm(instance=profile)

    return render(request, 'team_hope/register_team_hope.html', {'form': form})

def register_alive_and_kicking(request):
    if not request.user.is_authenticated:
        return redirect(azure_b2c_login)

    current_user = request.user
    profile = UserProfile.objects.get(user=current_user)

    if request.method == 'POST':
        form = RegisterForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.subscribed_to_aliveandkicking = True
            if not profile.surgery_date:
                profile.surgery_date = form.cleaned_data.get('surgery_date')
            profile.save()
            return redirect('home')
    else:
        form = RegisterForm(instance=profile)

    return render(request, 'team_hope/register_alive_and_kicking.html', {'form': form})

def unsubscribe_alive_and_kicking(request):
    if not request.user.is_authenticated:
        return redirect(azure_b2c_login)

    current_user = request.user
    profile = UserProfile.objects.get(user=current_user)

    if request.method == 'POST':
        profile.subscribed_to_aliveandkicking = False
        profile.save()

        # Unsubscribe the user from the SendGrid list
        success = sendgrid_unsubscribe_user(profile.user.email)
        if success:
            messages.success(request, "You have successfully unsubscribed from Alive and Kicking.")
        else:
            messages.error(request, "There was an issue unsubscribing you. Please try again later.")
        
        return redirect('home')

    return render(request, 'team_hope/unsubscribe_alive_and_kicking.html')

def register_location(request):
    if not request.user.is_authenticated:
        return redirect('home')

    current_user = request.user
    profile, created = UserProfile.objects.get_or_create(user=current_user)

    if request.method == 'POST':
        country = request.POST.get('country')
        if country and country in state_countries_dict:
            profile.country = country
            state = request.POST.get('state')
            if state and state in state_countries_dict[country]:
                profile.state = state
            profile.save()
            return render(request, 'team_hope/registration/journey.html')

    return render(request, 'team_hope/registration/location.html')

def register_journey(request):
    if not request.user.is_authenticated:
        return redirect('home')

    current_user = request.user
    profile, created = UserProfile.objects.get_or_create(user=current_user)

    if request.method == 'POST':
        journey = request.POST.get('journey')
        if journey:
            profile.journey = journey[:4000]
            profile.save()
            return redirect('register_confirm')

    return render(request, 'team_hope/registration/journey.html')

def register_confirm(request):
    if not request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Process the form data here
            pass

    return render(request, 'team_hope/registration/confirm.html')

def chat(request):
    if not request.user.is_authenticated or not user_profile_is_complete(request.user):
        return redirect('home')

    current_user = request.user
    ccuser = CCUser(current_user)

    try:
        ccuser_info = ccuser.get()
        if not ccuser_info:
            ccuser.sync()
            ccuser_info = ccuser.get()
    except Exception as error:
        print(f"Failed to get or create CometChat user: {error}")
        return redirect('home')

    if ccuser_info:
        params = {
            'COMET_APP_ID': settings.COMET_APP_ID,
            'COMET_REGION': settings.COMET_REGION,
            'COMET_AUTH_KEY': settings.COMET_AUTH_KEY,
            'DEPLOYENV': settings.DEPLOYENV,
            'UID': ccuser_info['uid'],
        }
        return render(request, 'team_hope/chat.html', params)

    return redirect('home')
