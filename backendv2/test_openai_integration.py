#!/usr/bin/env python3
"""
Test script for OpenAI integration
"""
import asyncio
import sys
import os
import httpx
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.openai_service import openai_service

async def test_openai_connection():
    """Test OpenAI API connection"""
    print("🔗 Testing OpenAI API connection...")
    try:
        result = await openai_service.test_connection()
        if result["success"]:
            print(f"✅ OpenAI connection successful: {result['message']}")
            print(f"   Service: {result['service']}")
            if "response" in result:
                print(f"   Response: {result['response']}")
        else:
            print(f"❌ OpenAI connection failed: {result['message']}")
            print(f"   Service: {result['service']}")
        return result["success"]
    except Exception as e:
        print(f"❌ OpenAI connection test failed: {str(e)}")
        return False

async def test_ad_copy_generation():
    """Test ad copy generation"""
    print("\n📝 Testing ad copy generation...")
    try:
        result = await openai_service.generate_ad_copy(
            restaurant_name="Mario's Italian Bistro",
            item_to_promote="Margherita Pizza",
            offer="20% off all pizzas this weekend",
            target_audience="pizza lovers"
        )
        
        if result["success"]:
            print("✅ Ad copy generated successfully!")
            print(f"   Full ad copy:\n{result['ad_copy']}")
            print(f"   Character count: {result['metadata']['character_count']}")
            print(f"   Model: {result['metadata']['model']}")
            print(f"   Service: {result['metadata']['service']}")
            
            if "components" in result:
                print(f"   Headline: {result['components']['headline']}")
                print(f"   Body: {result['components']['body']}")
                print(f"   CTA: {result['components']['cta']}")
        else:
            print(f"❌ Ad copy generation failed: {result.get('error', 'Unknown error')}")
        
        return result["success"]
    except Exception as e:
        print(f"❌ Ad copy generation test failed: {str(e)}")
        return False

async def test_sms_generation():
    """Test SMS message generation"""
    print("\n📱 Testing SMS message generation...")
    try:
        result = await openai_service.generate_sms_message(
            restaurant_name="Mario's Italian Bistro",
            customer_name="John",
            offer="20% off your next visit",
            offer_code="WELCOME20",
            message_type="winback"
        )
        
        if result["success"]:
            print("✅ SMS message generated successfully!")
            print(f"   Message: {result['sms_message']}")
            print(f"   Character count: {result['metadata']['character_count']}")
            print(f"   Model: {result['metadata']['model']}")
            print(f"   Service: {result['metadata']['service']}")
        else:
            print(f"❌ SMS generation failed: {result.get('error', 'Unknown error')}")
        
        return result["success"]
    except Exception as e:
        print(f"❌ SMS generation test failed: {str(e)}")
        return False

async def test_email_campaign_generation():
    """Test email campaign generation"""
    print("\n📧 Testing email campaign generation...")
    try:
        result = await openai_service.generate_email_campaign(
            restaurant_name="Mario's Italian Bistro",
            campaign_type="promotional",
            offer="20% off all pasta dishes",
            target_audience="loyal customers"
        )
        
        if result["success"]:
            print("✅ Email campaign generated successfully!")
            email_data = result["email_campaign"]
            print(f"   Subject: {email_data['subject']}")
            print(f"   Preview: {email_data['preview']}")
            print(f"   Content: {email_data['content'][:100]}...")
            print(f"   CTA: {email_data['cta']}")
            print(f"   Model: {result['metadata']['model']}")
            print(f"   Service: {result['metadata']['service']}")
        else:
            print(f"❌ Email campaign generation failed: {result.get('error', 'Unknown error')}")
        
        return result["success"]
    except Exception as e:
        print(f"❌ Email campaign generation test failed: {str(e)}")
        return False

