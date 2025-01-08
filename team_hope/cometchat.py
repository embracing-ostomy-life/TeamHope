from django.conf import settings
import requests
from django.contrib.auth.models import User
from .models import UserProfile, UserType, UserIdentityInfo

REST_API_KEY = settings.COMET_REST_API_KEY
REGION = settings.COMET_REGION
AUTH_KEY = settings.COMET_AUTH_KEY
APP_ID = settings.COMET_APP_ID

json_headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "apiKey": REST_API_KEY,
}
default_headers = {"accept": "application/json", "apiKey": REST_API_KEY}


def _get_comet_url(urlstr):
    return f"https://{APP_ID}.api-{REGION}.cometchat.io/v3/{urlstr}"


def get_contacts():
    """Return a list of contact dictionaries sorted by name."""
    return []


def get_chats():
    """Return a list of chats sorted by most recent."""
    return []


def _api_get_all_convos():
    url = f"https://{APP_ID}.api-{REGION}.cometchat.io/v3/conversations?perPage=100&page=1"
    headers = {"Content-Type": "application/json", "apiKey": REST_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        convos = response.json()
        print("List of conversations:")
        for convo in convos["data"]:
            print(convo["name"])
    else:
        print("Error:", response.status_code)


def _get_all_users():
    url = f"https://{APP_ID}.api-{REGION}.cometchat.io/v3/users"
    headers = {"Content-Type": "application/json", "apiKey": REST_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        users = response.json()
        print("List of users:")
        for user in users["data"]:
            print(user["name"])
    else:
        print("Error:", response.status_code)


def _sendmsg():
    payload = {
        "category": "message",
        "type": "text",
        "data": {"text": "henlo"},
        "receiver": "superhero1",
        "receiverType": "user",
    }
    headers = {
        "accept": "application/json",
        "onBehalfOf": "superhero2",
        "content-type": "application/json",
        "apikey": REST_API_KEY,
    }
    url = f"https://{APP_ID}.api-{REGION}.cometchat.io/v3/messages"
    response = requests.post(url, json=payload, headers=headers)


def _metadata_params_add(params: dict, key, value):
    if params == {}:
        params["@private"] = {}
    params["@private"][key] = value


class CCUser:

    def __init__(self, user: User):
        self.django_user = user
        self.url = _get_comet_url("users")

    def get(self):
        identity_info = UserIdentityInfo.objects.get(user=self.django_user)
        print(identity_info.uuid)
        url = self.url + "/" + identity_info.uuid
        print("Getting CometChat user with UUID " + str(identity_info.uuid))
        print("Using URL " + url)
        response = requests.get(url, headers=default_headers)
        print("Get returned " + str(response.status_code) + " " + response.text)
        if response.status_code != 200:
            return None
        return response.json()["data"]

    def sync(self):
        """Update. Create if doesn't exist."""
        get_res = self.get()
        if get_res is None:
            self.create()
            self.update()
        else:
            self.update()

    def create(self):
        params = self._get_uid_param()
        self._add_name_param(params)
        print("Creating CometChat user with params " + str(params))
        print("Using URL " + self.url)
        print("Using headers: " + str(json_headers))
        response = requests.post(self.url, json=params, headers=json_headers)
        print("Create returned " + str(response.status_code) + " " + response.text)

    def update(self):
        params = self._gen_params()
        identity_info = UserIdentityInfo.objects.get(user=self.django_user)
        url = self.url + "/" + identity_info.uuid
        print("Updating CometChat user with params " + str(params))
        print("Using URL " + url)
        print("Using headers: " + str(json_headers))
        response = requests.put(url, json=params, headers=json_headers)
        print("Update returned " + str(response.status_code) + " " + response.text)

    def _get_uid_param(self):
        identity_info = UserIdentityInfo.objects.get(user=self.django_user)
        if identity_info.uuid is not None:
            return {"uid": identity_info.uuid}
        return None

    def _add_name_param(self, params: dict):
        if self.django_user.username is not None:
            params["name"] = self.django_user.username

    def _gen_params(self):
        user = self.django_user
        my_params = {}
        metadata = {}
        params = self._get_uid_param()
        self._add_name_param(params)
        if user.email is not None:
            _metadata_params_add(metadata, "email", user.email)
            my_params["metadata"] = metadata
        return params
