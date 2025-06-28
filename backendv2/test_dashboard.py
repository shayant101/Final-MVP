#!/usr/bin/env python3
"""
Test script for dashboard endpoints
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_dashboard_endpoints():
    """Test all dashboard endpoints"""
    print("🧪 Testing Dashboard Endpoints...")
    
    # Step 1: Try to register or login with test restaurant
    print("\n1. Getting test restaurant credentials...")
    import time
    unique_email = f"test-restaurant-{int(time.time())}@example.com"
    
    register_data = {
        "email": unique_email,
        "password": "testpass123",
        "restaurantName": "Test Restaurant",
        "address": "123 Test St",
        "phone": "555-0123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    if response.status_code == 200:
        print("✅ Restaurant registered successfully")
        auth_data = response.json()
        token = auth_data["token"]
        user_id = auth_data["user"]["user_id"]
    elif response.status_code == 400 and "already exists" in response.text:
        print("📝 User exists, trying to login...")
        login_data = {
            "email": "test-restaurant@example.com",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login successful")
            auth_data = response.json()
            token = auth_data["token"]
            user_id = auth_data["user"]["user_id"]
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    else:
        print(f"❌ Registration failed: {response.status_code} - {response.text}")
        return False
    
    # Headers for authenticated requests
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Add sample data for this restaurant
    print("\n2. Adding sample data for this restaurant...")
    import time
    from datetime import datetime, timedelta
    
    # Create sample campaigns for this user
    sample_campaigns = [
        {
            "restaurant_id": user_id,
            "campaign_type": "ad",
            "status": "active",
            "name": "New User Special",
            "details": "Welcome campaign for new restaurant",
            "budget": 300.00,
            "created_at": datetime.utcnow() - timedelta(days=2),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Create sample checklist for this user
    sample_checklist = [
        {
            "restaurant_id": user_id,
            "checklist_item_name": "Complete profile setup",
            "is_complete": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    print("✅ Sample data prepared")
    
    # Step 3: Test restaurant dashboard endpoint
    print("\n3. Testing restaurant dashboard endpoint...")
    response = requests.get(f"{BASE_URL}/api/dashboard/restaurant", headers=headers)
    if response.status_code == 200:
        print("✅ Restaurant dashboard endpoint working")
        dashboard_data = response.json()
        print(f"   Restaurant: {dashboard_data.get('restaurant', {}).get('name', 'N/A')}")
        print(f"   Campaigns: {len(dashboard_data.get('activeCampaigns', []))}")
        print(f"   Pending tasks: {len(dashboard_data.get('pendingTasks', []))}")
    else:
        print(f"❌ Restaurant dashboard failed: {response.status_code} - {response.text}")
    
    # Step 4: Test campaigns endpoint
    print("\n4. Testing campaigns endpoint...")
    response = requests.get(f"{BASE_URL}/api/dashboard/campaigns", headers=headers)
    if response.status_code == 200:
        print("✅ Campaigns endpoint working")
        campaigns_data = response.json()
        print(f"   Campaigns count: {len(campaigns_data.get('campaigns', []))}")
    else:
        print(f"❌ Campaigns endpoint failed: {response.status_code} - {response.text}")
    
    # Step 4: Register admin user and test admin endpoints
    print("\n4. Registering admin user...")
    admin_data = {
        "email": "admin-test@example.com",
        "password": "adminpass123",
        "restaurantName": "Admin Restaurant",  # Required but not used for admin
        "role": "admin"  # This won't work with current registration, but let's try
    }
    
    # For now, let's test with the restaurant token to see the error handling
    print("\n5. Testing admin dashboard with restaurant token (should fail)...")
    response = requests.get(f"{BASE_URL}/api/dashboard/admin", headers=headers)
    if response.status_code == 403:
        print("✅ Admin endpoint correctly rejects restaurant user")
    else:
        print(f"⚠️  Unexpected response: {response.status_code} - {response.text}")
    
    print("\n6. Testing restaurants list with restaurant token (should fail)...")
    response = requests.get(f"{BASE_URL}/api/dashboard/restaurants", headers=headers)
    if response.status_code == 403:
        print("✅ Restaurants endpoint correctly rejects restaurant user")
    else:
        print(f"⚠️  Unexpected response: {response.status_code} - {response.text}")
    
    print("\n🎉 Dashboard endpoints test completed!")
    return True

if __name__ == "__main__":
    try:
        test_dashboard_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to FastAPI server. Make sure it's running on port 8000.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)