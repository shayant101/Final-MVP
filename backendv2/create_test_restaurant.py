#!/usr/bin/env python3.9
"""
Create Test Restaurant User Script
Creates a sample restaurant user for testing the Python backend
"""
import asyncio
from datetime import datetime
from app.database import connect_to_mongo, get_users_collection, get_restaurants_collection
from app.auth import get_password_hash
from app.models import UserRole

async def create_test_restaurant():
    """Create test restaurant user"""
    print("🔧 Creating test restaurant user...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Get collections
    users_collection = get_users_collection()
    restaurants_collection = get_restaurants_collection()
    
    # Check if test restaurant already exists
    existing_user = await users_collection.find_one({"email": "test@restaurant.com"})
    if existing_user:
        print("✅ Test restaurant user already exists")
        print(f"📧 Email: test@restaurant.com")
        print(f"🔑 Password: test123")
        return
    
    # Create restaurant user
    user_data = {
        "email": "test@restaurant.com",
        "password_hash": get_password_hash("test123"),
        "role": UserRole.restaurant,
        "created_at": datetime.utcnow()
    }
    
    # Insert user
    user_result = await users_collection.insert_one(user_data)
    user_id = str(user_result.inserted_id)
    
    # Create restaurant document
    restaurant_data = {
        "user_id": user_id,
        "name": "Mario's Italian Bistro",
        "address": "123 Main Street, Downtown",
        "phone": "(555) 123-4567",
        "created_at": datetime.utcnow()
    }
    
    # Insert restaurant
    restaurant_result = await restaurants_collection.insert_one(restaurant_data)
    restaurant_id = str(restaurant_result.inserted_id)
    
    print("✅ Test restaurant user created successfully!")
    print(f"📧 Email: test@restaurant.com")
    print(f"🔑 Password: test123")
    print(f"🏪 Restaurant: Mario's Italian Bistro")
    print(f"🆔 User ID: {user_id}")
    print(f"🆔 Restaurant ID: {restaurant_id}")
    print("\n🎉 You can now login as a restaurant user!")

if __name__ == "__main__":
    asyncio.run(create_test_restaurant())