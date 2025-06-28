#!/usr/bin/env python3.9
"""
Debug Restaurant Login Script
Check the current state of the test restaurant user and verify login
"""
import asyncio
from datetime import datetime
from app.database import connect_to_mongo, get_users_collection, get_restaurants_collection
from app.auth import get_password_hash, verify_password
from app.models import UserRole

async def debug_restaurant_login():
    """Debug test restaurant user login"""
    print("🔍 Debugging restaurant login...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Get collections
    users_collection = get_users_collection()
    restaurants_collection = get_restaurants_collection()
    
    # Find test restaurant user
    user_doc = await users_collection.find_one({"email": "test@restaurant.com"})
    if not user_doc:
        print("❌ Test restaurant user not found!")
        return
    
    print(f"✅ Found user: test@restaurant.com")
    print(f"🆔 User ID: {str(user_doc['_id'])}")
    print(f"👤 Role: {user_doc['role']}")
    print(f"🔐 Password Hash: {user_doc['password_hash'][:50]}...")
    
    # Test password verification
    test_password = "test123"
    try:
        is_valid = verify_password(test_password, user_doc["password_hash"])
        print(f"🔑 Password verification for '{test_password}': {'✅ VALID' if is_valid else '❌ INVALID'}")
    except Exception as e:
        print(f"❌ Password verification error: {e}")
    
    # Check restaurant document
    restaurant_doc = await restaurants_collection.find_one({"user_id": str(user_doc["_id"])})
    if restaurant_doc:
        print(f"🏪 Restaurant found: {restaurant_doc['name']}")
        print(f"🆔 Restaurant ID: {str(restaurant_doc['_id'])}")
    else:
        print("❌ No restaurant document found for this user!")
    
    # Test with a fresh hash
    print("\n🔄 Testing fresh password hash generation...")
    fresh_hash = get_password_hash("test123")
    print(f"🔐 Fresh hash: {fresh_hash[:50]}...")
    
    try:
        fresh_verify = verify_password("test123", fresh_hash)
        print(f"🔑 Fresh hash verification: {'✅ VALID' if fresh_verify else '❌ INVALID'}")
    except Exception as e:
        print(f"❌ Fresh hash verification error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_restaurant_login())