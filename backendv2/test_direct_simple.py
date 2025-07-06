#!/usr/bin/env python3
"""
Direct test of website generation logic without imports
"""
import asyncio
import sys
sys.path.append('.')

from app.database import connect_to_mongo, db
from app.services.dashboard_service import DashboardService
from bson import ObjectId

async def test_direct():
    """Test the exact website generation flow"""
    print("🔍 DIRECT WEBSITE GENERATION TEST")
    print("=" * 50)
    
    try:
        await connect_to_mongo()
        print("✅ Database connected")
        
        # Roma Trattoria data from backend logs
        restaurant_id = "685f6e61f5e9b5ab108e9f93"  # Restaurant _id
        user_id = "685f6e61f5e9b5ab108e9f92"        # User _id
        
        print(f"\n1. Testing with Roma Trattoria:")
        print(f"   Restaurant ID: {restaurant_id}")
        print(f"   User ID: {user_id}")
        
        # Step 1: Test dashboard service (what frontend calls first)
        print(f"\n2. Testing dashboard service...")
        try:
            dashboard_data = await DashboardService.get_restaurant_dashboard_data(restaurant_id)
            print("✅ Dashboard service works!")
            
            restaurant_info = dashboard_data.get('restaurant', {})
            extracted_restaurant_id = restaurant_info.get('restaurant_id')
            extracted_user_id = restaurant_info.get('user_id')
            
            print(f"   Dashboard returns:")
            print(f"     restaurant_id: {extracted_restaurant_id}")
            print(f"     user_id: {extracted_user_id}")
            print(f"     name: {restaurant_info.get('name')}")
            
        except Exception as e:
            print(f"❌ Dashboard service failed: {e}")
            return
        
        # Step 2: Test the _get_restaurant_data logic manually
        print(f"\n3. Testing restaurant data retrieval logic...")
        
        # This is the exact logic from _get_restaurant_data function
        try:
            # Convert restaurant_id to ObjectId for MongoDB query
            try:
                restaurant_object_id = ObjectId(extracted_restaurant_id)
                print(f"   ✅ ObjectId conversion: {restaurant_object_id}")
            except Exception as e:
                print(f"   ❌ ObjectId conversion failed: {e}")
                return
            
            # Get restaurant from database
            restaurant = await db.database.restaurants.find_one({"_id": restaurant_object_id})
            if not restaurant:
                print(f"   ❌ Restaurant not found in database")
                return
            
            print(f"   ✅ Restaurant found: {restaurant.get('name')}")
            
            # Verify user has access (this is the critical check)
            restaurant_user_id = restaurant.get("user_id")
            current_user_id = extracted_user_id  # This comes from the dashboard
            
            print(f"   Access check:")
            print(f"     Restaurant user_id: {restaurant_user_id} (type: {type(restaurant_user_id)})")
            print(f"     Current user_id: {current_user_id} (type: {type(current_user_id)})")
            print(f"     Match: {restaurant_user_id == current_user_id}")
            
            if restaurant_user_id != current_user_id:
                print(f"   ❌ ACCESS DENIED - User ID mismatch!")
                print(f"   This is likely the root cause of 'Failed to fetch restaurants'")
                
                # Let's check if it's a string vs ObjectId issue
                try:
                    if str(restaurant_user_id) == str(current_user_id):
                        print(f"   🔧 String comparison works - it's a type mismatch issue")
                    else:
                        print(f"   ❌ Even string comparison fails - data integrity issue")
                except Exception as e:
                    print(f"   ❌ String comparison error: {e}")
                
                return
            
            print(f"   ✅ Access granted!")
            
            # Get additional data (menu items, etc.)
            menu_items = await db.database.menu_items.find({"restaurant_id": extracted_restaurant_id}).to_list(length=None)
            print(f"   Found {len(menu_items)} menu items")
            
            # Combine data for AI (this would be the final result)
            restaurant_data = {
                **restaurant,
                "menu_items": menu_items,
                "restaurant_id": extracted_restaurant_id
            }
            
            print(f"   ✅ Restaurant data compiled successfully!")
            print(f"   Final restaurant_id: {restaurant_data.get('restaurant_id')}")
            print(f"   Restaurant name: {restaurant_data.get('name')}")
            print(f"   Menu items: {len(restaurant_data.get('menu_items', []))}")
            
        except Exception as e:
            print(f"❌ Restaurant data retrieval failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 50)
        print("🎯 DIRECT TEST COMPLETE")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct())