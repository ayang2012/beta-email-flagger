import os
import json
from flask import redirect, request, url_for
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

CLIENT_SECRETS_FILE = os.environ.get("CLIENT_SECRETS_FILE", "secrets/credentials.json")
G_CREDENTIALS_FILEPATH = "secrets/g_credentials.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("callback_route", _external=True, _scheme="https"),
    )
    authorization_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    return redirect(authorization_url)


def save_credentials(credentials, file_path):
    with open(file_path, "w") as f:
        json.dump(credentials_to_dict(credentials), f)


def load_credentials(file_path):
    with open(file_path, "r") as f:
        credentials_data = json.load(f)
        credentials = Credentials.from_authorized_user_info(credentials_data)
    return credentials


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


def callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("callback_route", _external=True, _scheme="https"),
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    save_credentials(credentials, G_CREDENTIALS_FILEPATH)
    return "Authorization successful! Credentials saved."
