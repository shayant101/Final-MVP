import asyncio
import random
from datetime import datetime, timedelta
from app.database import connect_to_mongo, get_database
from bson import ObjectId

async def populate_sample_checklist_status():
    """Create sample checklist completion data for restaurants"""
    try:
        print("🚀 Starting sample checklist status population...")
        
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        
        # Get all restaurants
        restaurants = []
        async for restaurant in db.restaurants.find():
            restaurants.append(restaurant)
        
        # Get all checklist items
        items = []
        async for item in db.checklist_items.find():
            items.append(item)
        
        print(f"📊 Found {len(restaurants)} restaurants and {len(items)} checklist items")
        
        # Clear existing checklist status data
        await db.restaurant_checklist_status.delete_many({})
        print("✅ Cleared existing checklist status data")
        
        # Create sample completion data for each restaurant
        for restaurant in restaurants:
            restaurant_id = restaurant["_id"]
            restaurant_name = restaurant.get("name", "Unknown")
            
            # Create realistic completion patterns
            # Some restaurants are more advanced than others
            completion_rate = random.uniform(0.2, 0.8)  # 20% to 80% completion
            
            completed_items = []
            
            for item in items:
                # Higher chance of completing critical items
                if item.get("is_critical", False):
                    complete_chance = completion_rate + 0.2  # Boost for critical items
                else:
                    complete_chance = completion_rate
                
                # Foundational items are more likely to be completed first
                category_cursor = db.checklist_categories.find({"_id": item["category_id"]})
                category = await category_cursor.to_list(length=1)
                if category and category[0].get("type") == "foundational":
                    complete_chance += 0.1
                
                # Cap at 100%
                complete_chance = min(complete_chance, 1.0)
                
                if random.random() < complete_chance:
                    # Create completion record
                    completion_date = datetime.utcnow() - timedelta(days=random.randint(1, 90))
                    
                    status_doc = {
                        "restaurant_id": restaurant_id,
                        "item_id": item["_id"],
                        "is_completed": True,
                        "completed_at": completion_date,
                        "notes": f"Completed for {restaurant_name}",
                        "created_at": completion_date,
                        "updated_at": completion_date
                    }
                    completed_items.append(status_doc)
            
            # Insert all completion records for this restaurant
            if completed_items:
                await db.restaurant_checklist_status.insert_many(completed_items)
                print(f"✅ Created {len(completed_items)} completion records for {restaurant_name}")
            else:
                print(f"⚠️  No items completed for {restaurant_name}")
        
        # Verify the data
        total_completions = await db.restaurant_checklist_status.count_documents({})
        print(f"🎉 Sample checklist status population completed!")
        print(f"📊 Total completion records created: {total_completions}")
        
        # Show sample completion rates
        print("\n📈 Sample completion rates by restaurant:")
        for restaurant in restaurants[:5]:  # Show first 5
            restaurant_id = restaurant["_id"]
            restaurant_name = restaurant.get("name", "Unknown")
            
            completed_count = await db.restaurant_checklist_status.count_documents({
                "restaurant_id": restaurant_id,
                "is_completed": True
            })
            
            completion_rate = (completed_count / len(items)) * 100 if items else 0
            print(f"  - {restaurant_name}: {completed_count}/{len(items)} items ({completion_rate:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error populating sample checklist status: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(populate_sample_checklist_status())