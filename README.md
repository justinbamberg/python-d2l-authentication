## D2L WhoAmI Local Starter (Python)

Authenticate against Brightspace (D2L) using OAuth 2.0 with PKCE, then call WhoAmI:
`GET /d2l/api/lp/1.43/users/whoami`.

### What this includes
- OAuth 2.0 Authorization Code + PKCE flow with optional client secret support
- Secure refresh token storage via `keyring` (macOS Keychain; Windows Credential Manager)
- Local HTTPS callback server on `https://localhost:3001/callback` using mkcert certs

---

## 1) Create a D2L OAuth 2.0 client
In your Brightspace tenant, create an OAuth 2 client (App):
- Redirect URI: `https://localhost:3001/callback`
- Scopes: `core:*:* users:userdata:read`
- Copy the Client ID (and Client Secret if the client is confidential)

Note: This app uses PKCE; a client secret is not required for public clients. If your client is confidential, set `D2L_CLIENT_SECRET` and the app will authenticate using HTTP Basic to the token endpoint.

---

## 2) Install prerequisites

### macOS
- Python 3.10+
- mkcert for local trusted certs

Install mkcert and generate localhost certs:
```bash
brew install mkcert nss
mkcert -install
cd /Users/justinbamberg/Desktop/whoami_python_d2L
mkcert -key-file localhost+2-key.pem -cert-file localhost+2.pem localhost 127.0.0.1 ::1
```

### Windows
- Python 3.10+
- mkcert for local trusted certs (Chocolatey recommended)

Install mkcert and generate localhost certs (PowerShell as Admin):
```powershell
choco install mkcert -y
mkcert -install
cd C:\\path\\to\\whoami_python_d2L
mkcert -key-file localhost+2-key.pem -cert-file localhost+2.pem localhost 127.0.0.1 ::1
```

---

## 3) Configure environment variables

You can set environment variables (defaults shown). Minimum required: `D2L_ROOT`, `D2L_CLIENT_ID`, `D2L_REDIRECT_URI`.

### macOS (zsh/bash)
```bash
export D2L_ROOT="https://elearning.delta.edu"     # Your Brightspace base URL
export D2L_AUTH_BASE="https://auth.brightspace.com"
export D2L_CLIENT_ID="<your-client-id>"
# export D2L_CLIENT_SECRET=""                      # Only for confidential clients
export D2L_SCOPES="core:*:* users:userdata:read"
export D2L_REDIRECT_URI="https://localhost:3001/callback"
# Optional overrides if you named certs differently
# export TLS_CERT_FILE="localhost+2.pem"
# export TLS_KEY_FILE="localhost+2-key.pem"
```

### Windows (PowerShell)
```powershell
$env:D2L_ROOT = "https://elearning.delta.edu"
$env:D2L_AUTH_BASE = "https://auth.brightspace.com"
$env:D2L_CLIENT_ID = "<your-client-id>"
# $env:D2L_CLIENT_SECRET = ""                      # Only for confidential clients
$env:D2L_SCOPES = "core:*:* users:userdata:read"
$env:D2L_REDIRECT_URI = "https://localhost:3001/callback"
# Optional overrides
# $env:TLS_CERT_FILE = "localhost+2.pem"
# $env:TLS_KEY_FILE = "localhost+2-key.pem"
```

Refresh tokens are stored securely by `keyring` (macOS Keychain or Windows Credential Manager) under service name `d2l-desktop-automation`.

---

## 4) Install and run

### macOS / Windows (same commands)
```bash
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

What happens:
1) Browser opens for Brightspace login/consent.
2) OAuth redirect hits `https://localhost:3001/callback`.
3) App calls `GET /d2l/api/lp/1.43/users/whoami` and prints your user info.

---

## 5) Troubleshooting

- Missing TLS certs/keys
  - The app will print instructions. Re-run mkcert commands and try again.

- 400 unauthorized_client: Must authenticate either via Authorization header or body, not both
  - Ensure you did NOT set both a client secret in env AND include it in the POST body. This app uses HTTP Basic automatically when `D2L_CLIENT_SECRET` is set and does not put it in the body.

- invalid_grant
  - Most common causes: Redirect URI mismatch, or the `code_verifier`/PKCE not matching the `code_challenge` for this authorization.
  - Ensure your OAuth client’s Redirect URI exactly matches `D2L_REDIRECT_URI`.

- 401 on API call
  - Token expired or missing scope. App will refresh if a refresh token exists. Verify `D2L_SCOPES` includes `users:userdata:read`.

---

## 6) Publish to GitHub

1) Create a new empty repository on GitHub (no README/License yet)
2) Initialize git and push:
```bash
cd /path/to/whoami_python_d2L
git init
git add .
git commit -m "Initial commit: D2L WhoAmI local starter"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Safe sharing tips:
- Do not commit secrets. This repo includes a `.gitignore` that excludes `.venv/` and `*.pem` certs.
- Verify no secrets are in history before making the repository public.

---

## Configuration reference

- D2L_ROOT: Brightspace root URL (e.g., `https://yourtenant.brightspace.com`)
- D2L_AUTH_BASE: D2L Auth root (`https://auth.brightspace.com`)
- D2L_CLIENT_ID: Your OAuth client ID
- D2L_CLIENT_SECRET: Optional; only for confidential clients
- D2L_SCOPES: Default `core:*:* users:userdata:read`
- D2L_REDIRECT_URI: Default `https://localhost:3001/callback`
- TLS_CERT_FILE / TLS_KEY_FILE: Local cert file names (mkcert)

---

## D2L OAuth app setup (with screenshots)
See: [docs/D2L-OAuth-Setup.md](docs/D2L-OAuth-Setup.md)

Add your screenshots to:
- `docs/img/register-application.png`
- `docs/img/application-details.png`

---

## License
Choose and add a license (e.g., MIT) if you intend to open-source. If internal only, omit.

