"""
Test SMS Preview with Authentication
"""
import asyncio
import httpx
import json
import io

async def test_sms_preview_with_auth():
    """Test the SMS preview endpoint with proper authentication"""
    print("🧪 Testing SMS Preview with Authentication")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test data
    test_csv_content = """customer_name,phone_number,last_order_date
John Doe,+1234567890,2024-01-15
Jane Smith,1987654321,2024-02-20
Bob Johnson,555-123-4567,2024-01-10"""
    
    async with httpx.AsyncClient() as client:
        # Step 1: Login to get authentication token
        print("\n🔐 Logging in...")
        login_data = {
            "username": "testrestaurant",
            "password": "password123"
        }
        
        login_response = await client.post(
            f"{base_url}/api/auth/login",
            data=login_data
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return
        
        login_result = login_response.json()
        token = login_result["access_token"]
        print("✅ Login successful!")
        
        # Step 2: Test SMS preview with authentication
        print("\n📱 Testing SMS Preview with Authentication...")
        
        # Create a test CSV file in memory
        csv_file = io.BytesIO(test_csv_content.encode())
        
        try:
            files = {
                'customerList': ('test_customers.csv', csv_file, 'text/csv')
            }
            data = {
                'restaurantName': 'Test Restaurant',
                'offer': 'Get 20% off your next order!',
                'offerCode': 'TEST20'
            }
            
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = await client.post(
                f"{base_url}/api/campaigns/sms/preview",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SMS Preview successful!")
                print(f"   Sample message: {result['preview']['sample_message']}")
                print(f"   Character count: {result['preview']['character_count']}")
                print(f"   Target customers: {result['preview']['target_customers']}")
                print(f"   Estimated cost: ${result['preview']['estimated_cost']}")
                if result['preview'].get('csv_stats'):
                    stats = result['preview']['csv_stats']
                    print(f"   CSV Stats:")
                    print(f"     - Total uploaded: {stats['total_uploaded']}")
                    print(f"     - Lapsed customers: {stats['lapsed_customers']}")
                    print(f"     - Errors: {stats['errors']}")
            else:
                print(f"❌ SMS Preview failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing SMS preview: {str(e)}")
        
        # Step 3: Test SMS preview without CSV (should still work)
        print("\n📱 Testing SMS Preview without CSV...")
        try:
            data = {
                'restaurantName': 'Test Restaurant',
                'offer': 'Get 20% off your next order!',
                'offerCode': 'TEST20'
            }
            
            response = await client.post(
                f"{base_url}/api/campaigns/sms/preview",
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SMS Preview (no CSV) successful!")
                print(f"   Sample message: {result['preview']['sample_message']}")
                print(f"   Character count: {result['preview']['character_count']}")
                print(f"   Target customers: {result['preview']['target_customers']}")
                print(f"   Estimated cost: ${result['preview']['estimated_cost']}")
            else:
                print(f"❌ SMS Preview (no CSV) failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing SMS preview without CSV: {str(e)}")
    
    print(f"\n🎉 SMS Preview authentication test completed!")

if __name__ == "__main__":
    asyncio.run(test_sms_preview_with_auth())