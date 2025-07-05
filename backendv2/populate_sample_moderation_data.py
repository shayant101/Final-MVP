#!/usr/bin/env python3
"""
Populate Sample Moderation Data
Creates sample flagged, approved, and rejected content for testing the admin dashboard
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from database import connect_to_mongo, get_database

async def populate_sample_moderation_data():
    """Create sample content moderation data"""
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    print("🔧 Creating sample content moderation data...")
    
    # Sample restaurant IDs (you can adjust these)
    restaurant_ids = [
        "675f551b1a7341a4f85782a1",  # Sample restaurant ID
        "675f551b1a7341a4f85782a2",
        "675f551b1a7341a4f85782a3"
    ]
    
    # Sample flagged content
    flagged_content = [
        {
            "moderation_id": str(uuid.uuid4()),
            "restaurant_id": restaurant_ids[0],
            "content_type": "social_media_post",
            "content_id": "post_001",
            "status": "flagged",
            "content_data": {
                "text": "Check out our amazing new burger! 🍔 Best in town!",
                "platform": "facebook",
                "scheduled_time": "2025-01-06T12:00:00Z"
            },
            "flags": ["promotional_language", "needs_review"],
            "reviewed_by": None,
            "flagged_at": datetime.utcnow() - timedelta(hours=2),
            "reviewed_at": None,
            "created_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "moderation_id": str(uuid.uuid4()),
            "restaurant_id": restaurant_ids[1],
            "content_type": "menu_description",
            "content_id": "menu_item_042",
            "status": "flagged",
            "content_data": {
                "item_name": "Spicy Dragon Roll",
                "description": "Our signature sushi roll with fresh salmon, avocado, and spicy mayo",
                "price": "$14.99"
            },
            "flags": ["allergen_warning_missing", "needs_review"],
            "reviewed_by": None,
            "flagged_at": datetime.utcnow() - timedelta(hours=5),
            "reviewed_at": None,
            "created_at": datetime.utcnow() - timedelta(hours=5)
        },
        {
            "moderation_id": str(uuid.uuid4()),
            "restaurant_id": restaurant_ids[2],
            "content_type": "marketing_email",
            "content_id": "email_campaign_15",
            "status": "flagged",
            "content_data": {
                "subject": "Limited Time Offer - 50% Off!",
                "content": "Don't miss out on our incredible half-price deal this weekend only!",
                "recipient_count": 1250
            },
            "flags": ["high_discount_claim", "urgency_language"],
            "reviewed_by": None,
            "flagged_at": datetime.utcnow() - timedelta(minutes=30),
            "reviewed_at": None,
            "created_at": datetime.utcnow() - timedelta(minutes=30)
        }
    ]
    
    # Sample approved content
    approved_content = [
        {
            "moderation_id": str(uuid.uuid4()),
            "restaurant_id": restaurant_ids[0],
            "content_type": "social_media_post",
            "content_id": "post_002",
            "status": "approved",
            "content_data": {
                "text": "Join us for our weekly trivia night every Wednesday at 7 PM!",
                "platform": "instagram",
                "scheduled_time": "2025-01-08T19:00:00Z"
            },
            "flags": ["community_event"],
            "reviewed_by": "admin@momentum.com",
            "flagged_at": datetime.utcnow() - timedelta(days=1),
            "reviewed_at": datetime.utcnow() - timedelta(hours=18),
            "review_reason": "Community event promotion - approved",
            "created_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "moderation_id": str(uuid.uuid4()),
            "restaurant_id": restaurant_ids[1],
            "content_type": "menu_description",
            "content_id": "menu_item_043",
            "status": "approved",
            "content_data": {
                "item_name": "Classic Caesar Salad",
                "description": "Fresh romaine lettuce, parmesan cheese, croutons, and our house-made Caesar dressing",
                "price": "$12.99"
            },
            "flags": ["standard_menu_item"],
            "reviewed_by": "admin@momentum.com",
            "flagged_at": datetime.utcnow() - timedelta(days=2),
            "reviewed_at": datetime.utcnow() - timedelta(days=1, hours=12),
            "review_reason": "Standard menu description - approved",
            "created_at": datetime.utcnow() - timedelta(days=2)
        }
    ]
    
    # Sample rejected content
    rejected_content = [
        {
            "moderation_id": str(uuid.uuid4()),
            "restaurant_id": restaurant_ids[2],
            "content_type": "social_media_post",
            "content_id": "post_003",
            "status": "rejected",
            "content_data": {
                "text": "URGENT!!! MUST TRY NOW!!! BEST DEAL EVER!!! LIMITED TIME!!!",
                "platform": "facebook",
                "scheduled_time": "2025-01-05T10:00:00Z"
            },
            "flags": ["excessive_caps", "spam_like", "poor_quality"],
            "reviewed_by": "admin@momentum.com",
            "flagged_at": datetime.utcnow() - timedelta(days=3),
            "reviewed_at": datetime.utcnow() - timedelta(days=2, hours=8),
            "review_reason": "Excessive capitalization and spam-like content - rejected",
            "created_at": datetime.utcnow() - timedelta(days=3)
        },
        {
            "moderation_id": str(uuid.uuid4()),
            "restaurant_id": restaurant_ids[0],
            "content_type": "marketing_email",
            "content_id": "email_campaign_12",
            "status": "rejected",
            "content_data": {
                "subject": "You WON'T BELIEVE these prices!!!",
                "content": "CLICK NOW OR MISS OUT FOREVER! Our competitors HATE this one trick!",
                "recipient_count": 2500
            },
            "flags": ["clickbait", "misleading_claims", "poor_quality"],
            "reviewed_by": "admin@momentum.com",
            "flagged_at": datetime.utcnow() - timedelta(days=4),
            "reviewed_at": datetime.utcnow() - timedelta(days=3, hours=6),
            "review_reason": "Clickbait subject and misleading content - rejected",
            "created_at": datetime.utcnow() - timedelta(days=4)
        }
    ]
    
    # Combine all content
    all_content = flagged_content + approved_content + rejected_content
    
    # Insert into database
    try:
        result = await db.ai_content_moderation.insert_many(all_content)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} content moderation records")
        
        # Print summary
        flagged_count = len(flagged_content)
        approved_count = len(approved_content)
        rejected_count = len(rejected_content)
        
        print(f"📊 Content Summary:")
        print(f"   • Flagged Content: {flagged_count} items")
        print(f"   • Approved Content: {approved_count} items")
        print(f"   • Rejected Content: {rejected_count} items")
        print(f"   • Total: {len(all_content)} items")
        
        print("\n🎯 You can now test the Content Moderation tab in the admin dashboard!")
        print("   • Switch between Flagged, Approved, and Rejected content using the dropdown")
        print("   • Use the search functionality to filter content")
        print("   • Test the moderation workflow by approving/rejecting flagged items")
        
    except Exception as e:
        print(f"❌ Error inserting content moderation data: {str(e)}")
        return False
    
    return True

async def main():
    """Main function"""
    print("🚀 Starting sample content moderation data population...")
    
    success = await populate_sample_moderation_data()
    
    if success:
        print("\n✅ Sample content moderation data populated successfully!")
        print("🔗 Access the admin dashboard at: http://localhost:3000")
        print("🔑 Login with: admin@momentum.com / admin123")
    else:
        print("\n❌ Failed to populate sample data")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())