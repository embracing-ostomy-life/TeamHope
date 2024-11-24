import time
import requests
from threading import Lock
from docusign_esign import ApiClient
from jwt import encode
from django.conf import settings

DS_CLIENT_ID = settings.DS_CLIENT_ID
DS_IMPERSONATED_USER_ID = settings.DS_IMPERSONATED_USER_ID
DS_PRIVATE_KEY = settings.DS_PRIVATE_KEY
DS_AUTHORIZATION_SERVER = settings.DS_AUTHORIZATION_SERVER
DS_HOST = settings.DS_HOST
SIGNATURE_SCOPES = ["signature", "impersonation"]


class DocuSignTokenManager:
    """Singleton class for Docusign."""

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        """Singleton implementation to ensure only one instance."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(DocuSignTokenManager, cls).__new__(
                        cls, *args, **kwargs
                    )
        return cls._instance

    def __init__(self):
        """Initialize the token manager with required configurations."""
        if not hasattr(self, "access_token"):
            self.access_token = None
            self.token_expiry = 0  # Epoch timestamp when the token expires
            self.client_id = DS_CLIENT_ID
            self.user_id = DS_IMPERSONATED_USER_ID
            self.private_key = DS_PRIVATE_KEY
            self.oauth_base_url = DS_AUTHORIZATION_SERVER
            self.api_client = ApiClient()

    def generate_jwt(self):
        """Generate a JWT for DocuSign."""
        jwt_payload = {
            "iss": self.client_id,
            "sub": self.user_id,
            "aud": self.oauth_base_url,
            "scope": "signature",
            "exp": int(time.time()) + 3600,  # 1-hour validity
        }
        return encode(jwt_payload, self.private_key, algorithm="RS256")

    def fetch_access_token(self):
        """Fetch a new access token from DocuSign."""
        try:
            response = self.api_client.request_jwt_user_token(
                client_id=self.client_id,
                user_id=self.user_id,
                oauth_host_name=self.oauth_base_url,
                private_key_bytes=self.private_key.encode(),
                expires_in=3600,
                scopes=SIGNATURE_SCOPES,
            )
            self.access_token = response.access_token
            self.token_expiry = (
                int(time.time()) + 3600
            )  # Token expiry is 1 hour from now
        except Exception as e:
            raise Exception(f"Failed to fetch DocuSign access token: {str(e)}")

    def get_access_token(self):
        """Retrieve the current token or refresh if expired."""
        if self.access_token is None or time.time() >= self.token_expiry:
            self.fetch_access_token()
        return self.access_token

    def get_api_client(self):
        """Retrieve the API client with a valid access token."""
        if self.access_token is None or time.time() >= self.token_expiry:
            self.fetch_access_token()
        self.api_client.set_default_header(
            "Authorization", f"Bearer {self.access_token}"
        )
        self.api_client.host = f"https://{DS_HOST}/restapi"
        return self.api_client
