"""
Test SMS Campaign API endpoints
"""
import asyncio
import httpx
import json
import io

async def test_sms_api():
    """Test the SMS campaign API endpoints"""
    print("🧪 Testing SMS Campaign API")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test data
    test_csv_content = """customer_name,phone_number,last_order_date
John Doe,+1234567890,2024-01-15
Jane Smith,1987654321,2024-02-20
Bob Johnson,555-123-4567,2024-01-10"""
    
    # Create a test CSV file in memory
    csv_file = io.BytesIO(test_csv_content.encode())
    
    async with httpx.AsyncClient() as client:
        print("\n📱 Testing SMS Preview Endpoint...")
        try:
            # Test SMS preview
            files = {
                'customerList': ('test_customers.csv', csv_file, 'text/csv')
            }
            data = {
                'restaurantName': 'Test Restaurant',
                'offer': 'Get 20% off your next order!',
                'offerCode': 'TEST20'
            }
            
            response = await client.post(
                f"{base_url}/api/campaigns/sms/preview",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SMS Preview successful!")
                print(f"   Sample message: {result['preview']['sample_message']}")
                print(f"   Character count: {result['preview']['character_count']}")
                print(f"   Target customers: {result['preview']['target_customers']}")
                print(f"   Estimated cost: ${result['preview']['estimated_cost']}")
            else:
                print(f"❌ SMS Preview failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing SMS preview: {str(e)}")
        
        print("\n📋 Testing Sample CSV Download...")
        try:
            response = await client.get(f"{base_url}/api/campaigns/sms/sample-csv")
            
            if response.status_code == 200:
                print("✅ Sample CSV download successful!")
                print(f"   Content length: {len(response.content)} bytes")
                print(f"   Content type: {response.headers.get('content-type')}")
            else:
                print(f"❌ Sample CSV download failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing sample CSV: {str(e)}")
    
    print(f"\n🎉 SMS API test completed!")

if __name__ == "__main__":
    asyncio.run(test_sms_api())