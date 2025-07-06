#!/usr/bin/env python3
"""
Investigate Restaurant Data Discrepancy
Check why we see 10 restaurants instead of expected 25
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import connect_to_mongo, get_database

async def investigate_restaurants():
    """Investigate the restaurant data discrepancy"""
    print("🔍 COMPREHENSIVE RESTAURANT DATABASE ANALYSIS")
    print("=" * 60)
    
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        print("✅ Connected to database")
        
        # Count all restaurants
        total_restaurants = await db.restaurants.count_documents({})
        print(f"📊 Total restaurants in database: {total_restaurants}")
        
        # Count restaurants with user_id
        restaurants_with_users = await db.restaurants.count_documents({"user_id": {"$exists": True, "$ne": None}})
        print(f"👥 Restaurants with user_id: {restaurants_with_users}")
        
        # Count restaurants without user_id
        restaurants_without_users = await db.restaurants.count_documents({"user_id": {"$exists": False}})
        orphaned_restaurants = await db.restaurants.count_documents({"user_id": None})
        print(f"🚫 Restaurants without user_id field: {restaurants_without_users}")
        print(f"🚫 Restaurants with null user_id: {orphaned_restaurants}")
        
        # Show sample of restaurants without users
        print("\n📋 RESTAURANTS WITHOUT USER_ID:")
        print("-" * 40)
        orphaned = await db.restaurants.find({"$or": [{"user_id": {"$exists": False}}, {"user_id": None}]}).limit(10).to_list(length=10)
        for i, restaurant in enumerate(orphaned, 1):
            print(f"{i:2d}. {restaurant.get('name', 'Unknown'):30s} (ID: {restaurant['_id']})")
        
        # Show sample of restaurants with users
        print("\n✅ RESTAURANTS WITH USER_ID:")
        print("-" * 40)
        with_users = await db.restaurants.find({"user_id": {"$exists": True, "$ne": None}}).limit(10).to_list(length=10)
        for i, restaurant in enumerate(with_users, 1):
            print(f"{i:2d}. {restaurant.get('name', 'Unknown'):30s} (ID: {restaurant['_id']}, User: {restaurant.get('user_id')})")
        
        # Count total users
        total_users = await db.users.count_documents({})
        print(f"\n👤 Total users in database: {total_users}")
        
        # Show user details
        print("\n👥 USER DETAILS:")
        print("-" * 40)
        users = await db.users.find({}).limit(10).to_list(length=10)
        for i, user in enumerate(users, 1):
            print(f"{i:2d}. {user.get('email', 'No email'):30s} (ID: {user['_id']})")
        
        # Check if there are restaurants with string user_ids vs ObjectId user_ids
        print("\n🔍 USER_ID TYPE ANALYSIS:")
        print("-" * 40)
        sample_restaurants = await db.restaurants.find({"user_id": {"$exists": True, "$ne": None}}).limit(5).to_list(length=5)
        for restaurant in sample_restaurants:
            user_id = restaurant.get('user_id')
            print(f"Restaurant: {restaurant.get('name'):20s} | User ID: {user_id} | Type: {type(user_id).__name__}")
        
        # Check for data integrity issues
        print("\n🔧 DATA INTEGRITY CHECK:")
        print("-" * 40)
        
        # Find restaurants with user_ids that don't match any users
        restaurant_user_ids = await db.restaurants.distinct("user_id", {"user_id": {"$exists": True, "$ne": None}})
        user_ids = await db.users.distinct("_id")
        
        print(f"Unique user_ids in restaurants: {len(restaurant_user_ids)}")
        print(f"Unique user _ids in users: {len(user_ids)}")
        
        # Convert to strings for comparison
        restaurant_user_ids_str = [str(uid) for uid in restaurant_user_ids if uid is not None]
        user_ids_str = [str(uid) for uid in user_ids]
        
        orphaned_user_ids = set(restaurant_user_ids_str) - set(user_ids_str)
        if orphaned_user_ids:
            print(f"⚠️  Restaurants with non-existent user_ids: {len(orphaned_user_ids)}")
            for uid in list(orphaned_user_ids)[:5]:
                print(f"   - {uid}")
        else:
            print("✅ All restaurant user_ids match existing users")
            
    except Exception as e:
        print(f"❌ Investigation failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(investigate_restaurants())