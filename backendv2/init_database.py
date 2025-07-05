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
    
    # Create analytics collections and indexes
    print("📈 Setting up analytics collections and indexes...")
    
    # Create indexes for analytics collections
    analytics_collection = db.database.ai_usage_analytics
    moderation_collection = db.database.ai_content_moderation
    metrics_collection = db.database.ai_performance_metrics
    toggles_collection = db.database.ai_feature_toggles
    
    # Analytics indexes
    await analytics_collection.create_index([("restaurant_id", 1), ("timestamp", -1)])
    await analytics_collection.create_index([("feature_type", 1), ("timestamp", -1)])
    await analytics_collection.create_index([("status", 1), ("timestamp", -1)])
    
    # Moderation indexes
    await moderation_collection.create_index([("status", 1), ("flagged_at", -1)])
    await moderation_collection.create_index([("restaurant_id", 1), ("status", 1)])
    
    # Performance metrics indexes
    await metrics_collection.create_index([("feature_type", 1), ("metric_date", -1)])
    
    # Feature toggles indexes
    await toggles_collection.create_index([("restaurant_id", 1), ("feature_name", 1)], unique=True)
    
    print("✅ Created analytics indexes")
    
    # Create initial admin user if not exists
    admin_user = await users_collection.find_one({"role": "admin"})
    if not admin_user:
        print("👑 Creating initial admin user...")
        admin_doc = {
            "_id": ObjectId(),
            "email": "admin@momentum.com",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VJWZFsMlO",  # password: admin123
            "role": "admin",
            "created_at": datetime.utcnow()
        }
        await users_collection.insert_one(admin_doc)
        print("✅ Created admin user (email: admin@momentum.com, password: admin123)")
    else:
        print("✅ Admin user already exists")
    
    # Set up default feature toggles for the restaurant
    print("🎛️ Setting up default feature toggles...")
    default_features = [
        {
            "feature_name": "image_enhancement",
            "enabled": True,
            "rate_limits": {"daily_limit": 100, "hourly_limit": 10}
        },
        {
            "feature_name": "content_generation",
            "enabled": True,
            "rate_limits": {"daily_limit": 50, "hourly_limit": 5}
        },
        {
            "feature_name": "marketing_assistant",
            "enabled": True,
            "rate_limits": {"daily_limit": 20, "hourly_limit": 3}
        },
        {
            "feature_name": "menu_optimizer",
            "enabled": True,
            "rate_limits": {"daily_limit": 10, "hourly_limit": 2}
        },
        {
            "feature_name": "digital_grader",
            "enabled": True,
            "rate_limits": {"daily_limit": 5, "hourly_limit": 1}
        }
    ]
    
    for feature in default_features:
        toggle_doc = {
            "toggle_id": str(ObjectId()),
            "restaurant_id": restaurant_id,
            "feature_name": feature["feature_name"],
            "enabled": feature["enabled"],
            "rate_limits": feature["rate_limits"],
            "updated_at": datetime.utcnow(),
            "updated_by": "system"
        }
        
        # Upsert the toggle
        await toggles_collection.update_one(
            {"restaurant_id": restaurant_id, "feature_name": feature["feature_name"]},
            {"$set": toggle_doc},
            upsert=True
        )
    
    print(f"✅ Set up {len(default_features)} default feature toggles")
    
    # Create some sample analytics data
    print("📊 Creating sample analytics data...")
    sample_analytics = []
    
    # Generate sample data for the last 7 days
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        
        # Image enhancement usage
        for j in range(5):
            sample_analytics.append({
                "analytics_id": str(ObjectId()),
                "restaurant_id": restaurant_id,
                "feature_type": "image_enhancement",
                "operation_type": "enhance_image",
                "timestamp": date - timedelta(hours=j),
                "processing_time_ms": 1200 + (j * 100),
                "tokens_used": 0,
                "estimated_cost": 0.0,
                "status": "success",
                "metadata": {"image_size": "2MB", "enhancement_applied": True},
                "created_at": date - timedelta(hours=j)
            })
        
        # Content generation usage
        for j in range(3):
            sample_analytics.append({
                "analytics_id": str(ObjectId()),
                "restaurant_id": restaurant_id,
                "feature_type": "content_generation",
                "operation_type": "generate_social_media",
                "timestamp": date - timedelta(hours=j + 2),
                "processing_time_ms": 800 + (j * 50),
                "tokens_used": 150 + (j * 25),
                "estimated_cost": 0.003 + (j * 0.0005),
                "status": "success",
                "metadata": {"content_type": "social_media_caption"},
                "created_at": date - timedelta(hours=j + 2)
            })
    
    if sample_analytics:
        await analytics_collection.insert_many(sample_analytics)
        print(f"✅ Created {len(sample_analytics)} sample analytics records")
    
    print("\n🎉 Database initialization complete!")
    print(f"📊 Restaurant ID: {restaurant_id}")
    print("👑 Admin user: admin@momentum.com (password: admin123)")
    print("🔗 You can now test the dashboard and admin endpoints")

if __name__ == "__main__":
    asyncio.run(init_database())