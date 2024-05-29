import os
from flask import Flask, request, redirect, url_for
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
import base64
from pprint import pprint
import json

app = Flask(__name__)

# Load client secrets from the secure directory
CLIENT_SECRETS_FILE = os.environ.get('CLIENT_SECRETS_FILE', 'secrets/credentials.json')
G_CREDENTIALS_FILEPATH = 'secrets/g_credentials.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

@app.route('/')
def index():
    return redirect(url_for('authorize'))

@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('callback', _external=True, _scheme='https')
    )
    authorization_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return redirect(authorization_url)


def save_credentials(credentials, file_path):
    with open(file_path, 'w') as f:
        json.dump(credentials_to_dict(credentials), f)
def load_credentials(file_path):
    with open(file_path, 'r') as f:
        credentials_data = json.load(f)
        credentials = Credentials.from_authorized_user_info(credentials_data)
    return credentials
def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

@app.route('/callback')
def callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('callback', _external=True, _scheme='https')
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    # Save credentials to a file or database for later use
    save_credentials(credentials, G_CREDENTIALS_FILEPATH)
    
    return 'Authorization successful! Credentials saved.'


def fetch_recent_emails(credentials, max_results=10):
    service = build('gmail', 'v1', credentials=credentials)
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    decoded_emails = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg['payload']
        headers = payload['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        if subject:
            decoded_emails.append({'id': msg['id'], 'subject': subject})
    return decoded_emails


@app.route('/test_fetch_emails')
def test_fetch_emails():
    credentials = load_credentials(G_CREDENTIALS_FILEPATH)
    recent_emails = fetch_recent_emails(credentials)
    email_subjects = [email['subject'] for email in recent_emails]
    return '<br>'.join(email_subjects)

if __name__ == '__main__':
    app.run(debug=True)



if __name__ == '__main__':
    app.run(
        debug=True,
        ssl_context=(
            os.environ.get('SSL_CERT_FILE', 'secrets/localhost.crt'),
            os.environ.get('SSL_KEY_FILE', 'secrets/localhost.key')
        )
    )
