#!/usr/bin/env python3.9
"""
Fix Restaurant Password Hash Script
Recreates the test restaurant user with proper bcrypt password hash
"""
import asyncio
from datetime import datetime
from app.database import connect_to_mongo, get_users_collection, get_restaurants_collection
from app.auth import get_password_hash
from app.models import UserRole

async def fix_restaurant_password():
    """Fix test restaurant user password hash"""
    print("🔧 Fixing test restaurant user password hash...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Get collections
    users_collection = get_users_collection()
    restaurants_collection = get_restaurants_collection()
    
    # Find existing test restaurant user
    existing_user = await users_collection.find_one({"email": "test@restaurant.com"})
    if not existing_user:
        print("❌ Test restaurant user not found!")
        return
    
    print(f"📧 Found user: test@restaurant.com")
    print(f"🆔 User ID: {str(existing_user['_id'])}")
    
    # Generate new bcrypt hash for password "test123"
    new_password_hash = get_password_hash("test123")
    print(f"🔐 Generated new bcrypt hash")
    
    # Update the user's password hash
    result = await users_collection.update_one(
        {"email": "test@restaurant.com"},
        {"$set": {"password_hash": new_password_hash}}
    )
    
    if result.modified_count > 0:
        print("✅ Password hash updated successfully!")
        print(f"📧 Email: test@restaurant.com")
        print(f"🔑 Password: test123")
        print("\n🎉 Restaurant login should now work!")
    else:
        print("❌ Failed to update password hash")

if __name__ == "__main__":
    asyncio.run(fix_restaurant_password())