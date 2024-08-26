from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib import admin

from .views import azure_b2c_login, azure_b2c_callback, home
from .views import user_type, register_type, register_confirm, register_location, register_journey
from .views import chat, CustomLogoutView
from . import views 
from django.conf import settings

urlpatterns = [
    path("tyn997tpjaekxycjvjjq7y/", admin.site.urls),
    path('components/', include('components.urls')),
    re_path(r'^$', views.index, name='index'),
    path('home', home, name='home'),

    # Azure B2C Authentication
    path('auth/login/', azure_b2c_login, name='azure_b2c_login'),
    path('auth/logout/', CustomLogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='azure_b2c_logout'),
    path('auth/callback/', azure_b2c_callback, name='azure_b2c_callback'),

    # Registration begins
    path('register/user_type', user_type, name='register_user_type'),

    # take in user type, display location
    path('register/register_type', register_type, name='register_type'),

    # take in location, display user journey
    path('register/location', register_location, name='register_location'),

    # take in journey, display confirmation
    path('register/journey', register_journey, name='register_confirm'),

    path('chat', chat, name='chat'),
]
