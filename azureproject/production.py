import os

from .settings import *  # noqa
from .settings import BASE_DIR


print('\n\n\n\nIn production settings :)\n\n\n\n')

# Configure the domain name using the environment variable
# that Azure automatically creates for us.
ALLOWED_HOSTS = [os.environ['CUSTOM_WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['CUSTOM_WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')



# WhiteNoise configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Add whitenoise middleware after the security middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# Azure B2C Configuration
AZURE_B2C_CLIENT_ID = os.getenv('AZURE_B2C_CLIENT_ID')
AZURE_B2C_CLIENT_SECRET = os.getenv('AZURE_B2C_CLIENT_SECRET')
AZURE_B2C_TENANT = os.getenv('AZURE_B2C_TENANT')
AZURE_B2C_DOMAIN = os.getenv('AZURE_B2C_DOMAIN')
AZURE_B2C_POLICY_NAME = os.getenv('AZURE_B2C_POLICY_NAME')
AZURE_B2C_REDIRECT_URI = os.getenv('AZURE_B2C_REDIRECT_URI')

AZURE_B2C_AUTH_URL = f'https://{AZURE_B2C_TENANT}.b2clogin.com/{AZURE_B2C_TENANT}.onmicrosoft.com/oauth2/v2.0/authorize?p={AZURE_B2C_POLICY_NAME}&client_id={AZURE_B2C_CLIENT_ID}&response_type=id_token&redirect_uri={{redirect_uri}}&response_mode=query&scope=openid%20profile%20email&state=12345'
AZURE_B2C_LOGOUT_URL = f'https://{AZURE_B2C_TENANT}.b2clogin.com/{AZURE_B2C_TENANT}.onmicrosoft.com/oauth2/v2.0/logout?p={AZURE_B2C_POLICY_NAME}&post_logout_redirect_uri={AZURE_B2C_REDIRECT_URI}'


SESSION_ENGINE = "django.contrib.sessions.backends.cache"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configure Postgres database based on connection string of the libpq Keyword/Value form
# https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': conn_str_params['dbname'],
        'HOST': conn_str_params['host'],
        'USER': conn_str_params['user'],
        'PASSWORD': conn_str_params['password'],
    }
}

CACHES = {
        "default": {  
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ.get('AZURE_REDIS_CONNECTIONSTRING'),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        },
    }
}
