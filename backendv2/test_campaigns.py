"""
Comprehensive test suite for campaign management endpoints
"""
import asyncio
import pytest
import httpx
import io
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@restaurant.com"
TEST_PASSWORD = "testpass123"
ADMIN_EMAIL = "admin@momentum.com"
ADMIN_PASSWORD = "admin123"

class TestCampaignManagement:
    def __init__(self):
        self.auth_token = None
        self.admin_token = None
        self.restaurant_id = None
        self.test_campaign_id = None
        
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up campaign tests...")
        
        # Register test user if needed and get auth token
        await self.register_test_user()
        await self.login_test_user()
        
        print("✅ Campaign test setup complete")
    
    async def register_test_user(self):
        """Register a test restaurant user"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{BASE_URL}/api/auth/register", json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD,
                    "restaurantName": "Test Restaurant",
                    "address": "123 Test St",
                    "phone": "555-0123"
                })
                
                if response.status_code == 201:
                    print("✅ Test user registered successfully")
                elif response.status_code == 400:
                    print("ℹ️ Test user already exists")
                else:
                    print(f"⚠️ Registration response: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️ Registration error (user may already exist): {e}")
    
    async def login_test_user(self):
        """Login test user and get auth token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["token"]
                self.restaurant_id = data["user"]["restaurant"]["restaurant_id"]
                print("✅ Test user logged in successfully")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
    
    async def test_facebook_ad_campaign_creation(self):
        """Test Facebook ad campaign creation"""
        print("\n📢 Testing Facebook Ad Campaign Creation...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        async with httpx.AsyncClient() as client:
            # Test campaign data
            campaign_data = {
                "restaurantName": "Test Restaurant",
                "itemToPromote": "Signature Burger",
                "offer": "20% off your next visit",
                "budget": 25.00
            }
            
            # Create form data
            files = {}
            data = campaign_data
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            try:
                response = await client.post(
                    f"{BASE_URL}/api/campaigns/facebook-ads",
                    data=data,
                    files=files,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        self.test_campaign_id = result["data"]["campaign_id"]
                        print("✅ Facebook ad campaign created successfully")
                        print(f"   Campaign ID: {self.test_campaign_id}")
                        print(f"   Promo Code: {result['data']['promo_code']}")
                        print(f"   Expected Reach: {result['data']['expected_reach']}")
                        return True
                    else:
                        print(f"❌ Campaign creation failed: {result}")
                        return False
                else:
                    print(f"❌ HTTP Error: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Exception during campaign creation: {e}")
                return False
    
    async def test_facebook_ad_preview(self):
        """Test Facebook ad preview generation"""
        print("\n👁️ Testing Facebook Ad Preview...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        async with httpx.AsyncClient() as client:
            preview_data = {
                "restaurantName": "Test Restaurant",
                "itemToPromote": "Special Pizza",
                "offer": "Buy one get one 50% off"
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            try:
                response = await client.post(
                    f"{BASE_URL}/api/campaigns/facebook-ads/preview",
                    json=preview_data,
                    headers=headers,
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        preview = result["preview"]
                        print("✅ Facebook ad preview generated successfully")
                        print(f"   Ad Copy: {preview['ad_copy'][:100]}...")
                        print(f"   Promo Code: {preview['promo_code']}")
                        print(f"   Character Count: {preview['character_count']}")
                        return True
                    else:
                        print(f"❌ Preview generation failed: {result}")
                        return False
                else:
                    print(f"❌ HTTP Error: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Exception during preview generation: {e}")
                return False
    
    async def test_sms_campaign_creation(self):
        """Test SMS campaign creation with CSV upload"""
        print("\n📱 Testing SMS Campaign Creation...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        # Create sample CSV content
        csv_content = """customer_name,phone_number,last_order_date,email
John Smith,+1-555-123-4567,2023-10-15,john@email.com
Sarah Johnson,(555) 234-5678,2023-09-22,sarah@email.com
Mike Davis,555.345.6789,2023-08-30,mike@email.com"""
        
        async with httpx.AsyncClient() as client:
            # Prepare form data
            data = {
                "restaurantName": "Test Restaurant",
                "offer": "Come back for 15% off",
                "offerCode": "COMEBACK15"
            }
            
            files = {
                "customerList": ("customers.csv", io.StringIO(csv_content), "text/csv")
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            try:
                response = await client.post(
                    f"{BASE_URL}/api/campaigns/sms",
                    data=data,
                    files=files,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print("✅ SMS campaign created successfully")
                        print(f"   Campaign ID: {result['data']['campaign_id']}")
                        print(f"   Messages Sent: {result['data']['messages_sent']}")
                        print(f"   Total Cost: ${result['data']['total_cost']}")
                        print(f"   Delivery Rate: {result['data']['delivery_rate']}")
                        return True
                    else:
                        print(f"❌ SMS campaign creation failed: {result}")
                        return False
                else:
                    print(f"❌ HTTP Error: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Exception during SMS campaign creation: {e}")
                return False
    
    async def test_sms_preview(self):
        """Test SMS campaign preview"""
        print("\n👁️ Testing SMS Campaign Preview...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        async with httpx.AsyncClient() as client:
            # Prepare form data
            data = {
                "restaurantName": "Test Restaurant",
                "offer": "Special discount just for you",
                "offerCode": "SPECIAL20"
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            try:
                response = await client.post(
                    f"{BASE_URL}/api/campaigns/sms/preview",
                    data=data,
                    headers=headers,
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        preview = result["preview"]
                        print("✅ SMS preview generated successfully")
                        print(f"   Sample Message: {preview['sample_message']}")
                        print(f"   Character Count: {preview['character_count']}")
                        print(f"   Offer Code: {preview['offer_code']}")
                        return True
                    else:
                        print(f"❌ SMS preview generation failed: {result}")
                        return False
                else:
                    print(f"❌ HTTP Error: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Exception during SMS preview generation: {e}")
                return False
    
    async def test_sample_csv_download(self):
        """Test sample CSV download"""
        print("\n📄 Testing Sample CSV Download...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BASE_URL}/api/campaigns/sms/sample-csv")
                
                if response.status_code == 200:
                    csv_content = response.text
                    if "customer_name,phone_number,last_order_date" in csv_content:
                        print("✅ Sample CSV downloaded successfully")
                        print(f"   Content length: {len(csv_content)} characters")
                        return True
                    else:
                        print(f"❌ Invalid CSV content: {csv_content[:100]}")
                        return False
                else:
                    print(f"❌ HTTP Error: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Exception during CSV download: {e}")
                return False
    
    async def test_get_campaigns(self):
        """Test getting campaigns for restaurant"""
        print("\n📋 Testing Get Campaigns...")
        
        if not self.auth_token or not self.restaurant_id:
            print("❌ No auth token or restaurant ID available")
            return False
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            try:
                response = await client.get(
                    f"{BASE_URL}/api/campaigns/{self.restaurant_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        campaigns = result["campaigns"]
                        print("✅ Campaigns retrieved successfully")
                        print(f"   Total campaigns: {result['total']}")
                        for campaign in campaigns[:3]:  # Show first 3
                            print(f"   - {campaign['name']} ({campaign['campaign_type']})")
                        return True
                    else:
                        print(f"❌ Failed to get campaigns: {result}")
                        return False
                else:
                    print(f"❌ HTTP Error: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Exception during get campaigns: {e}")
                return False
    
    async def test_campaign_lifecycle(self):
        """Test campaign lifecycle operations"""
        print("\n🔄 Testing Campaign Lifecycle...")
        
        if not self.auth_token or not self.test_campaign_id:
            print("❌ No auth token or campaign ID available")
            return False
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            try:
                # Test get specific campaign
                response = await client.get(
                    f"{BASE_URL}/api/campaigns/campaign/{self.test_campaign_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    campaign = response.json()
                    print("✅ Campaign details retrieved successfully")
                    print(f"   Campaign: {campaign['name']}")
                    print(f"   Status: {campaign['status']}")
                    print(f"   Type: {campaign['campaign_type']}")
                else:
                    print(f"❌ Failed to get campaign details: {response.status_code}")
                    return False
                
                # Test pause campaign (if active)
                if campaign.get('status') == 'active':
                    response = await client.put(
                        f"{BASE_URL}/api/campaigns/campaign/{self.test_campaign_id}/pause",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            print("✅ Campaign paused successfully")
                        else:
                            print(f"❌ Failed to pause campaign: {result}")
                    else:
                        print(f"❌ Pause request failed: {response.status_code}")
                
                return True
                
            except Exception as e:
                print(f"❌ Exception during campaign lifecycle test: {e}")
                return False
    
    async def test_campaign_status_endpoints(self):
        """Test campaign status and analytics endpoints"""
        print("\n📊 Testing Campaign Status Endpoints...")
        
        if not self.auth_token or not self.test_campaign_id:
            print("❌ No auth token or campaign ID available")
            return False
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            try:
                # Test Facebook campaign status
                response = await client.get(
                    f"{BASE_URL}/api/campaigns/facebook-ads/status/{self.test_campaign_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    status = response.json()
                    if status.get("success"):
                        print("✅ Facebook campaign status retrieved successfully")
                        metrics = status.get("metrics", {})
                        print(f"   Impressions: {metrics.get('impressions', 'N/A')}")
                        print(f"   Clicks: {metrics.get('clicks', 'N/A')}")
                        print(f"   Spend: ${metrics.get('spend', 'N/A')}")
                        return True
                    else:
                        print(f"❌ Failed to get campaign status: {status}")
                        return False
                else:
                    print(f"❌ Status request failed: {response.status_code} - {response.text}")
                    return False
                
            except Exception as e:
                print(f"❌ Exception during status test: {e}")
                return False
    
    async def run_all_tests(self):
        """Run all campaign tests"""
        print("🚀 Starting Campaign Management Tests")
        print("=" * 50)
        
        await self.setup()
        
        tests = [
            ("Facebook Ad Preview", self.test_facebook_ad_preview),
            ("Facebook Ad Campaign Creation", self.test_facebook_ad_campaign_creation),
            ("SMS Preview", self.test_sms_preview),
            ("SMS Campaign Creation", self.test_sms_campaign_creation),
            ("Sample CSV Download", self.test_sample_csv_download),
            ("Get Campaigns", self.test_get_campaigns),
            ("Campaign Lifecycle", self.test_campaign_lifecycle),
            ("Campaign Status", self.test_campaign_status_endpoints),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 CAMPAIGN TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All campaign tests passed!")
        else:
            print(f"⚠️ {total - passed} tests failed")
        
        return passed == total

async def main():
    """Main test runner"""
    tester = TestCampaignManagement()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    asyncio.run(main())