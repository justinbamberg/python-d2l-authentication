import os
import json
import webbrowser
from urllib.parse import urlencode
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("D2L_CLIENT_ID")
CLIENT_SECRET = os.getenv("D2L_CLIENT_SECRET")
REDIRECT_URI = os.getenv("D2L_REDIRECT_URI")
AUTH_URL = os.getenv("D2L_AUTH_URL")
TOKEN_URL = os.getenv("D2L_TOKEN_URL")

TOKEN_FILE = "token.json"

def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            token = json.load(f)
            return token
    return None

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f)

def authenticate():
    d2l = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=["*"])
    auth_url, state = d2l.authorization_url(AUTH_URL)

    print(f"🔗 Visit this URL to authorize: {auth_url}")
    webbrowser.open(auth_url)
    redirect_response = input("Paste the full redirect URL after login: ").strip()

    token = d2l.fetch_token(
        TOKEN_URL,
        authorization_response=redirect_response,
        client_secret=CLIENT_SECRET
    )
    save_token(token)
    print("✅ Token saved successfully!")
    return token

def get_authenticated_session():
    token = get_token()
    d2l = OAuth2Session(CLIENT_ID, token=token, auto_refresh_url=TOKEN_URL,
                        auto_refresh_kwargs={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET},
                        token_updater=save_token)
    return d2l
