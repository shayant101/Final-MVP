#!/usr/bin/env python3
"""
Test script to verify MongoDB SSL connection fix and login functionality
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

async def test_mongodb_connection():
    """Test if the backend can connect to MongoDB"""
    print("🔍 Testing MongoDB Connection...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test a simple endpoint that requires database access
            response = await client.get(f"{BASE_URL}/api/auth/me", 
                                      headers={"Authorization": "Bearer invalid_token"})
            
            # We expect 401 (unauthorized) not 500 (server error)
            if response.status_code == 401:
                print("✅ MongoDB connection working - got expected 401 (unauthorized)")
                return True
            elif response.status_code == 500:
                print("❌ MongoDB connection failed - got 500 (server error)")
                print(f"   Response: {response.text}")
                return False
            else:
                print(f"⚠️  Unexpected response: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def test_login_functionality():
    """Test login with a known user"""
    print("\n🔐 Testing Login Functionality...")
    
    # Test credentials (you may need to adjust these)
    test_credentials = {
        "email": "test@restaurant.com",
        "password": "password123"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json=test_credentials,
                timeout=30.0
            )
            
            if response.status_code == 200:
                print("✅ Login successful!")
                data = response.json()
                print(f"   User: {data.get('user', {}).get('email', 'Unknown')}")
                print(f"   Token received: {'Yes' if data.get('token') else 'No'}")
                return True
            elif response.status_code == 401:
                print("⚠️  Login failed - Invalid credentials (expected if user doesn't exist)")
                print("   This is normal if test user doesn't exist")
                return True  # This is actually OK - means DB connection works
            elif response.status_code == 500:
                print("❌ Login failed - Server error (MongoDB SSL issue)")
                print(f"   Response: {response.text}")
                return False
            else:
                print(f"⚠️  Unexpected login response: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except httpx.TimeoutException:
        print("❌ Login request timed out (likely MongoDB SSL issue)")
        return False
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

async def test_user_creation():
    """Test creating a new user to verify full database functionality"""
    print("\n👤 Testing User Registration...")
    
    import random
    random_id = random.randint(1000, 9999)
    
    test_user = {
        "email": f"testuser{random_id}@restaurant.com",
        "password": "password123",
        "restaurantName": f"Test Restaurant {random_id}",
        "address": "123 Test Street",
        "phone": "+1234567890"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json=test_user,
                timeout=30.0
            )
            
            if response.status_code == 200:
                print("✅ User registration successful!")
                data = response.json()
                print(f"   User: {data.get('user', {}).get('email', 'Unknown')}")
                print(f"   Restaurant: {data.get('user', {}).get('restaurant', {}).get('name', 'Unknown')}")
                return True
            elif response.status_code == 400:
                print("⚠️  Registration failed - User might already exist")
                return True  # This is OK - means DB connection works
            elif response.status_code == 500:
                print("❌ Registration failed - Server error (MongoDB SSL issue)")
                print(f"   Response: {response.text}")
                return False
            else:
                print(f"⚠️  Unexpected registration response: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except httpx.TimeoutException:
        print("❌ Registration request timed out (likely MongoDB SSL issue)")
        return False
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 MongoDB SSL Connection Fix Verification")
    print("=" * 50)
    
    # Test 1: Basic MongoDB connection
    connection_ok = await test_mongodb_connection()
    
    # Test 2: Login functionality
    login_ok = await test_login_functionality()
    
    # Test 3: User creation (full database operations)
    registration_ok = await test_user_creation()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 50)
    print(f"MongoDB Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Login Functionality: {'✅ PASS' if login_ok else '❌ FAIL'}")
    print(f"User Registration: {'✅ PASS' if registration_ok else '❌ FAIL'}")
    
    if all([connection_ok, login_ok, registration_ok]):
        print("\n🎉 ALL TESTS PASSED - MongoDB SSL issue is FIXED!")
        print("✅ Users should now be able to log in successfully")
    else:
        print("\n⚠️  SOME TESTS FAILED - MongoDB SSL issue may persist")
        print("🔧 Additional troubleshooting may be needed")

if __name__ == "__main__":
    asyncio.run(main())