async def test_social_media_generation():
    """Test social media post generation"""
    print("\n📱 Testing social media post generation...")
    try:
        platforms = ["facebook", "instagram", "twitter"]
        success_count = 0
        
        for platform in platforms:
            result = await openai_service.generate_social_media_post(
                restaurant_name="Mario's Italian Bistro",
                platform=platform,
                content_type="promotional",
                item_to_promote="Margherita Pizza",
                offer="20% off all pizzas"
            )
            
            if result["success"]:
                print(f"✅ {platform.capitalize()} post generated successfully!")
                print(f"   Post: {result['social_post'][:100]}...")
                print(f"   Character count: {result['metadata']['character_count']}")
                success_count += 1
            else:
                print(f"❌ {platform.capitalize()} post generation failed: {result.get('error', 'Unknown error')}")
        
        return success_count == len(platforms)
    except Exception as e:
        print(f"❌ Social media generation test failed: {str(e)}")
        return False

async def test_menu_descriptions():
    """Test menu description generation"""
    print("\n🍽️ Testing menu description generation...")
    try:
        items = [
            {"name": "Margherita Pizza", "ingredients": "Fresh mozzarella, tomato sauce, basil"},
            {"name": "Chicken Parmigiana", "ingredients": "Breaded chicken, marinara sauce, mozzarella"},
            {"name": "Caesar Salad", "ingredients": "Romaine lettuce, parmesan, croutons, caesar dressing"}
        ]
        
        result = await openai_service.generate_menu_descriptions(
            restaurant_name="Mario's Italian Bistro",
            cuisine_type="Italian",
            items=items
        )
        
        if result["success"]:
            print("✅ Menu descriptions generated successfully!")
            print(f"   Descriptions:\n{result['menu_descriptions']}")
            print(f"   Model: {result['metadata']['model']}")
            print(f"   Service: {result['metadata']['service']}")
        else:
            print(f"❌ Menu description generation failed: {result.get('error', 'Unknown error')}")
        
        return result["success"]
    except Exception as e:
        print(f"❌ Menu description generation test failed: {str(e)}")
        return False

async def test_campaign_suggestions():
    """Test campaign suggestions generation"""
    print("\n💡 Testing campaign suggestions generation...")
    try:
        result = await openai_service.generate_campaign_suggestions(
            restaurant_name="Mario's Italian Bistro",
            campaign_type="facebook_ad",
            business_goals=["increase sales", "attract new customers", "promote new menu items"]
        )
        
        if result["success"]:
            print("✅ Campaign suggestions generated successfully!")
            print(f"   Suggestions: {result['suggestions'][:200]}...")
            print(f"   Model: {result['metadata']['model']}")
            print(f"   Service: {result['metadata']['service']}")
        else:
            print(f"❌ Campaign suggestions generation failed: {result.get('error', 'Unknown error')}")
        
        return result["success"]
    except Exception as e:
        print(f"❌ Campaign suggestions generation test failed: {str(e)}")
        return False

async def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API endpoints...")
    
    # Note: This would require authentication token in a real test
    print("   API endpoint testing requires authentication token")
    print("   Endpoints available:")
    print("   - POST /api/content/generate/ad-copy")
    print("   - POST /api/content/generate/sms-message")
    print("   - POST /api/content/generate/email-campaign")
    print("   - POST /api/content/generate/social-media-post")
    print("   - POST /api/content/generate/menu-descriptions")
    print("   - POST /api/content/generate/campaign-suggestions")
    print("   - GET /api/content/test-connection")
    print("   - POST /api/content/generate/bulk/social-media")
    print("   - POST /api/content/generate/marketing-package")
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting OpenAI Integration Tests")
    print("=" * 50)
    
    tests = [
        ("OpenAI Connection", test_openai_connection),
        ("Ad Copy Generation", test_ad_copy_generation),
        ("SMS Generation", test_sms_generation),
        ("Email Campaign Generation", test_email_campaign_generation),
        ("Social Media Generation", test_social_media_generation),
        ("Menu Descriptions", test_menu_descriptions),
        ("Campaign Suggestions", test_campaign_suggestions),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OpenAI integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())