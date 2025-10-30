import os, ssl, json, secrets, base64, hashlib, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs
from pathlib import Path
import requests, keyring

# ====== CONFIG ======
BRIGHTSPACE_ROOT = os.getenv("D2L_ROOT", "https://elearning.delta.edu")
AUTH_BASE        = os.getenv("D2L_AUTH_BASE", "https://auth.brightspace.com")
AUTHZ_URL        = f"{AUTH_BASE}/oauth2/auth"
TOKEN_URL        = f"{AUTH_BASE}/core/connect/token"


CLIENT_ID        = os.getenv("D2L_CLIENT_ID", "<d2L-client>")   # from D2L OAuth app
CLIENT_SECRET    = os.getenv("D2L_CLIENT_SECRET", "")
SCOPES           = os.getenv("D2L_SCOPES", "core:*:* users:userdata:read")
REDIRECT_URI     = os.getenv("D2L_REDIRECT_URI", "https://localhost:3001/callback")
CERT_FILE        = os.getenv("TLS_CERT_FILE", "localhost+2.pem")
KEY_FILE         = os.getenv("TLS_KEY_FILE", "localhost+2-key.pem")
APP_NAME         = os.getenv("APP_NAME", "d2l-desktop-automation")

# ====== STORAGE ======
def save_tokens(data: dict):
    if "refresh_token" in data and data["refresh_token"]:
        keyring.set_password(APP_NAME, "refresh_token", data["refresh_token"])
    support = Path.home() / "Library" / "Application Support" / APP_NAME
    support.mkdir(parents=True, exist_ok=True)
    with open(support / "session.json", "w") as f:
        json.dump(data, f, indent=2)

def load_refresh_token():
    return keyring.get_password(APP_NAME, "refresh_token")

# ====== PKCE ======
def make_pkce():
    verifier  = base64.urlsafe_b64encode(os.urandom(40)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    return verifier, challenge

# ====== HTTPS CALLBACK SERVER ======
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlparse(self.path).path != urlparse(REDIRECT_URI).path:
            self.send_error(404); return
        qs = parse_qs(urlparse(self.path).query)
        if "error" in qs:
            self.send_response(400); self.end_headers()
            self.wfile.write(b"Authorization error.")
            self.server.auth_code = None
            return
        self.server.auth_code = qs.get("code", [None])[0]
        self.send_response(200); self.end_headers()
        self.wfile.write(b"You can close this window and return to the app.")

def wait_for_auth_code():
    # Ensure local TLS certs exist; provide guidance if missing
    if not Path(CERT_FILE).exists() or not Path(KEY_FILE).exists():
        print("Missing TLS certificate or key for localhost.")
        print("If you're on macOS, install mkcert and generate trusted certs:")
        print("  brew install mkcert nss")
        print("  mkcert -install")
        print(f"  mkcert -key-file {KEY_FILE} -cert-file {CERT_FILE} localhost 127.0.0.1 ::1")
        raise SystemExit(1)
    httpd = HTTPServer(("localhost", urlparse(REDIRECT_URI).port or 3001), Handler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT_FILE, KEY_FILE)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    while getattr(httpd, "auth_code", None) is None:
        httpd.handle_request()
    return httpd.auth_code

# ====== TOKEN EXCHANGE / REFRESH ======
def token_request(data: dict):
    headers = {"Accept": "application/json"}
    auth = (CLIENT_ID, CLIENT_SECRET) if CLIENT_SECRET else None
    resp = requests.post(TOKEN_URL, data=data, headers=headers, auth=auth, timeout=30)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        details = None
        try:
            details = resp.json()
        except Exception:
            details = resp.text
        print("Token request failed:")
        print(f"  Status: {resp.status_code}")
        print(f"  Body:   {details}")
        raise e
    return resp.json()

def exchange_code_for_tokens(code: str, verifier: str):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
        "client_id": CLIENT_ID,
    }
    tokens = token_request(data)
    save_tokens(tokens)
    return tokens["access_token"]

def refresh_access_token():
    rt = load_refresh_token()
    if not rt:
        return None
    data = {
        "grant_type": "refresh_token",
        "refresh_token": rt,
        "client_id": CLIENT_ID,
    }
    try:
        tokens = token_request(data)
        save_tokens(tokens)
        return tokens["access_token"]
    except requests.HTTPError:
        return None

def get_access_token():
    # try refresh first
    tok = refresh_access_token()
    if tok:
        return tok
    # if no refresh token, launch browser
    verifier, challenge = make_pkce()
    state = secrets.token_urlsafe(16)
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
        "code_challenge_method": "S256",
        "code_challenge": challenge,
    }
    auth_url = AUTHZ_URL + "?" + urlencode(params)
    print("🌐 Opening browser for D2L login...")
    webbrowser.open(auth_url)
    code = wait_for_auth_code()
    return exchange_code_for_tokens(code, verifier)

# ====== API CALL ======
def d2l_get(path: str):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BRIGHTSPACE_ROOT}{path}"
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code == 401:
        token = get_access_token()
        headers["Authorization"] = f"Bearer {token}"
        r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

# ====== MAIN ======
if __name__ == "__main__":
    me = d2l_get("/d2l/api/lp/1.43/users/whoami")
    print("\n✅ Connected to Brightspace!")
    print(f"👤 {me.get('FirstName')} {me.get('LastName')} ({me.get('UniqueName')})")
