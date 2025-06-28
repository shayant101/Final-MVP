"""
Reverse Engineer Checklist Scores
This script analyzes the current marketing scores shown on dashboard cards
and updates checklist completion status to match those scores.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import connect_to_mongo, db
from app.services.dashboard_service import DashboardService
from bson import ObjectId
import random

async def reverse_engineer_checklist_scores():
    """
    Reverse engineer checklist completion to match dashboard marketing scores
    """
    try:
        print("🚀 Starting checklist score reverse engineering...")
        
        # Connect to database
        await connect_to_mongo()
        
        # Get all restaurants
        restaurants_collection = db.database.restaurants
        restaurants = await restaurants_collection.find({}).to_list(length=None)
        
        print(f"📊 Found {len(restaurants)} restaurants to process")
        
        for restaurant in restaurants:
            restaurant_id = str(restaurant["_id"])
            restaurant_name = restaurant.get("name", "Unknown")
            
            print(f"\n🏪 Processing {restaurant_name} (ID: {restaurant_id})")
            
            try:
                # Get current dashboard data (which has the target marketing score)
                dashboard_data = await DashboardService.get_restaurant_dashboard_data(restaurant_id)
                target_score = dashboard_data.get("momentumMetrics", {}).get("marketingScore", 0)
                
                print(f"🎯 Target marketing score: {target_score}")
                
                # Get all checklist items
                items_collection = db.database.checklist_items
                categories_collection = db.database.checklist_categories
                status_collection = db.database.restaurant_checklist_status
                
                # Get all items with their categories
                pipeline = [
                    {
                        "$lookup": {
                            "from": "checklist_categories",
                            "localField": "category_id",
                            "foreignField": "_id",
                            "as": "category"
                        }
                    },
                    {"$unwind": "$category"},
                    {"$sort": {"category.order_in_list": 1, "order_in_category": 1}}
                ]
                
                all_items = await items_collection.aggregate(pipeline).to_list(length=None)
                
                # Separate foundational and ongoing items
                foundational_items = [item for item in all_items if item["category"]["type"] == "foundational"]
                ongoing_items = [item for item in all_items if item["category"]["type"] == "ongoing"]
                
                print(f"📋 Found {len(foundational_items)} foundational items, {len(ongoing_items)} ongoing items")
                
                # Calculate how many items to complete to reach target score
                # Using the same algorithm as MarketingFoundations.js
                foundational_weight = 0.7
                ongoing_weight = 0.3
                critical_bonus = 0.1
                
                # Clear existing status for this restaurant
                await status_collection.delete_many({"restaurant_id": ObjectId(restaurant_id)})
                
                # Determine completion strategy based on target score
                if target_score == 0:
                    # No items completed
                    foundational_to_complete = 0
                    ongoing_to_complete = 0
                elif target_score <= 20:
                    # Complete a few foundational items (prioritize critical)
                    foundational_to_complete = min(3, len(foundational_items))
                    ongoing_to_complete = 0
                elif target_score <= 40:
                    # Complete more foundational items
                    foundational_to_complete = min(int(len(foundational_items) * 0.3), len(foundational_items))
                    ongoing_to_complete = 0
                elif target_score <= 60:
                    # Complete majority of foundational items
                    foundational_to_complete = min(int(len(foundational_items) * 0.6), len(foundational_items))
                    ongoing_to_complete = min(int(len(ongoing_items) * 0.2), len(ongoing_items))
                elif target_score <= 80:
                    # Complete most foundational items and some ongoing
                    foundational_to_complete = min(int(len(foundational_items) * 0.8), len(foundational_items))
                    ongoing_to_complete = min(int(len(ongoing_items) * 0.4), len(ongoing_items))
                else:
                    # High score - complete most items
                    foundational_to_complete = min(int(len(foundational_items) * 0.9), len(foundational_items))
                    ongoing_to_complete = min(int(len(ongoing_items) * 0.6), len(ongoing_items))
                
                print(f"📝 Will complete {foundational_to_complete}/{len(foundational_items)} foundational items")
                print(f"📝 Will complete {ongoing_to_complete}/{len(ongoing_items)} ongoing items")
                
                # Prioritize critical items for completion
                foundational_critical = [item for item in foundational_items if item.get("is_critical", False)]
                foundational_non_critical = [item for item in foundational_items if not item.get("is_critical", False)]
                
                # Select items to complete (prioritize critical items)
                items_to_complete = []
                
                # Complete critical items first
                critical_to_complete = min(len(foundational_critical), foundational_to_complete)
                items_to_complete.extend(foundational_critical[:critical_to_complete])
                
                # Complete remaining foundational items
                remaining_foundational = foundational_to_complete - critical_to_complete
                if remaining_foundational > 0:
                    items_to_complete.extend(foundational_non_critical[:remaining_foundational])
                
                # Complete ongoing items
                if ongoing_to_complete > 0:
                    items_to_complete.extend(ongoing_items[:ongoing_to_complete])
                
                # Create completion records
                completion_records = []
                for item in items_to_complete:
                    completion_records.append({
                        "restaurant_id": ObjectId(restaurant_id),
                        "item_id": item["_id"],
                        "status": "completed",
                        "notes": "Auto-completed to match dashboard score",
                        "last_updated_at": restaurant.get("created_at")  # Use restaurant creation date
                    })
                
                if completion_records:
                    await status_collection.insert_many(completion_records)
                    print(f"✅ Created {len(completion_records)} completion records")
                
                # Verify the resulting score
                final_metrics = await DashboardService._calculate_momentum_metrics_exact(restaurant_id)
                actual_score = final_metrics.get("marketingScore", 0)
                
                print(f"🎯 Target: {target_score}, Actual: {actual_score}, Difference: {abs(target_score - actual_score)}")
                
                if abs(target_score - actual_score) > 5:  # Allow 5 point tolerance
                    print(f"⚠️  Score difference is significant, may need manual adjustment")
                
            except Exception as e:
                print(f"❌ Error processing {restaurant_name}: {str(e)}")
                continue
        
        print(f"\n🎉 Checklist score reverse engineering completed!")
        print(f"📊 Processed {len(restaurants)} restaurants")
        
        # Verify overall results
        print(f"\n📈 Final verification:")
        for restaurant in restaurants[:5]:  # Show first 5 as sample
            restaurant_id = str(restaurant["_id"])
            restaurant_name = restaurant.get("name", "Unknown")
            
            try:
                dashboard_data = await DashboardService.get_restaurant_dashboard_data(restaurant_id)
                target_score = dashboard_data.get("momentumMetrics", {}).get("marketingScore", 0)
                
                final_metrics = await DashboardService._calculate_momentum_metrics_exact(restaurant_id)
                actual_score = final_metrics.get("marketingScore", 0)
                
                print(f"  {restaurant_name}: Target={target_score}, Actual={actual_score}")
            except Exception as e:
                print(f"  {restaurant_name}: Error - {str(e)}")
        
    except Exception as e:
        print(f"❌ Error in reverse engineering: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(reverse_engineer_checklist_scores())