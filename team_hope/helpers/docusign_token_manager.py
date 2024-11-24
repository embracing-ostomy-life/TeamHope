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
    _private_key = """
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEApUL/jzWLLNzrbkRivz/wBU5Qw6zWsJ31aowYWOrMz9kRJQaF
Xbm6txUKxEjQRWXlX8AD71y4b/x9/qJORlsU2K6DHIUqb/6cRsoiQ06eV+7xzvOv
5dK3LvTu3MKMEmzBNTyPgr1ndIzjQ3AcW6WLtGOtN54VsRGGlYtcxn0hWodmbPXZ
OVDodbc6b7O2Opj+3IkJ7TT07ENgZ0u/ioTBQVNnktYTmzbYe07DvIFvDpOlzIXx
Xb2lTB0IV6xR9Kmk16tJatHBNNWN5krekR7A6VRMxFa3K2W8EHnBtvZXpl6dxX4I
3B+epONhdxKsGBSiWbBfdwpuNd7VpTee6um/PwIDAQABAoIBABSmriO5p6YYBy10
yzgl57rqAeqpxvw0CO5jCknWMXjJobxUN8cyBdSKAxnrFWeOp56S8orvNbb8wMvY
gVqGWDEJgaXHODndga7Q5H4vrVbEq5/WUMUx0yVBgzW/89v7jhs2caJ/Q5XLYzzS
niCPq8kDaapZDVHepEg8rX+6NDhJHnnAFSYYKWaEqu/pGmdwlOE/nmwe4nWDiLCL
z4r7VTl87S5vAZeOWEsIYaN6TYkrwGGlm9emepwjzMOdyC4sbFIIE6kBhMp5ZyZw
bAoFtMzt8677CcY4pvpfaMN04AJywX6lJsMwwWAey81ogmdUa0pMvVAmaAMPuaPf
TAN7TzECgYEA5bO/Bpsacbaxj+edErc/eGKw7lz4+b/zdXIDcbkIgODUWrgHQEdW
sInh8rPj55pMjFeS1C0Rn9kUwGnxO+KD69TTnKeEAGXZd/+LLU+ahDUPZahJiVSA
TN+/oMthlWf46+cISjDVY6cu31Hsu8PNUq4ydtMM4Hx1zT8bGJvUF/ECgYEAuC6X
hvrjOEiz4H+tqMtrRU4cs44xXbTSo4sQALUfB3F7KzJMKOoQZOsq7oQLo/K2rcFZ
KT+KnMHnKhwSVoOJwN/RwsRcZ5QR7pzxWU8XVZ0hE2gNV9AZfamoenOmR+JAX2jP
YmlY75zPkOCqGCitUq353Wv/bJMUJCeAIwEY+i8CgYAilURebz20/yeOnfV1GufQ
bTNsP80wdOjntsmz9oLEPJVcLzbQQ61WmPvOuazHcuCxhIHTthFgOqO4MHskY/8u
o3VUsZfbI3pxaaT/pmuCGib+TC7+IR3L9Sf5woUnpGbCxZ7m5KFMBqC0+LWms10X
ZKiuYSogJjzqMOUYeGWfUQKBgCiM8YWhZTd2IkxSMAzSxIpcuUr7CnlkH2AsdNiD
CBLedEy9ZTE432UotaoP3nQ5MuksgZHoUH9U3a1SwuLTURfq70bfbqzLV+teGHEe
TbfmwWqBZTapNYOKP/K91aVL9fpLnCVBpngS4Uw3epuZERf7/+A1L+Zat3uCSt7q
FfK3AoGBAMr5wlEKChmFKUMHEhIafQpmI0IRkqfFhRRthoYuhLA08hZ8Xt52rmC9
qNr8t1lkmUfuxD58qmpZw0Lz0to0eRnvW3wHne8ROx4meggnglj10eFwBwTApToc
i4Zr7puY8XWtB63g3131KwVsMn8BUDgvb/qyfcD1/W8G8OcWduuW
-----END RSA PRIVATE KEY-----
"""

    _public_key = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApUL/jzWLLNzrbkRivz/w
BU5Qw6zWsJ31aowYWOrMz9kRJQaFXbm6txUKxEjQRWXlX8AD71y4b/x9/qJORlsU
2K6DHIUqb/6cRsoiQ06eV+7xzvOv5dK3LvTu3MKMEmzBNTyPgr1ndIzjQ3AcW6WL
tGOtN54VsRGGlYtcxn0hWodmbPXZOVDodbc6b7O2Opj+3IkJ7TT07ENgZ0u/ioTB
QVNnktYTmzbYe07DvIFvDpOlzIXxXb2lTB0IV6xR9Kmk16tJatHBNNWN5krekR7A
6VRMxFa3K2W8EHnBtvZXpl6dxX4I3B+epONhdxKsGBSiWbBfdwpuNd7VpTee6um/
PwIDAQAB
-----END PUBLIC KEY----
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
