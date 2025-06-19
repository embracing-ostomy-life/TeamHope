import time
from threading import Lock

from django.conf import settings
from docusign_esign import ApiClient
from jwt import encode

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
    _private_key_dev = """
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAz8SoTt0cNQ6C5TSNIDUT8sggCOcN57MGS3ubZPv2KnMYv44+
4BqHt0Vrz7+WQ1hns+5ejw4Rtu9lcMFDBio3foTFLMHaG0YRYPsSLmsouFpHXViC
ZOKfIIYwedz+EMH+VT/aISzJCNOOHEN5gSfNn5VLp590jrc8x/g6ogTk53FB5mYH
+tw9P6JBKD3CdaLHQ1FaDAAmkfn3c0sE8MsbuFhzZaPJFhjijjQRfEgKlnspFPIY
eA2NHO+K1KYPnM9yhjhNynOuXjbkWvvPrBdcJ7NTFBuhxP0qdb+jgQ0fb9OLaXo4
Rks5s7FN9Fo5Mn+nTiTCgdR1TCK8KT+Bw0ARVQIDAQABAoH/MamfB7D5741XMpnJ
cMvcs+a/wYhlhZBi5vbWEJJQ7IXlRvglrOHlopCJKtqDQalzvedGUIkWPMGGTJ6q
cInh4VI9p/UkcjkcKWrt48gb/X7R8puhyo9NPvj7xMLdC64/iUh1DKBi9zkkKzri
AX1Q7izyywDmIHIOvKosvCsgjAoh3zp7rec4qqrseeVz7JIaXjz3QW3zgJBT3Y8G
liG3AD1mmA//NJzoVzp30aIn6TCXSfqHCs0LGGnjLIDCqo5jrscoe6patauIvpgO
CoAavBw0KWn9SDCOsrzN8Fdgps/PVHV1pP3Gf+v0xDiAmwv95Lso103Y4pzNBHo2
FMCjAoGBAPOEJvxHGXD+Io7wJc6Cb9cELqHqwj/q61iatC1ne0fRk4OJnOi7GFSm
mwGpSqDqy2VODtTIIIofL6oIAxyM0miP2F/6a3WHlV/51tSB4H73FPMAymQeXBX9
Dsb9yeXHpqGg7z65c17XuFtuLwF5he9lWfflxg2daRXCG2DDh74fAoGBANprW1Pa
DJYPcFqRWCEcc/3bjmpwXLv6BYRui7ZD8l5eWbPktWZlAGco1thGasXYQldqZeHu
RSbS98jHyQmGYJE/2hP7P8VZLw8dgtLbTPFyA4USgLgVjFn4BSoiwNsTB2wq26od
Dw8Ht/c1IyyKwDCEGUCStwzx1IwdP33B7FoLAoGBAKBxte4KOm0ERGjBOWey8VVN
4Bu2vX23npCmfYhc4hETuIm2JbgBbap4izCxBga4LIL2xzbTFP1sRs9UsBgjgI58
GChEqoCpcHXn+u/REsUUrqzdHHyStEGYlh/uHxRSUyuzCW7eaXFX2JQFKNtj4ic1
M+3tamyWBiLb3YYHzmwpAoGAVhr0if3v8Eht1oZt47+/ylf/sN5S8JgEDM03rsbi
iWlQm6aSDKfMnN5wtBouhYhXvvZm68Zu5HtOy4xXKLYc46X0ZuQpo7cg4iiUJmPl
1VlJIfDFZcy4487u2kmRFcxOpMnQhyOliBtW3tHH6Ata8MVi3x33o9bCH+p32S/V
6TkCgYEAmRADKCl6+WjGVrAIes/rqqrC/yrKDIsXT8cGHgMWICZUtsdO6yXsCQdD
KTtLi6EoymfkBTPHICsLRJa2pB0ENv6uzyRnGFF0TFRCKWcufxTJSxRuUNMpyoZd
184h5dTQv4hfe/Qvhs8TvzQLq/cbZ8EUu+neinDQRjjE2O/sgqI=
-----END RSA PRIVATE KEY-----
"""

    _private_key = """
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAz8SoTt0cNQ6C5TSNIDUT8sggCOcN57MGS3ubZPv2KnMYv44+
4BqHt0Vrz7+WQ1hns+5ejw4Rtu9lcMFDBio3foTFLMHaG0YRYPsSLmsouFpHXViC
ZOKfIIYwedz+EMH+VT/aISzJCNOOHEN5gSfNn5VLp590jrc8x/g6ogTk53FB5mYH
+tw9P6JBKD3CdaLHQ1FaDAAmkfn3c0sE8MsbuFhzZaPJFhjijjQRfEgKlnspFPIY
eA2NHO+K1KYPnM9yhjhNynOuXjbkWvvPrBdcJ7NTFBuhxP0qdb+jgQ0fb9OLaXo4
Rks5s7FN9Fo5Mn+nTiTCgdR1TCK8KT+Bw0ARVQIDAQABAoH/MamfB7D5741XMpnJ
cMvcs+a/wYhlhZBi5vbWEJJQ7IXlRvglrOHlopCJKtqDQalzvedGUIkWPMGGTJ6q
cInh4VI9p/UkcjkcKWrt48gb/X7R8puhyo9NPvj7xMLdC64/iUh1DKBi9zkkKzri
AX1Q7izyywDmIHIOvKosvCsgjAoh3zp7rec4qqrseeVz7JIaXjz3QW3zgJBT3Y8G
liG3AD1mmA//NJzoVzp30aIn6TCXSfqHCs0LGGnjLIDCqo5jrscoe6patauIvpgO
CoAavBw0KWn9SDCOsrzN8Fdgps/PVHV1pP3Gf+v0xDiAmwv95Lso103Y4pzNBHo2
FMCjAoGBAPOEJvxHGXD+Io7wJc6Cb9cELqHqwj/q61iatC1ne0fRk4OJnOi7GFSm
mwGpSqDqy2VODtTIIIofL6oIAxyM0miP2F/6a3WHlV/51tSB4H73FPMAymQeXBX9
Dsb9yeXHpqGg7z65c17XuFtuLwF5he9lWfflxg2daRXCG2DDh74fAoGBANprW1Pa
DJYPcFqRWCEcc/3bjmpwXLv6BYRui7ZD8l5eWbPktWZlAGco1thGasXYQldqZeHu
RSbS98jHyQmGYJE/2hP7P8VZLw8dgtLbTPFyA4USgLgVjFn4BSoiwNsTB2wq26od
Dw8Ht/c1IyyKwDCEGUCStwzx1IwdP33B7FoLAoGBAKBxte4KOm0ERGjBOWey8VVN
4Bu2vX23npCmfYhc4hETuIm2JbgBbap4izCxBga4LIL2xzbTFP1sRs9UsBgjgI58
GChEqoCpcHXn+u/REsUUrqzdHHyStEGYlh/uHxRSUyuzCW7eaXFX2JQFKNtj4ic1
M+3tamyWBiLb3YYHzmwpAoGAVhr0if3v8Eht1oZt47+/ylf/sN5S8JgEDM03rsbi
iWlQm6aSDKfMnN5wtBouhYhXvvZm68Zu5HtOy4xXKLYc46X0ZuQpo7cg4iiUJmPl
1VlJIfDFZcy4487u2kmRFcxOpMnQhyOliBtW3tHH6Ata8MVi3x33o9bCH+p32S/V
6TkCgYEAmRADKCl6+WjGVrAIes/rqqrC/yrKDIsXT8cGHgMWICZUtsdO6yXsCQdD
KTtLi6EoymfkBTPHICsLRJa2pB0ENv6uzyRnGFF0TFRCKWcufxTJSxRuUNMpyoZd
184h5dTQv4hfe/Qvhs8TvzQLq/cbZ8EUu+neinDQRjjE2O/sgqI=
-----END RSA PRIVATE KEY-----
"""

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
            self.private_key = self._private_key
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
