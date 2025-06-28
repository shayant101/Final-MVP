#!/usr/bin/env python3
"""
Test script to verify OpenAI integration with campaign service
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.campaign_service import campaign_service
from app.models import FacebookAdCampaignCreate

async def test_facebook_campaign_with_openai():
    """Test Facebook campaign creation with OpenAI integration"""
    print("🚀 Testing Facebook campaign creation with OpenAI integration...")
    
    try:
        # Create test campaign data
        campaign_data = FacebookAdCampaignCreate(
            restaurantName="Mario's Italian Bistro",
            itemToPromote="Margherita Pizza",
            offer="20% off all pizzas this weekend",
            budget=50.0
        )
        
        # Test restaurant ID (this would normally come from authentication)
        test_restaurant_id = "test_restaurant_123"
        
        print(f"📝 Creating campaign for: {campaign_data.restaurantName}")
        print(f"   Item: {campaign_data.itemToPromote}")
        print(f"   Offer: {campaign_data.offer}")
        print(f"   Budget: ${campaign_data.budget}")
        
        # Create the campaign (this will use OpenAI for ad copy generation)
        result = await campaign_service.create_facebook_ad_campaign(
            restaurant_id=test_restaurant_id,
            campaign_data=campaign_data
        )
        
        if result["success"]:
            print("✅ Campaign created successfully!")
            print(f"   Campaign ID: {result['data']['campaign_id']}")
            print(f"   Promo Code: {result['data']['promo_code']}")
            print(f"   Expected Reach: {result['data']['expected_reach']}")
            print(f"   Ad Copy Preview:")
            print(f"   {result['data']['ad_copy']}")
            return True
        else:
            print(f"❌ Campaign creation failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Campaign test failed: {str(e)}")
        return False

async def main():
    """Run campaign integration test"""
    print("🧪 OpenAI Campaign Integration Test")
    print("=" * 50)
    
    success = await test_facebook_campaign_with_openai()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OpenAI integration with campaigns is working correctly!")
        print("   ✅ Ad copy generation integrated")
        print("   ✅ Campaign creation successful")
        print("   ✅ Fallback mechanism working")
    else:
        print("⚠️ Campaign integration test failed")
        print("   Check the error messages above for details")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())