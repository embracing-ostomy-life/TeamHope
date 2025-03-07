"""
Django settings for embracing_ostomy_life project.

Generated by 'django-admin startproject' using Django 4.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path

import environ

DEBUG = True
env = environ.Env(
    DEBUG=(bool, False)
)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(BASE_DIR / '.env')

print("\n\n\n\nIn normal settings :)\n\n\n\n")
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")
COMET_APP_ID = os.getenv("COMET_APP_ID")
COMET_AUTH_KEY = os.getenv("COMET_AUTH_KEY")
COMET_REST_API_KEY = os.getenv("COMET_REST_API_KEY")
COMET_REGION = os.getenv("COMET_REGION")
DEPLOYENV = os.getenv("DEPLOYENV")

AZURE_B2C_CLIENT_ID = os.getenv("AZURE_B2C_CLIENT_ID")
AZURE_B2C_CLIENT_SECRET = os.getenv("AZURE_B2C_CLIENT_SECRET")
AZURE_B2C_TENANT = os.getenv("AZURE_B2C_TENANT")
AZURE_B2C_DOMAIN = os.getenv("AZURE_B2C_DOMAIN")
AZURE_B2C_POLICY_NAME = os.getenv("AZURE_B2C_POLICY_NAME")
AZURE_B2C_REDIRECT_URI = os.getenv("DEV_AZURE_B2C_REDIRECT_URI")
AZURE_POST_LOGOUT_REDIRECT_URI = os.getenv("APP_URL") + "/logout/complete/"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_ALIVE_AND_KICKING_ID = os.getenv("SENDGRID_ALIVE_AND_KICKING_ID")

AZURE_B2C_AUTH_URL = f"https://{AZURE_B2C_TENANT}.b2clogin.com/{AZURE_B2C_TENANT}.onmicrosoft.com/oauth2/v2.0/authorize?p={AZURE_B2C_POLICY_NAME}&client_id={AZURE_B2C_CLIENT_ID}&response_type=id_token&redirect_uri={{redirect_uri}}&response_mode=query&scope=openid%20profile%20email&state=12345"
AZURE_B2C_LOGOUT_URL = f"https://{AZURE_B2C_TENANT}.b2clogin.com/{AZURE_B2C_TENANT}.onmicrosoft.com/oauth2/v2.0/logout?p={AZURE_B2C_POLICY_NAME}&post_logout_redirect_uri={AZURE_POST_LOGOUT_REDIRECT_URI}"

# DOCUSIGN
DS_CLIENT_ID = os.getenv("DS_CLIENT_ID")
DS_IMPERSONATED_USER_ID = os.getenv("DS_IMPERSONATED_USER_ID")
DS_PRIVATE_KEY = os.getenv("DS_PRIVATE_KEY")
DS_AUTHORIZATION_SERVER = os.getenv("DS_AUTHORIZATION_SERVER")
DS_ALIVE_KICKING_TEMPLATE_ID = os.getenv("DS_ALIVE_KICKING_TEMPLATE_ID")
DS_TEAM_HOPE_MEMBER_TEMPLATE_ID = os.getenv("DS_TEAM_HOPE_MEMBER_TEMPLATE_ID")
DS_TEAM_HOPE_VOLUNTEER_TEMPLATE_ID = os.getenv("DS_TEAM_HOPE_VOLUNTEER_TEMPLATE_ID")
DS_REDIRECT_URL = os.getenv("DS_REDIRECT_URL")
DS_ACCOUNT_ID = os.getenv("DS_ACCOUNT_ID")
DS_HOST = os.getenv("DS_HOST")
DS_CALLBACK_SECRET = os.getenv("DS_CALLBACK_SECRET")

# MAILCHIMP
MAILCHIMP_TRANSACTIONAL_API_KEY = os.getenv("MAILCHIMP_TRANSACTIONAL_API_KEY")
MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MAILCHIMP_SERVER_KEY = os.getenv("MAILCHIMP_SERVER_KEY")
MAILCHIMP_LIST_ID = os.getenv("MAILCHIMP_LIST_ID")
# SECURITY WARNING: don't run with debug turned on in production!


# settings.py

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"  # AZURE_B2C_LOGOUT_URL

ALLOWED_HOSTS = [
    "169.254.131.3",
    "localhost:8000",
    "localhost",
    "app.embracingostomylife.org",
]

if "CODESPACE_NAME" in os.environ:
    CSRF_TRUSTED_ORIGINS = [
        f'https://{os.getenv("CODESPACE_NAME")}-8000.{os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")}'
    ]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_components",
    "django.contrib.sites",  #
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "team_hope",
    # 'allauth.socialaccount.providers.azure',#
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = ("allauth.account.auth_backends.AuthenticationBackend",)  #

SOCIALACCOUNT_PROVIDERS = {
    "azure": {
        "APP": {
            "client_id": os.getenv("AZURE_B2C_CLIENT_ID"),
            "secret": os.getenv("AZURE_B2C_CLIENT_SECRET"),
            "key": "",
        },
        "tenant": os.getenv("AZURE_B2C_TENANT"),
    }
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Add a comma here
    "allauth.account.middleware.AccountMiddleware",
]

STATICFILES_DIRS = [os.path.join(BASE_DIR, "components")]

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
ROOT_URLCONF = "embracing_ostomy_life.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        # 'APP_DIRS': True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "team_hope.context_processors.azure_b2c_logout_url",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                        "django_components.template_loader.Loader",
                    ],
                )
            ],
            "builtins": [
                "django_components.templatetags.component_tags",
            ],
        },
    },
]

WSGI_APPLICATION = "embracing_ostomy_life.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# To use sqllite as the database engine,
#   uncomment the following block and comment out the Postgres section below


# Configure Postgres database for local development
#   Set these environment variables in the .env file for this project.
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.environ.get("DBNAME"),
#         "HOST": os.environ.get("DBHOST"),
#         "USER": os.environ.get("DBUSER"),
#         "PASSWORD": os.environ.get("DBPASS"),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',  # os.environ.get('DBNAME'),
        'HOST': 'localhost',  # os.environ.get('DBHOST'),
        'PORT': '5431',  # os.environ.get('DBPORT'),
        'USER': 'postgres',  # os.environ.get('DBUSER'),
        'PASSWORD': 'TeamHope1',  # os.environ.get('DBPASS'),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "apikey")
EMAIL_HOST_PASSWORD = os.getenv("SENDGRID_API_KEY")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL","admin@embracingostomylife.org")

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/1",  # Replace with your Redis server's location
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
# CACHES = {
#         "default": {
#             "BACKEND": "django_redis.cache.RedisCache",
#             "LOCATION": os.environ.get('CACHELOCATION'),
#             "OPTIONS": {
#                 "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         },
#     }
# }

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATICFILES_DIRS = (str(BASE_DIR.joinpath("static")),)
STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": env("DJANGO_LOG_FILE"),
            "level": env("DJANGO_LOG_LEVEL"),
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": env("DJANGO_LOG_LEVEL"),
            "formatter": "verbose",
        }

    },
    "loggers": {
        "team_hope": {
            "level": env("DJANGO_LOG_LEVEL"),
            "handlers": ["file", "console"],
            "propagate": True,
        }
    },
    "formatters": {
        "verbose": {
            "format": "{asctime}: {levelname}: {name} IN {module}.py:(line {lineno:d}) : {message}",
            "style": "{",
        }
    }

}
