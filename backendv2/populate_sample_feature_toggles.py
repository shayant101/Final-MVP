#!/usr/bin/env python3
"""
Populate Sample Feature Toggles
Creates sample feature toggles for testing the admin dashboard
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from database import connect_to_mongo, get_database

async def populate_sample_feature_toggles():
    """Create sample feature toggles"""
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    print("🔧 Creating sample feature toggles...")
    
    # Sample restaurant IDs
    restaurant_ids = [
        "675f551b1a7341a4f85782a1",
        "675f551b1a7341a4f85782a2", 
        "675f551b1a7341a4f85782a3"
    ]
    
    # AI Features to toggle
    ai_features = [
        "content_generation",
        "image_enhancement", 
        "marketing_assistant",
        "menu_optimizer",
        "digital_grader"
    ]
    
    # Create feature toggles for each restaurant
    feature_toggles = []
    
    for restaurant_id in restaurant_ids:
        for feature in ai_features:
            # Vary the enabled status and rate limits
            if feature == "content_generation":
                enabled = True
                rate_limits = {"daily_limit": 50, "hourly_limit": 10}
            elif feature == "image_enhancement":
                enabled = True
                rate_limits = {"daily_limit": 20, "hourly_limit": 5}
            elif feature == "marketing_assistant":
                enabled = restaurant_id != restaurant_ids[2]  # Disabled for one restaurant
                rate_limits = {"daily_limit": 30, "hourly_limit": 8}
            elif feature == "menu_optimizer":
                enabled = True
                rate_limits = {"daily_limit": 15, "hourly_limit": 3}
            else:  # digital_grader
                enabled = restaurant_id == restaurant_ids[0]  # Only enabled for first restaurant
                rate_limits = {"daily_limit": 10, "hourly_limit": 2}
            
            toggle = {
                "restaurant_id": restaurant_id,
                "feature_name": feature,
                "enabled": enabled,
                "rate_limits": rate_limits,
                "updated_at": datetime.utcnow(),
                "updated_by": "admin@momentum.com",
                "created_at": datetime.utcnow()
            }
            
            feature_toggles.append(toggle)
    
    # Insert into database
    try:
        result = await db.ai_feature_toggles.insert_many(feature_toggles)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} feature toggles")
        
        # Print summary
        enabled_count = sum(1 for toggle in feature_toggles if toggle["enabled"])
        disabled_count = len(feature_toggles) - enabled_count
        
        print(f"📊 Feature Toggle Summary:")
        print(f"   • Total Toggles: {len(feature_toggles)}")
        print(f"   • Enabled Features: {enabled_count}")
        print(f"   • Disabled Features: {disabled_count}")
        print(f"   • Restaurants: {len(restaurant_ids)}")
        print(f"   • AI Features: {len(ai_features)}")
        
        print("\n🎯 You can now test the Feature Management tab in the admin dashboard!")
        print("   • View feature toggles by restaurant")
        print("   • Enable/disable features for specific restaurants")
        print("   • Configure rate limits for each feature")
        
    except Exception as e:
        print(f"❌ Error inserting feature toggles: {str(e)}")
        return False
    
    return True

async def main():
    """Main function"""
    print("🚀 Starting sample feature toggles population...")
    
    success = await populate_sample_feature_toggles()
    
    if success:
        print("\n✅ Sample feature toggles populated successfully!")
        print("🔗 Access the admin dashboard at: http://localhost:3000")
        print("🔑 Login with: admin@momentum.com / admin123")
    else:
        print("\n❌ Failed to populate sample data")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())