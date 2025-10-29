# D2L OAuth WhoAmI Python Example

This project demonstrates authenticating to D2L Brightspace using OAuth 2.0 and retrieving user information from the `/whoami` endpoint.

## 🚀 Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/YOURNAME/d2l-oauth-whoami.git
   cd d2l-oauth-whoami
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your D2L credentials:
   ```bash
   cp .env.example .env
   ```

4. Run:
   ```bash
   python main.py
   ```

Follow the printed authorization link, paste the redirect URL, and view your D2L profile data!
