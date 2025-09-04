import requests
import json

# Define the base URL for the API
API_BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{API_BASE_URL}/auth/login"

# --- IMPORTANT ---
# Replace with valid credentials for a test user
# You can create a test user by running:
# python backendv2/create_admin.py --email your_email@example.com --password your_password
TEST_USER_EMAIL = "your_email@example.com"
TEST_USER_PASSWORD = "your_password"

def get_auth_token():
    """
    Logs in a test user and retrieves a valid JWT token.
    """
    if TEST_USER_EMAIL == "your_email@example.com" or TEST_USER_PASSWORD == "your_password":
        print("👉 Please update the TEST_USER_EMAIL and TEST_USER_PASSWORD in the script.")
        return None

    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        
        if response.ok:
            token_data = response.json()
            print("✅ Login successful!")
            print("Access Token:", token_data.get("access_token"))
            return token_data.get("access_token")
        else:
            print("❌ Login failed.")
            print("Status Code:", response.status_code)
            print("Response Text:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    get_auth_token()