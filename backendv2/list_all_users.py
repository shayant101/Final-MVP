#!/usr/bin/env python3
"""
List all users and restaurants in the database
"""
import asyncio
from app.database import connect_to_mongo, get_users_collection, get_restaurants_collection

async def list_all_users():
    """List all users and their associated restaurants"""
    
    print("🔍 LISTING ALL USERS AND RESTAURANTS")
    print("=" * 50)
    
    try:
        await connect_to_mongo()
        users_collection = get_users_collection()
        restaurants_collection = get_restaurants_collection()
        
        print("\n📋 ALL USERS:")
        print("-" * 30)
        
        user_count = 0
        restaurant_count = 0
        
        async for user in users_collection.find({}):
            user_count += 1
            email = user.get('email', 'No email')
            role = user.get('role', 'No role')
            user_id = str(user.get('_id'))
            created_at = user.get('created_at', 'Unknown')
            
            print(f"\n👤 USER #{user_count}")
            print(f"   📧 Email: {email}")
            print(f"   🎭 Role: {role}")
            print(f"   🆔 User ID: {user_id}")
            print(f"   📅 Created: {created_at}")
            
            # If it's a restaurant user, find their restaurant
            if role == 'restaurant':
                restaurant = await restaurants_collection.find_one({'user_id': user_id})
                if restaurant:
                    restaurant_count += 1
                    restaurant_name = restaurant.get('name', 'Unnamed Restaurant')
                    restaurant_id = str(restaurant.get('_id'))
                    address = restaurant.get('address', 'No address')
                    phone = restaurant.get('phone', 'No phone')
                    
                    print(f"   🏪 Restaurant: {restaurant_name}")
                    print(f"   🆔 Restaurant ID: {restaurant_id}")
                    print(f"   📍 Address: {address}")
                    print(f"   📞 Phone: {phone}")
                    
                    # Note: We can't show actual passwords as they're hashed
                    print(f"   🔐 Login: {email} / [password is hashed]")
                else:
                    print(f"   ❌ No restaurant found for this user")
            
            print("   " + "-" * 40)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Users: {user_count}")
        print(f"   Total Restaurants: {restaurant_count}")
        print(f"   Admin Users: {user_count - restaurant_count}")
        
        print(f"\n💡 COMMON TEST PASSWORDS:")
        print(f"   - test123")
        print(f"   - admin123") 
        print(f"   - password123")
        print(f"   - restaurant123")
        
        print(f"\n🔑 TO TEST LOGIN:")
        print(f"   Try each email with the common passwords above")
        print(f"   Or create a new account using the registration form")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(list_all_users())