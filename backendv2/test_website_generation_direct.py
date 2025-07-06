#!/usr/bin/env python3
"""
Test website generation directly with Roma Trattoria account
"""
import asyncio
import sys
import json
sys.path.append('.')

from app.database import connect_to_mongo, db
from app.routes.website_builder import _get_restaurant_data
from app.auth import TokenData
from bson import ObjectId

async def test_website_generation():
    """Test website generation with Roma Trattoria account"""
    print("🔍 TESTING WEBSITE GENERATION WITH ROMA TRATTORIA")
    print("=" * 60)
    
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Database connected")
        
        # Roma Trattoria data from logs
        restaurant_id = "685f6e61f5e9b5ab108e9f93"  # Restaurant _id
        user_id = "685f6e61f5e9b5ab108e9f92"        # User _id
        
        print(f"\n1. Testing with Roma Trattoria:")
        print(f"   Restaurant ID: {restaurant_id}")
        print(f"   User ID: {user_id}")
        
        # Create mock user token (simulating logged-in user)
        mock_user = TokenData(user_id=user_id, email="romatrattoria@yahoo.com", role="restaurant")
        
        # Test Step 1: Dashboard endpoint simulation
        print(f"\n2. Simulating dashboard API call...")
        try:
            from app.services.dashboard_service import DashboardService
            dashboard_data = await DashboardService.get_restaurant_dashboard_data(restaurant_id)
            
            print("✅ Dashboard service works!")
            restaurant_data = dashboard_data.get('restaurant', {})
            extracted_restaurant_id = restaurant_data.get('restaurant_id')
            
            print(f"   Dashboard returns restaurant_id: {extracted_restaurant_id}")
            print(f"   Dashboard returns user_id: {restaurant_data.get('user_id')}")
            print(f"   Dashboard returns name: {restaurant_data.get('name')}")
            
            # This is what the frontend extracts
            frontend_restaurant_id = extracted_restaurant_id
            
        except Exception as e:
            print(f"❌ Dashboard service failed: {e}")
            return
        
        # Test Step 2: Website builder _get_restaurant_data function
        print(f"\n3. Testing _get_restaurant_data with extracted ID...")
        print(f"   Using restaurant_id: {frontend_restaurant_id}")
        
        try:
            restaurant_data = await _get_restaurant_data(frontend_restaurant_id, mock_user, db)
            
            if restaurant_data:
                print("✅ _get_restaurant_data SUCCESS!")
                print(f"   Returned restaurant name: {restaurant_data.get('name')}")
                print(f"   Returned restaurant_id: {restaurant_data.get('restaurant_id')}")
                print(f"   Has menu items: {len(restaurant_data.get('menu_items', []))}")
            else:
                print("❌ _get_restaurant_data returned None")
                print("   This means the restaurant lookup or access check failed")
                
                # Debug the failure
                print(f"\n4. Debugging the failure...")
                
                # Test ObjectId conversion
                try:
                    restaurant_object_id = ObjectId(frontend_restaurant_id)
                    print(f"   ✅ ObjectId conversion: {restaurant_object_id}")
                except Exception as e:
                    print(f"   ❌ ObjectId conversion failed: {e}")
                    return
                
                # Test restaurant lookup
                restaurant = await db.database.restaurants.find_one({"_id": restaurant_object_id})
                if restaurant:
                    print(f"   ✅ Restaurant found in database")
                    print(f"   Restaurant user_id: {restaurant.get('user_id')}")
                    print(f"   Mock user user_id: {mock_user.user_id}")
                    print(f"   User ID match: {restaurant.get('user_id') == mock_user.user_id}")
                    
                    if restaurant.get('user_id') != mock_user.user_id:
                        print(f"   ❌ USER ID MISMATCH - This is the problem!")
                        print(f"   Restaurant expects: {restaurant.get('user_id')}")
                        print(f"   User provides: {mock_user.user_id}")
                else:
                    print(f"   ❌ Restaurant not found in database")
                
        except Exception as e:
            print(f"❌ _get_restaurant_data failed with error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test Step 3: Check the actual data flow
        print(f"\n5. Checking complete data flow...")
        
        # What the dashboard returns
        print(f"   Dashboard restaurant.restaurant_id: {dashboard_data.get('restaurant', {}).get('restaurant_id')}")
        
        # What the restaurant collection has
        restaurant_doc = await db.database.restaurants.find_one({"_id": ObjectId(restaurant_id)})
        if restaurant_doc:
            print(f"   Database restaurant._id: {restaurant_doc.get('_id')}")
            print(f"   Database restaurant.user_id: {restaurant_doc.get('user_id')}")
        
        # What the user collection has
        user_doc = await db.database.users.find_one({"_id": ObjectId(user_id)})
        if user_doc:
            print(f"   Database user._id: {user_doc.get('_id')}")
            print(f"   Database user.email: {user_doc.get('email')}")
        
        print("\n" + "=" * 60)
        print("🎯 WEBSITE GENERATION TEST COMPLETE")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_website_generation())