from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path

from . import views
from .views import ProfileUpdateView, CustomLogoutView
from .views import azure_b2c_login, azure_b2c_callback, home
from .views import chat
from .views import (
    user_type,
    register_type,
    register_confirm,
    register_location,
    register_journey,
    register_team_hope,
    register_alive_and_kicking,
    ProfilePictureUpdateView,
    logout_view,
    logout_complete_view,
)

app_name = 'team_hope'
urlpatterns = [
    path("tyn997tpjaekxycjvjjq7y/", admin.site.urls),
    path("components/", include("components.urls")),
    re_path(r"^$", views.index, name="index"),
    path("home", home, name="home"),
    # Azure B2C Authentication
    path("auth/login/", azure_b2c_login, name="azure_b2c_login"),
    path(
        "auth/logout/",
        CustomLogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL),
        name="azure_b2c_logout",
    ),
    path("auth/callback/", azure_b2c_callback, name="azure_b2c_callback"),
    # Registration begins
    path("register/user_type", user_type, name="register_user_type"),
    path("register/team_hope/", register_team_hope, name="register_team_hope"),
    path(
        "register/alive_and_kicking/",
        register_alive_and_kicking,
        name="register_alive_and_kicking",
    ),
    # take in user type, display location
    path("register/register_type", register_type, name="register_type"),
    # take in location, display user journey
    path("register/location", register_location, name="register_location"),
    # take in journey, display confirmation
    path("register/journey", register_journey, name="register_journey"),
    path("register/confirm/", register_confirm, name="register_confirm"),
    path("chat", chat, name="chat"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
    path(
        "profile/picture/",
        ProfilePictureUpdateView.as_view(),
        name="profile_picture_edit",
    ),
    # path('logout/', CustomLogoutView.as_view(), name='logout')
    path("logout/", logout_view, name="logout"),
    path("logout/complete/", logout_complete_view, name="logout_complete"),
    path(
        "unsubscribe/alive_and_kicking",
        views.unsubscribe_alive_and_kicking,
        name="unsubscribe_alive_and_kicking",
    ),  # Add this line
    path(
        "unsubscribe/teamhope",
        views.unsubscribe_teamhope,
        name="unsubscribe_teamhope",
    ),  # Add this line
    path("docusign/webhook", views.docusign_webhook, name="docusign_webhook"),
    path("cometchat/webhook", views.cometchat_webhook, name="cometchat_webhook"),
]
