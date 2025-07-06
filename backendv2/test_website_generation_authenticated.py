#!/usr/bin/env python3
"""
Authenticated Website Generation Test
Tests website generation with proper authentication
"""
import asyncio
import json
import httpx
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_authenticated_website_generation():
    """Test website generation with authentication"""
    
    print("🔍 TESTING AUTHENTICATED WEBSITE GENERATION")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            
            # Step 1: Create or login a test user
            print("\n1️⃣ Creating/logging in test user...")
            
            # Try to create a test user first
            test_user_data = {
                "email": "test@example.com",
                "password": "testpassword123",
                "name": "Test User"
            }
            
            try:
                # Try to register
                response = await client.post(
                    f"{base_url}/api/auth/register",
                    json=test_user_data
                )
                print(f"   Registration status: {response.status_code}")
                
                if response.status_code == 400:
                    print("   User already exists, trying login...")
                elif response.status_code == 201:
                    print("   ✅ User created successfully")
                    
            except Exception as e:
                print(f"   Registration failed: {str(e)}")
            
            # Now try to login
            login_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            
            try:
                response = await client.post(
                    f"{base_url}/api/auth/login",
                    json=login_data
                )
                print(f"   Login status: {response.status_code}")
                
                if response.status_code == 200:
                    login_response = response.json()
                    access_token = login_response.get("access_token")
                    user_id = login_response.get("user", {}).get("user_id")
                    
                    print(f"   ✅ Login successful")
                    print(f"   User ID: {user_id}")
                    print(f"   Token: {access_token[:20]}..." if access_token else "No token")
                    
                    if not access_token:
                        print("   ❌ No access token received")
                        return
                        
                else:
                    print(f"   ❌ Login failed: {response.text}")
                    return
                    
            except Exception as e:
                print(f"   ❌ Login request failed: {str(e)}")
                return
            
            # Step 2: Create a test restaurant
            print("\n2️⃣ Creating test restaurant...")
            
            restaurant_data = {
                "name": "Test Restaurant for Website",
                "cuisine_type": "Italian",
                "location": "Test City",
                "price_range": "moderate",
                "phone": "555-123-4567",
                "email": "test@restaurant.com"
            }
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            try:
                response = await client.post(
                    f"{base_url}/api/dashboard/restaurants",
                    json=restaurant_data,
                    headers=headers
                )
                print(f"   Restaurant creation status: {response.status_code}")
                
                if response.status_code == 201:
                    restaurant_response = response.json()
                    restaurant_id = restaurant_response.get("restaurant_id")
                    print(f"   ✅ Restaurant created: {restaurant_id}")
                elif response.status_code == 400:
                    # Restaurant might already exist, try to get existing ones
                    print("   Restaurant might already exist, fetching existing...")
                    response = await client.get(
                        f"{base_url}/api/dashboard/restaurants",
                        headers=headers
                    )
                    if response.status_code == 200:
                        restaurants = response.json()
                        if restaurants and len(restaurants) > 0:
                            restaurant_id = restaurants[0].get("_id") or restaurants[0].get("restaurant_id")
                            print(f"   ✅ Using existing restaurant: {restaurant_id}")
                        else:
                            print("   ❌ No restaurants found")
                            return
                    else:
                        print(f"   ❌ Failed to fetch restaurants: {response.text}")
                        return
                else:
                    print(f"   ❌ Restaurant creation failed: {response.text}")
                    return
                    
            except Exception as e:
                print(f"   ❌ Restaurant creation failed: {str(e)}")
                return
            
            # Step 3: Test website generation with authentication
            print("\n3️⃣ Testing website generation with authentication...")
            
            website_request = {
                "restaurant_id": restaurant_id,
                "website_name": "Test Website Generation",
                "design_preferences": {
                    "style": "modern",
                    "colors": ["blue", "white"]
                },
                "content_preferences": {
                    "tone": "professional"
                }
            }
            
            try:
                print(f"   Sending request to generate website for restaurant: {restaurant_id}")
                response = await client.post(
                    f"{base_url}/api/website-builder/generate",
                    json=website_request,
                    headers=headers
                )
                
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    print(f"   ✅ Website generation started successfully!")
                    print(f"   Website ID: {response_data.get('website_id')}")
                    print(f"   Generation Status: {response_data.get('generation_status')}")
                    print(f"   Estimated Time: {response_data.get('estimated_completion_time')} seconds")
                    
                    # Step 4: Check generation progress
                    website_id = response_data.get('website_id')
                    if website_id:
                        print("\n4️⃣ Checking generation progress...")
                        
                        # Extract generation ID from website ID or response
                        generation_id = f"gen_{restaurant_id}_{int(datetime.now().timestamp())}"
                        
                        # Wait a bit for generation to start
                        await asyncio.sleep(2)
                        
                        try:
                            progress_response = await client.get(
                                f"{base_url}/api/website-builder/generation/{generation_id}/progress",
                                headers=headers
                            )
                            print(f"   Progress check status: {progress_response.status_code}")
                            
                            if progress_response.status_code == 200:
                                progress_data = progress_response.json()
                                print(f"   Progress: {progress_data.get('progress_percentage', 0)}%")
                                print(f"   Current Step: {progress_data.get('current_step')}")
                                print(f"   Status: {progress_data.get('status')}")
                            else:
                                print(f"   Progress check response: {progress_response.text}")
                                
                        except Exception as e:
                            print(f"   Progress check failed: {str(e)}")
                    
                elif response.status_code == 500:
                    print(f"   ❌ Internal server error - this is the issue!")
                    try:
                        error_data = response.json()
                        print(f"   Error details: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"   Raw error: {response.text}")
                        
                elif response.status_code == 404:
                    print(f"   ❌ Restaurant not found or access denied")
                    print(f"   Response: {response.text}")
                    
                elif response.status_code == 422:
                    print(f"   ❌ Validation error")
                    try:
                        error_data = response.json()
                        print(f"   Validation errors: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"   Raw validation error: {response.text}")
                        
                else:
                    print(f"   ❌ Unexpected status: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Website generation request failed: {str(e)}")
                import traceback
                traceback.print_exc()
    
    except Exception as e:
        print(f"❌ Critical error in authenticated testing: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    await test_authenticated_website_generation()
    
    print("\n" + "=" * 60)
    print("🔍 AUTHENTICATED TEST SUMMARY")
    print("=" * 60)
    print("This test verifies:")
    print("1. User authentication flow")
    print("2. Restaurant creation/access")
    print("3. Authenticated website generation")
    print("4. Actual error details from the server")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())