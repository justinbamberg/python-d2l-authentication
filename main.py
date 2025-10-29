import os
from dotenv import load_dotenv
from d2l_auth import get_authenticated_session, authenticate

load_dotenv()
API_BASE = os.getenv("D2L_API_BASE")

def whoami():
    try:
        session = get_authenticated_session()
    except Exception:
        print("⚠️  No valid token found, re-authenticating...")
        authenticate()
        session = get_authenticated_session()

    version = "1.52"
    response = session.get(f"{API_BASE}/lp/{version}/whoami")
    if response.status_code == 200:
        data = response.json()
        print("\n👤 User Information:")
        print(f"ID: {data['Identifier']}")
        print(f"Name: {data['FirstName']} {data['LastName']}")
        print(f"Username: {data['UniqueName']}")
        print(f"Pronouns: {data.get('Pronouns', 'Not set')}")
    else:
        print("❌ Failed to fetch WhoAmI:", response.status_code, response.text)

if __name__ == "__main__":
    whoami()
