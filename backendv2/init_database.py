#!/usr/bin/env python3.9
"""
Database Initialization Script
Creates collections and sample data for the dashboard endpoints
"""
import asyncio
from datetime import datetime, timedelta
from bson import ObjectId
from app.database import connect_to_mongo, initialize_collections, db

async def init_database():
    """Initialize database with collections and sample data"""
    print("🔧 Initializing database...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    await initialize_collections()
    
    # Get collection references
    users_collection = db.database.users
    campaigns_collection = db.database.campaigns
    checklist_collection = db.database.checklist_status
    
    # Get a sample restaurant user
    restaurant_user = await users_collection.find_one({"role": "restaurant"})
    if not restaurant_user:
        print("❌ No restaurant user found. Please register a restaurant first.")
        return
    
    restaurant_id = str(restaurant_user["_id"])
    print(f"✅ Found restaurant user: {restaurant_user.get('email')} (ID: {restaurant_id})")
    
    # Create sample campaigns
    print("📊 Creating sample campaigns...")
    sample_campaigns = [
        {
            "_id": ObjectId(),
            "restaurant_id": restaurant_id,
            "campaign_type": "ad",
            "status": "active",
            "name": "Summer Special Promotion",
            "details": "20% off all summer dishes",
            "budget": 500.00,
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "_id": ObjectId(),
            "restaurant_id": restaurant_id,
            "campaign_type": "sms",
            "status": "active",
            "name": "Weekend Brunch SMS",
            "details": "SMS campaign for weekend brunch specials",
            "budget": 200.00,
            "created_at": datetime.utcnow() - timedelta(days=3),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "restaurant_id": restaurant_id,
            "campaign_type": "ad",
            "status": "completed",
            "name": "Grand Opening Campaign",
            "details": "Initial launch campaign",
            "budget": 1000.00,
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow() - timedelta(days=25)
        }
    ]
    
    # Insert campaigns (replace existing)
    await campaigns_collection.delete_many({"restaurant_id": restaurant_id})
    await campaigns_collection.insert_many(sample_campaigns)
    print(f"✅ Created {len(sample_campaigns)} sample campaigns")
    
    # Create sample checklist items
    print("📋 Creating sample checklist items...")
    sample_checklist = [
        {
            "_id": ObjectId(),
            "restaurant_id": restaurant_id,
            "checklist_item_name": "Set up Google My Business",
            "is_complete": True,
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow() - timedelta(days=8)
        },
        {
            "_id": ObjectId(),
            "restaurant_id": restaurant_id,
            "checklist_item_name": "Create Facebook Business Page",
            "is_complete": True,
            "created_at": datetime.utcnow() - timedelta(days=9),
            "updated_at": datetime.utcnow() - timedelta(days=7)
        },
        {
            "_id": ObjectId(),
            "restaurant_id": restaurant_id,
            "checklist_item_name": "Upload menu photos",
            "is_complete": False,
            "created_at": datetime.utcnow() - timedelta(days=8),
            "updated_at": datetime.utcnow() - timedelta(days=8)
        },
        {
            "_id": ObjectId(),
            "restaurant_id": restaurant_id,
            "checklist_item_name": "Set up online ordering",
            "is_complete": False,
            "created_at": datetime.utcnow() - timedelta(days=7),
            "updated_at": datetime.utcnow() - timedelta(days=7)
        },
        {
            "_id": ObjectId(),
            "restaurant_id": restaurant_id,
            "checklist_item_name": "Configure SMS notifications",
            "is_complete": False,
            "created_at": datetime.utcnow() - timedelta(days=6),
            "updated_at": datetime.utcnow() - timedelta(days=6)
        }
    ]
    
    # Insert checklist items (replace existing)
    await checklist_collection.delete_many({"restaurant_id": restaurant_id})
    await checklist_collection.insert_many(sample_checklist)
    print(f"✅ Created {len(sample_checklist)} sample checklist items")
    
    # Update restaurant with some performance metrics
    print("📈 Adding performance metrics to restaurant...")
    await users_collection.update_one(
        {"_id": restaurant_user["_id"]},
        {
            "$set": {
                "new_customers_acquired": 45,
                "customers_reengaged": 23,
                "total_customers": 150,
                "monthly_revenue": 12500.00,
                "customer_retention": 78.5,
                "campaign_performance": 85.2
            }
        }
    )
    print("✅ Added performance metrics")
    
    print("\n🎉 Database initialization complete!")
    print(f"📊 Restaurant ID: {restaurant_id}")
    print("🔗 You can now test the dashboard endpoints")

if __name__ == "__main__":
    asyncio.run(init_database())