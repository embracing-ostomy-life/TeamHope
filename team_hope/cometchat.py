import logging

import requests
from django.conf import settings
from django.contrib.auth.models import User

from .models import UserIdentityInfo, UserProfile, TeamHopeMemberRoleChoices

REST_API_KEY = settings.COMET_REST_API_KEY
REGION = settings.COMET_REGION
AUTH_KEY = settings.COMET_AUTH_KEY
APP_ID = settings.COMET_APP_ID

# Create a logger
logger = logging.getLogger(__name__)

json_headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "apiKey": REST_API_KEY,
}
default_headers = {"accept": "application/json", "apiKey": REST_API_KEY}


def _get_comet_url(urlstr):
    return f"https://{APP_ID}.api-{REGION}.cometchat.io/v3/{urlstr}"


def get_contacts():  # TODO implement this functionality
    """Return a list of contact dictionaries sorted by name."""
    return []


def get_chats():  # TODO implement this functionality
    """Return a list of chats sorted by most recent."""
    return []


def _api_get_all_convos():  # TODO implement this functionality currently this just prints out the output
    url = f"https://{APP_ID}.api-{REGION}.cometchat.io/v3/conversations?perPage=100&page=1"
    headers = {"Content-Type": "application/json", "apiKey": REST_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        convos = response.json()
        for convo in convos["data"]:
            print(convo["name"])
    else:
        logging.error(f"Error Obtaining chats:- Error code: {response.status_code}")


def _get_all_users():  # TODO implement this functionality: Also just prints out  the response
    url = f"https://{APP_ID}.api-{REGION}.cometchat.io/v3/users"
    headers = {"Content-Type": "application/json", "apiKey": REST_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        users = response.json()
        print("List of users:")
        for user in users["data"]:
            print(user["name"])
    else:
        logging.error(f"Error obtaining the users: Error code:-{response.status_code}")


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
    return response


def _metadata_params_add(params: dict, key, value):
    if params is None:
        params = {}
    if not params:
        params["@private"] = {}
    params["@private"][key] = value
    return params


class CCUser:
    """Class for interacting with CometChat users."""

    def __init__(self, user: User):
        self.django_user = user
        self.url = _get_comet_url("users")

    def get(self):
        identity_info = UserIdentityInfo.objects.get(user=self.django_user)
        url = self.url + "/" + identity_info.uuid
        logging.debug(f"Getting CometChat user with url (url/UUID) {url}")
        response = requests.get(url, headers=default_headers)
        logging.debug(f"Get returned status code {str(response.status_code)}")
        if response.status_code != 200:
            # User was not found in comet chat
            return None
        return response.json().get("data")

    def sync(self):
        """Update. Create if user doesn't exist."""
        get_res = self.get()
        if get_res is None:
            return self.create()
        else:
            return self.update()

    def create(self):
        params = self._gen_params()
        self._add_name_param(params)
        self._add_profile_picture(params)
        logging.debug(f"Creating CometChat user with params {str(params)}")
        logging.debug(f"Using URL {self.url} And headers {str(json_headers)}")
        response = requests.post(self.url, json=params, headers=json_headers)
        logging.debug(
            f"Create returned  status-code:- ({str(response.status_code)})\n And text {response.text}"
        )

        return response.json().get("data")

    def update(self):
        params = self._gen_params()
        identity_info = UserIdentityInfo.objects.get(user=self.django_user)
        self._add_profile_picture(params)
        url = self.url + "/" + identity_info.uuid
        logging.debug(f"Updating CometChat user with params {str(params)}")
        logging.debug(f"Using Url ({url}) And headers: ({str(json_headers)})")
        response = requests.put(url, json=params, headers=json_headers)
        logging.debug(f"Update returned status code: ({str(response.status_code)})\n And text {response.text}")
        return response.json().get("data")

    def _get_uid_param(self):
        identity_info = UserIdentityInfo.objects.get(user=self.django_user)
        if identity_info.uuid is not None:
            return {"uid": identity_info.uuid}
        return {}

    def _add_name_param(self, params: dict):
        if self.django_user.username is not None:
            params["name"] = f"{self.django_user.first_name.capitalize()} {self.django_user.last_name.capitalize()}"

    def _gen_params(self):
        user = self.django_user
        params = self._get_uid_param()
        try:
            role = UserProfile.objects.get(user=user).teamhope_member_role
        except UserProfile.DoesNotExist:
            role = TeamHopeMemberRoleChoices.PARTICIPANT
        if user and user.email is not None:
            metadata = params.get("metadata", {})
            self._add_name_param(params)
            _metadata_params_add(metadata, "email", user.email)
            _metadata_params_add(metadata, "role", role)
            params["metadata"] = metadata
        return params

    def _add_profile_picture(self, params: dict):
        """
        Update the parameters with an avatar if the profile has a profile picture
        """
        try:
            profile = UserProfile.objects.get(user=self.django_user)
            if profile.profile_picture:
                params["avatar"] = profile.profile_picture.url
        except UserProfile.DoesNotExist:
            logger.warning(f"Theres no user associated with this profile: {self.django_user}")
        return params
