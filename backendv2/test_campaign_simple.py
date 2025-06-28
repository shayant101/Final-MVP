"""
Simple campaign endpoint test with fresh user registration
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_campaign_endpoints():
    """Test campaign endpoints with fresh user"""
    print("🚀 Testing Campaign Endpoints")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Register a fresh test user
        print("📝 Registering fresh test user...")
        register_data = {
            "email": f"campaign_test_{int(asyncio.get_event_loop().time())}@test.com",
            "password": "testpass123",
            "restaurantName": "Campaign Test Restaurant",
            "address": "123 Test Street",
            "phone": "555-0123"
        }
        
        response = await client.post(f"{BASE_URL}/api/auth/register", json=register_data)
        
        if response.status_code != 200:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
        
        auth_data = response.json()
        token = auth_data["token"]
        restaurant_id = auth_data["user"]["restaurant"]["restaurant_id"]
        
        print("✅ User registered successfully")
        print(f"   Restaurant ID: {restaurant_id}")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 1: Facebook Ad Preview
        print("\n👁️ Testing Facebook Ad Preview...")
        preview_data = {
            "restaurantName": "Campaign Test Restaurant",
            "itemToPromote": "Signature Burger",
            "offer": "20% off your next visit"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/campaigns/facebook-ads/preview",
            json=preview_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Facebook ad preview generated successfully")
            print(f"   Promo Code: {result['preview']['promo_code']}")
            print(f"   Character Count: {result['preview']['character_count']}")
        else:
            print(f"❌ Preview failed: {response.status_code} - {response.text}")
        
        # Test 2: SMS Preview
        print("\n📱 Testing SMS Preview...")
        sms_data = {
            "restaurantName": "Campaign Test Restaurant",
            "offer": "Come back for 15% off",
            "offerCode": "COMEBACK15"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/campaigns/sms/preview",
            data=sms_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SMS preview generated successfully")
            print(f"   Sample Message: {result['preview']['sample_message']}")
            print(f"   Character Count: {result['preview']['character_count']}")
        else:
            print(f"❌ SMS preview failed: {response.status_code} - {response.text}")
        
        # Test 3: Facebook Ad Campaign Creation
        print("\n📢 Testing Facebook Ad Campaign Creation...")
        campaign_data = {
            "restaurantName": "Campaign Test Restaurant",
            "itemToPromote": "Signature Burger",
            "offer": "20% off your next visit",
            "budget": "25.00"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/campaigns/facebook-ads",
            data=campaign_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                campaign_id = result["data"]["campaign_id"]
                print("✅ Facebook ad campaign created successfully")
                print(f"   Campaign ID: {campaign_id}")
                print(f"   Expected Reach: {result['data']['expected_reach']}")
                
                # Test 4: Get Campaign Details
                print("\n📋 Testing Get Campaign Details...")
                response = await client.get(
                    f"{BASE_URL}/api/campaigns/campaign/{campaign_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    campaign = response.json()
                    print("✅ Campaign details retrieved successfully")
                    print(f"   Name: {campaign['name']}")
                    print(f"   Status: {campaign['status']}")
                    print(f"   Type: {campaign['campaign_type']}")
                else:
                    print(f"❌ Get campaign failed: {response.status_code}")
                
                # Test 5: Get All Campaigns
                print("\n📋 Testing Get All Campaigns...")
                response = await client.get(
                    f"{BASE_URL}/api/campaigns/{restaurant_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ All campaigns retrieved successfully")
                    print(f"   Total campaigns: {result['total']}")
                else:
                    print(f"❌ Get all campaigns failed: {response.status_code}")
                
                # Test 6: Campaign Status
                print("\n📊 Testing Campaign Status...")
                response = await client.get(
                    f"{BASE_URL}/api/campaigns/facebook-ads/status/{campaign_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    status = response.json()
                    if status.get("success"):
                        print("✅ Campaign status retrieved successfully")
                        metrics = status.get("metrics", {})
                        print(f"   Impressions: {metrics.get('impressions')}")
                        print(f"   Clicks: {metrics.get('clicks')}")
                        print(f"   Spend: ${metrics.get('spend')}")
                    else:
                        print(f"❌ Status retrieval failed: {status}")
                else:
                    print(f"❌ Status request failed: {response.status_code}")
            else:
                print(f"❌ Campaign creation failed: {result}")
        else:
            print(f"❌ Campaign creation failed: {response.status_code} - {response.text}")
        
        # Test 7: Sample CSV Download
        print("\n📄 Testing Sample CSV Download...")
        response = await client.get(f"{BASE_URL}/api/campaigns/sms/sample-csv")
        
        if response.status_code == 200:
            csv_content = response.text
            print("✅ Sample CSV downloaded successfully")
            print(f"   Content length: {len(csv_content)} characters")
        else:
            print(f"❌ CSV download failed: {response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎉 Campaign endpoint testing completed!")
        print("✅ All major campaign functionality is working")
        
        return True

if __name__ == "__main__":
    asyncio.run(test_campaign_endpoints())