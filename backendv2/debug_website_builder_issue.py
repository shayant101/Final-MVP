#!/usr/bin/env python3
"""
Debug script to systematically test the website builder issue
"""
import asyncio
import sys
import os
sys.path.append('.')

from app.database import connect_to_mongo, db
from app.services.dashboard_service import DashboardService
from app.routes.website_builder import _get_restaurant_data
from app.auth import TokenData

async def debug_website_builder():
    """Systematically debug the website builder issue"""
    print("🔍 DEBUGGING WEBSITE BUILDER ISSUE")
    print("=" * 50)
    
    try:
        # Step 1: Connect to database
        print("1. Connecting to database...")
        await connect_to_mongo()
        print("✅ Database connected")
        
        # Step 2: Check restaurants in database
        print("\n2. Checking restaurants in database...")
        restaurants = await db.database.restaurants.find({}).to_list(length=10)
        print(f"Found {len(restaurants)} restaurants:")
        
        for i, restaurant in enumerate(restaurants):
            print(f"  Restaurant {i+1}:")
            print(f"    _id: {restaurant.get('_id')}")
            print(f"    user_id: {restaurant.get('user_id')}")
            print(f"    name: {restaurant.get('name', 'No name')}")
            print(f"    user_id type: {type(restaurant.get('user_id'))}")
            print()
        
        if not restaurants:
            print("❌ NO RESTAURANTS FOUND IN DATABASE!")
            print("This is likely the root cause of the issue.")
            return
        
        # Step 3: Test dashboard service with first restaurant
        test_restaurant = restaurants[0]
        restaurant_id = str(test_restaurant['_id'])
        user_id = test_restaurant.get('user_id')
        
        print(f"3. Testing dashboard service with restaurant_id: {restaurant_id}")
        try:
            dashboard_data = await DashboardService.get_restaurant_dashboard_data(restaurant_id)
            print("✅ Dashboard service works!")
            print("Dashboard data structure:")
            print(f"  restaurant.restaurant_id: {dashboard_data.get('restaurant', {}).get('restaurant_id')}")
            print(f"  restaurant.user_id: {dashboard_data.get('restaurant', {}).get('user_id')}")
            print(f"  restaurant.name: {dashboard_data.get('restaurant', {}).get('name')}")
        except Exception as e:
            print(f"❌ Dashboard service failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Step 4: Test _get_restaurant_data function directly
        print(f"\n4. Testing _get_restaurant_data function...")
        
        # Create a mock user token
        mock_user = TokenData(user_id=user_id, email="test@example.com", role="restaurant")
        
        try:
            restaurant_data = await _get_restaurant_data(restaurant_id, mock_user, db)
            if restaurant_data:
                print("✅ _get_restaurant_data works!")
                print(f"  Returned restaurant_id: {restaurant_data.get('restaurant_id')}")
                print(f"  Returned name: {restaurant_data.get('name')}")
            else:
                print("❌ _get_restaurant_data returned None")
        except Exception as e:
            print(f"❌ _get_restaurant_data failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Step 5: Test with wrong user_id (access control)
        print(f"\n5. Testing access control with wrong user_id...")
        wrong_user = TokenData(user_id="wrong_user_id", email="wrong@example.com", role="restaurant")
        
        try:
            restaurant_data = await _get_restaurant_data(restaurant_id, wrong_user, db)
            if restaurant_data:
                print("❌ Access control failed - should have returned None")
            else:
                print("✅ Access control works - correctly returned None")
        except Exception as e:
            print(f"Access control test error: {e}")
        
        # Step 6: Check users collection
        print(f"\n6. Checking users collection...")
        users = await db.database.users.find({}).to_list(length=10)
        print(f"Found {len(users)} users:")
        
        for i, user in enumerate(users):
            print(f"  User {i+1}:")
            print(f"    _id: {user.get('_id')}")
            print(f"    email: {user.get('email')}")
            print(f"    role: {user.get('role')}")
            print()
        
        # Step 7: Check for user-restaurant relationship issues
        print(f"\n7. Checking user-restaurant relationships...")
        for restaurant in restaurants:
            restaurant_user_id = restaurant.get('user_id')
            print(f"Restaurant '{restaurant.get('name')}' has user_id: {restaurant_user_id}")
            
            # Try to find corresponding user
            if restaurant_user_id:
                try:
                    from bson import ObjectId
                    # Try as ObjectId first
                    user = await db.database.users.find_one({"_id": ObjectId(restaurant_user_id)})
                    if not user:
                        # Try as string
                        user = await db.database.users.find_one({"_id": restaurant_user_id})
                    
                    if user:
                        print(f"  ✅ Found corresponding user: {user.get('email')}")
                    else:
                        print(f"  ❌ No corresponding user found for user_id: {restaurant_user_id}")
                except Exception as e:
                    print(f"  ❌ Error finding user: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 DIAGNOSIS COMPLETE")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_website_builder())