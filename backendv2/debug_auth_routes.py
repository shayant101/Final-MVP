#!/usr/bin/env python3
"""
Debug script to test auth routes and validate endpoint availability
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_auth_endpoints():
    """Test various auth endpoint combinations to identify the issue"""
    
    base_urls = [
        "https://final-mvp-jc3a.onrender.com",
        "http://localhost:8000"  # For local testing
    ]
    
    endpoints_to_test = [
        "/auth/login",           # What frontend is trying to call
        "/api/auth/login",       # What should work based on route definition
        "/docs",                 # FastAPI docs to see available routes
        "/api/health",           # Health check
        "/"                      # Root endpoint
    ]
    
    print("🔍 DEBUGGING AUTH ROUTES - Testing endpoint availability")
    print("=" * 60)
    
    for base_url in base_urls:
        print(f"\n🌐 Testing base URL: {base_url}")
        print("-" * 40)
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints_to_test:
                full_url = f"{base_url}{endpoint}"
                try:
                    print(f"Testing: {full_url}")
                    
                    if endpoint == "/auth/login" or endpoint == "/api/auth/login":
                        # Test POST request for login endpoints
                        test_data = {
                            "email": "test@example.com",
                            "password": "testpassword"
                        }
                        async with session.post(
                            full_url, 
                            json=test_data,
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            print(f"  ✅ POST {response.status}: {response.reason}")
                            if response.status != 404:
                                try:
                                    data = await response.json()
                                    print(f"  📄 Response: {json.dumps(data, indent=2)[:200]}...")
                                except:
                                    text = await response.text()
                                    print(f"  📄 Response: {text[:200]}...")
                    else:
                        # Test GET request for other endpoints
                        async with session.get(
                            full_url,
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            print(f"  ✅ GET {response.status}: {response.reason}")
                            if response.status == 200 and endpoint in ["/", "/api/health"]:
                                try:
                                    data = await response.json()
                                    print(f"  📄 Response: {json.dumps(data, indent=2)}")
                                except:
                                    text = await response.text()
                                    print(f"  📄 Response: {text[:200]}...")
                            elif response.status == 200 and endpoint == "/docs":
                                print(f"  📄 FastAPI docs are available - check manually for route list")
                                
                except asyncio.TimeoutError:
                    print(f"  ❌ TIMEOUT: Request timed out")
                except aiohttp.ClientError as e:
                    print(f"  ❌ CLIENT ERROR: {e}")
                except Exception as e:
                    print(f"  ❌ ERROR: {e}")
                    
                print()  # Empty line for readability

    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS SUMMARY:")
    print("1. If /auth/login returns 404 but /api/auth/login works:")
    print("   → Frontend is calling wrong endpoint")
    print("2. If both return 404:")
    print("   → Backend route registration issue")
    print("3. If /docs is available:")
    print("   → Check FastAPI docs for actual available routes")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_auth_endpoints())