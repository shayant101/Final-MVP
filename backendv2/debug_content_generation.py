#!/usr/bin/env python3
"""
Debug script for content generation issues
"""

import asyncio
import httpx
import json

async def test_facebook_ad_preview():
    """Test Facebook ad preview endpoint"""
    print("🧪 Testing Facebook Ad Preview...")
    
    # Test data
    test_data = {
        "restaurantName": "Test Restaurant",
        "itemToPromote": "Burger Special",
        "offer": "20% off all burgers"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # First, let's try to login to get a token
            login_response = await client.post(
                "http://localhost:8000/api/auth/login",
                json={
                    "email": "testuser6939@restaurant.com",  # Using the user we created earlier
                    "password": "password123"
                }
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return False
            
            login_data = login_response.json()
            token = login_data.get("token")
            
            if not token:
                print("❌ No token received from login")
                return False
            
            print("✅ Login successful, testing ad preview...")
            
            # Test Facebook ad preview
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                "http://localhost:8000/api/campaigns/facebook-ads/preview",
                json=test_data,
                headers=headers
            )
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Facebook Ad Preview Response:")
                print(json.dumps(result, indent=2))
                
                # Check if preview content is empty
                preview = result.get("preview", {})
                ad_copy = preview.get("ad_copy", "")
                
                if not ad_copy or ad_copy.strip() == "":
                    print("❌ Ad copy is empty!")
                    return False
                else:
                    print(f"✅ Ad copy generated: {len(ad_copy)} characters")
                    return True
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing Facebook ad preview: {e}")
        return False

async def test_sms_preview():
    """Test SMS preview endpoint"""
    print("\n🧪 Testing SMS Preview...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Login first
            login_response = await client.post(
                "http://localhost:8000/api/auth/login",
                json={
                    "email": "testuser6939@restaurant.com",
                    "password": "password123"
                }
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                return False
            
            token = login_response.json().get("token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test SMS preview
            form_data = {
                "restaurantName": "Test Restaurant",
                "offer": "20% off your next visit",
                "offerCode": "SAVE20"
            }
            
            response = await client.post(
                "http://localhost:8000/api/campaigns/sms/preview",
                data=form_data,
                headers=headers
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SMS Preview Response:")
                print(json.dumps(result, indent=2))
                
                # Check if preview content is empty
                preview = result.get("preview", {})
                sample_message = preview.get("sample_message", "")
                
                if not sample_message or sample_message.strip() == "":
                    print("❌ SMS message is empty!")
                    return False
                else:
                    print(f"✅ SMS message generated: {len(sample_message)} characters")
                    return True
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing SMS preview: {e}")
        return False

async def test_mock_service_directly():
    """Test the mock service directly"""
    print("\n🧪 Testing Mock Service Directly...")
    
    try:
        from app.services.mock_openai import generate_ad_copy, generate_sms_message
        
        # Test ad copy generation
        print("Testing ad copy generation...")
        ad_result = await generate_ad_copy("Test Restaurant", "Burger Special", "20% off all burgers")
        print(f"Ad Copy Result: {json.dumps(ad_result, indent=2)}")
        
        # Test SMS generation
        print("\nTesting SMS generation...")
        sms_result = await generate_sms_message("Test Restaurant", "John", "20% off your next visit", "SAVE20")
        print(f"SMS Result: {json.dumps(sms_result, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing mock service: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔍 CONTENT GENERATION DEBUG")
    print("=" * 50)
    
    # Test mock service directly first
    mock_success = await test_mock_service_directly()
    
    # Test API endpoints
    fb_success = await test_facebook_ad_preview()
    sms_success = await test_sms_preview()
    
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    print(f"Mock Service: {'✅ PASS' if mock_success else '❌ FAIL'}")
    print(f"Facebook Ad Preview: {'✅ PASS' if fb_success else '❌ FAIL'}")
    print(f"SMS Preview: {'✅ PASS' if sms_success else '❌ FAIL'}")
    
    if not any([mock_success, fb_success, sms_success]):
        print("\n❌ All tests failed - investigating further...")
    elif mock_success and not (fb_success and sms_success):
        print("\n⚠️  Mock service works but API endpoints fail - check API integration")
    else:
        print("\n✅ Content generation is working!")

if __name__ == "__main__":
    asyncio.run(main())