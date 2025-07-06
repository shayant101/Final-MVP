#!/usr/bin/env python3
"""
Simple debug script to test database and restaurant data
"""
import asyncio
import sys
import os
sys.path.append('.')

from app.database import connect_to_mongo, db
from bson import ObjectId

async def debug_simple():
    """Simple debug of database and restaurant data"""
    print("🔍 SIMPLE DATABASE DEBUG")
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
            
            # Check if we need to create test data
            print("\n3. Checking users collection...")
            users = await db.database.users.find({}).to_list(length=10)
            print(f"Found {len(users)} users:")
            
            for i, user in enumerate(users):
                print(f"  User {i+1}:")
                print(f"    _id: {user.get('_id')}")
                print(f"    email: {user.get('email')}")
                print(f"    role: {user.get('role')}")
                print()
            
            if users:
                print("\n4. Users exist but no restaurants - this is the problem!")
                print("The website builder expects restaurants to exist for users.")
                
                # Let's create a test restaurant for the first user
                test_user = users[0]
                user_id = str(test_user['_id'])
                
                print(f"\n5. Creating test restaurant for user: {test_user.get('email')}")
                
                test_restaurant = {
                    "user_id": user_id,
                    "name": "Debug Test Restaurant",
                    "cuisine_type": "American",
                    "address": "123 Test Street, Debug City",
                    "phone": "(555) 123-4567",
                    "price_range": "moderate",
                    "created_at": "2024-01-01T00:00:00Z"
                }
                
                result = await db.database.restaurants.insert_one(test_restaurant)
                print(f"✅ Created test restaurant with ID: {result.inserted_id}")
                
                # Verify the restaurant was created
                created_restaurant = await db.database.restaurants.find_one({"_id": result.inserted_id})
                print(f"✅ Verified restaurant creation:")
                print(f"    _id: {created_restaurant.get('_id')}")
                print(f"    user_id: {created_restaurant.get('user_id')}")
                print(f"    name: {created_restaurant.get('name')}")
            
            return
        
        # Step 3: Test restaurant access logic
        test_restaurant = restaurants[0]
        restaurant_id = str(test_restaurant['_id'])
        user_id = test_restaurant.get('user_id')
        
        print(f"3. Testing restaurant access logic...")
        print(f"   Restaurant ID: {restaurant_id}")
        print(f"   User ID: {user_id}")
        
        # Test ObjectId conversion
        try:
            restaurant_object_id = ObjectId(restaurant_id)
            print(f"   ✅ ObjectId conversion successful: {restaurant_object_id}")
        except Exception as e:
            print(f"   ❌ ObjectId conversion failed: {e}")
        
        # Test restaurant lookup
        try:
            found_restaurant = await db.database.restaurants.find_one({"_id": ObjectId(restaurant_id)})
            if found_restaurant:
                print(f"   ✅ Restaurant lookup successful")
                print(f"   Found restaurant user_id: {found_restaurant.get('user_id')}")
                print(f"   User ID match: {found_restaurant.get('user_id') == user_id}")
            else:
                print(f"   ❌ Restaurant lookup failed - not found")
        except Exception as e:
            print(f"   ❌ Restaurant lookup error: {e}")
        
        # Step 4: Check users collection
        print(f"\n4. Checking users collection...")
        users = await db.database.users.find({}).to_list(length=10)
        print(f"Found {len(users)} users:")
        
        # Step 5: Check user-restaurant relationships
        print(f"\n5. Checking user-restaurant relationships...")
        for restaurant in restaurants:
            restaurant_user_id = restaurant.get('user_id')
            restaurant_name = restaurant.get('name', 'Unnamed')
            print(f"Restaurant '{restaurant_name}' has user_id: {restaurant_user_id}")
            
            # Try to find corresponding user
            if restaurant_user_id:
                try:
                    # Try as ObjectId first
                    user = await db.database.users.find_one({"_id": ObjectId(restaurant_user_id)})
                    if not user:
                        # Try as string
                        user = await db.database.users.find_one({"_id": restaurant_user_id})
                    
                    if user:
                        print(f"  ✅ Found corresponding user: {user.get('email')}")
                    else:
                        print(f"  ❌ No corresponding user found for user_id: {restaurant_user_id}")
                        print(f"     This is a DATA INTEGRITY ISSUE!")
                except Exception as e:
                    print(f"  ❌ Error finding user: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 SIMPLE DIAGNOSIS COMPLETE")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_simple())