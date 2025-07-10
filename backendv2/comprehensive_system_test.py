#!/usr/bin/env python3
"""
Comprehensive system test to check all functionality
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def comprehensive_test():
    """Run comprehensive tests on the live system"""
    
    base_url = "https://final-mvp-jc3a.onrender.com"
    
    print("🔍 COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    print(f"Testing: {base_url}")
    print(f"Time: {datetime.now()}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Health Check
        print("\n1️⃣ HEALTH CHECK")
        print("-" * 30)
        try:
            async with session.get(f"{base_url}/api/health", timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"✅ Health: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Status: {data.get('status')}")
                    print(f"   Database: {data.get('database')}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        # Test 2: Authentication Test
        print("\n2️⃣ AUTHENTICATION TEST")
        print("-" * 30)
        
        # Test login with Roma Trattoria credentials
        login_data = {"email": "romatrattoria@yahoo.com", "password": "test123"}
        auth_token = None
        
        try:
            async with session.post(f"{base_url}/api/auth/login", json=login_data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"✅ Login attempt: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    auth_token = data.get('token')
                    user = data.get('user', {})
                    restaurant = user.get('restaurant', {})
                    print(f"   User: {user.get('email')}")
                    print(f"   Restaurant: {restaurant.get('name')}")
                    print(f"   Restaurant ID: {restaurant.get('restaurant_id')}")
                    print(f"   Token: {'✅ Received' if auth_token else '❌ Missing'}")
                else:
                    error_data = await response.json()
                    print(f"   Error: {error_data}")
        except Exception as e:
            print(f"❌ Login failed: {e}")
        
        # Test 3: Website Builder Check (if authenticated)
        print("\n3️⃣ WEBSITE BUILDER TEST")
        print("-" * 30)
        
        if auth_token:
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            # Check existing websites
            try:
                async with session.get(f"{base_url}/api/website-builder/websites", headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    print(f"✅ Get websites: {response.status}")
                    if response.status == 200:
                        websites = await response.json()
                        print(f"   Found {len(websites)} websites")
                        for i, website in enumerate(websites, 1):
                            print(f"   Website {i}: {website.get('name', 'Unnamed')} (ID: {website.get('_id')})")
                    else:
                        error_data = await response.json()
                        print(f"   Error: {error_data}")
            except Exception as e:
                print(f"❌ Website check failed: {e}")
        else:
            print("❌ Skipped - No auth token")
        
        # Test 4: Dashboard Data
        print("\n4️⃣ DASHBOARD TEST")
        print("-" * 30)
        
        if auth_token:
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            try:
                async with session.get(f"{base_url}/api/dashboard/restaurant", headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    print(f"✅ Dashboard: {response.status}")
                    if response.status == 200:
                        dashboard = await response.json()
                        print(f"   Restaurant: {dashboard.get('restaurant', {}).get('name')}")
                        print(f"   Checklist items: {len(dashboard.get('checklist_items', []))}")
                        print(f"   Campaigns: {len(dashboard.get('campaigns', []))}")
                    else:
                        error_data = await response.json()
                        print(f"   Error: {error_data}")
            except Exception as e:
                print(f"❌ Dashboard failed: {e}")
        else:
            print("❌ Skipped - No auth token")
        
        # Test 5: Database Direct Check
        print("\n5️⃣ DATABASE CONNECTIVITY TEST")
        print("-" * 30)
        
        # Test if we can reach any endpoint that would indicate DB connectivity
        try:
            async with session.get(f"{base_url}/", timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"✅ Root endpoint: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   API Version: {data.get('message', 'Unknown')}")
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")
        
        # Test 6: CORS Test
        print("\n6️⃣ CORS TEST")
        print("-" * 30)
        
        # Check if CORS headers are present
        try:
            async with session.options(f"{base_url}/api/auth/login", timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"✅ CORS preflight: {response.status}")
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                }
                for header, value in cors_headers.items():
                    print(f"   {header}: {value or 'Not set'}")
        except Exception as e:
            print(f"❌ CORS test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print("Check the results above to identify any issues.")
    print("If websites are missing, it suggests a database sync issue.")
    print("If authentication fails, there might be credential issues.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(comprehensive_test())