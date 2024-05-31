import os
from flask import Flask, redirect, url_for
from utils.auth import authorize, callback
from utils.gmail import test_fetch_emails

app = Flask(__name__)

# Load client secrets from the secure directory
CLIENT_SECRETS_FILE = os.environ.get("CLIENT_SECRETS_FILE", "secrets/credentials.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


@app.route("/")
def index():
    return redirect(url_for("authorize"))


@app.route("/authorize")
def authorize_route():
    return authorize()


@app.route("/callback")
def callback_route():
    return callback()


@app.route("/test_fetch_emails")
def test_fetch_emails_route():
    return test_fetch_emails()


if __name__ == "__main__":
    app.run(
        debug=True,
        ssl_context=(
            os.environ.get("SSL_CERT_FILE", "secrets/localhost.crt"),
            os.environ.get("SSL_KEY_FILE", "secrets/localhost.key"),
        ),
    )
