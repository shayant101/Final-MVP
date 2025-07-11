#!/usr/bin/env python3
"""
Test script for admin delete functionality
This script will help debug the admin delete endpoint
"""
import asyncio
import sys
import os
sys.path.insert(0, 'app')

from app.database import get_database
from bson import ObjectId

async def test_admin_delete():
    """Test the admin delete functionality"""
    print("🧪 Testing Admin Delete Functionality")
    print("=" * 50)
    
    try:
        # Get database connection
        db = get_database()
        print("✅ Database connection established")
        
        # List all restaurants
        restaurants = await db.restaurants.find({}).to_list(length=10)
        print(f"📊 Found {len(restaurants)} restaurants in database")
        
        if restaurants:
            print("\n🏪 Available restaurants:")
            for i, restaurant in enumerate(restaurants[:5]):  # Show first 5
                print(f"  {i+1}. ID: {restaurant['_id']}")
                print(f"     Name: {restaurant.get('name', 'Unknown')}")
                print(f"     Email: {restaurant.get('email', 'Unknown')}")
                print(f"     Type: {type(restaurant['_id'])}")
                print()
            
            # Test ObjectId conversion
            test_id = str(restaurants[0]['_id'])
            print(f"🔍 Testing ObjectId conversion with: {test_id}")
            
            # Test if ObjectId.is_valid works
            if ObjectId.is_valid(test_id):
                converted_id = ObjectId(test_id)
                print(f"✅ ObjectId conversion successful: {converted_id}")
                
                # Test database query with converted ObjectId
                found_restaurant = await db.restaurants.find_one({"_id": converted_id})
                if found_restaurant:
                    print("✅ Database query with ObjectId successful")
                    print(f"   Found: {found_restaurant.get('name', 'Unknown')}")
                else:
                    print("❌ Database query with ObjectId failed")
            else:
                print(f"❌ Invalid ObjectId format: {test_id}")
        else:
            print("❌ No restaurants found in database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_admin_delete())