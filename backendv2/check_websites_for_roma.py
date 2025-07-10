#!/usr/bin/env python3
"""
Check websites for Roma Trattoria account
"""
import asyncio
from app.database import connect_to_mongo, get_users_collection, get_restaurants_collection
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def check_roma_websites():
    """Check websites for Roma Trattoria"""
    
    print("🔍 CHECKING ROMA TRATTORIA WEBSITES")
    print("=" * 50)
    
    try:
        await connect_to_mongo()
        
        # Get database connection
        client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
        db = client.momentum_growth
        
        users_collection = get_users_collection()
        restaurants_collection = get_restaurants_collection()
        websites_collection = db.websites
        
        # Find Roma Trattoria user
        print("1️⃣ Finding Roma Trattoria user...")
        user = await users_collection.find_one({"email": "romatrattoria@yahoo.com"})
        
        if not user:
            print("❌ Roma Trattoria user not found!")
            return
        
        user_id = str(user["_id"])
        print(f"✅ Found user: {user['email']} (ID: {user_id})")
        
        # Find restaurant
        print("\n2️⃣ Finding restaurant...")
        restaurant = await restaurants_collection.find_one({"user_id": user_id})
        
        if not restaurant:
            print("❌ Restaurant not found!")
            return
        
        restaurant_id = str(restaurant["_id"])
        print(f"✅ Found restaurant: {restaurant['name']} (ID: {restaurant_id})")
        
        # Check websites
        print("\n3️⃣ Checking websites...")
        
        # Check by user_id
        websites_by_user = []
        async for website in websites_collection.find({"user_id": user_id}):
            websites_by_user.append(website)
        
        # Check by restaurant_id
        websites_by_restaurant = []
        async for website in websites_collection.find({"restaurant_id": restaurant_id}):
            websites_by_restaurant.append(website)
        
        print(f"📊 Websites found by user_id: {len(websites_by_user)}")
        print(f"📊 Websites found by restaurant_id: {len(websites_by_restaurant)}")
        
        # Show all websites
        all_websites = websites_by_user + websites_by_restaurant
        unique_websites = {w["_id"]: w for w in all_websites}.values()
        
        print(f"\n🌐 TOTAL UNIQUE WEBSITES: {len(unique_websites)}")
        
        for i, website in enumerate(unique_websites, 1):
            print(f"\nWebsite {i}:")
            print(f"   ID: {website.get('_id')}")
            print(f"   Name: {website.get('name', 'Unnamed')}")
            print(f"   User ID: {website.get('user_id')}")
            print(f"   Restaurant ID: {website.get('restaurant_id')}")
            print(f"   Created: {website.get('created_at')}")
            print(f"   Status: {website.get('status', 'Unknown')}")
        
        # Check all websites in database
        print(f"\n4️⃣ Checking ALL websites in database...")
        all_websites_count = await websites_collection.count_documents({})
        print(f"📊 Total websites in database: {all_websites_count}")
        
        if all_websites_count > 0:
            print("\nAll websites:")
            async for website in websites_collection.find({}):
                print(f"   - {website.get('name', 'Unnamed')} (User: {website.get('user_id')}, Restaurant: {website.get('restaurant_id')})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_roma_websites())