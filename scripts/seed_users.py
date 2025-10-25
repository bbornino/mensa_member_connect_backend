import json
import requests

# Load your users JSON file
with open("users.json", "r") as f:
    users = json.load(f)

API_BASE_URL = "http://localhost:8000/api/"
REGISTER_ENDPOINT = f"{API_BASE_URL}users/register/"

for user in users:
    try:
        # Only send the required fields your backend expects
        payload = {
            "username": user["username"],
            "email": user["email"],
            "password": user["password"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
        }
        response = requests.post(REGISTER_ENDPOINT, json=payload)

        if response.status_code == 201:
            print(f"✅ Created {user['username']}")
        else:
            print(f"❌ Failed {user['username']}: {response.json()}")
    except Exception as e:
        print(f"⚠️ Error for {user['username']}: {e}")
