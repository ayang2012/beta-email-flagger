import os
from flask import Flask, request, redirect, url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

app = Flask(__name__)

# Load client secrets from the secure directory
CLIENT_SECRETS_FILE = os.environ.get('CLIENT_SECRETS_FILE', 'secrets/credentials.json')
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
    return 'Authorization successful!'

if __name__ == '__main__':
    app.run(
        debug=True,
        ssl_context=(
            os.environ.get('SSL_CERT_FILE', 'secrets/localhost.crt'),
            os.environ.get('SSL_KEY_FILE', 'secrets/localhost.key')
        )
    )
