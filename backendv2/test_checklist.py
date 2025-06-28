import asyncio
import aiohttp
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "admin@test.com"
TEST_PASSWORD = "admin123"

class ChecklistTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.restaurant_id = None

    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    async def login(self):
        """Login and get auth token"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            async with self.session.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["token"]
                    user_data = data["user"]
                    
                    # For restaurant users, user_id IS the restaurant_id in our system
                    if user_data["role"] == "restaurant":
                        self.restaurant_id = user_data["user_id"]
                    elif user_data.get("restaurant"):
                        self.restaurant_id = user_data["restaurant"]["restaurant_id"]
                    
                    print(f"✅ Login successful - Role: {user_data['role']}")
                    if self.restaurant_id:
                        print(f"   Restaurant ID: {self.restaurant_id}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Login failed: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}

    async def test_get_categories(self):
        """Test GET /api/checklist/categories"""
        print("\n🧪 Testing GET /api/checklist/categories")
        
        try:
            # Test without filter
            async with self.session.get(
                f"{BASE_URL}/api/checklist/categories",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    categories = data["categories"]
                    print(f"✅ All categories: {len(categories)} found")
                    
                    # Print first few categories
                    for i, cat in enumerate(categories[:3]):
                        print(f"   {i+1}. {cat['name']} ({cat['type']})")
                else:
                    error_data = await response.json()
                    print(f"❌ Failed: {error_data}")
                    return False

            # Test with foundational filter
            async with self.session.get(
                f"{BASE_URL}/api/checklist/categories?type=foundational",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    foundational_categories = data["categories"]
                    print(f"✅ Foundational categories: {len(foundational_categories)} found")
                else:
                    print(f"❌ Foundational filter failed")
                    return False

            # Test with ongoing filter
            async with self.session.get(
                f"{BASE_URL}/api/checklist/categories?type=ongoing",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    ongoing_categories = data["categories"]
                    print(f"✅ Ongoing categories: {len(ongoing_categories)} found")
                    return True
                else:
                    print(f"❌ Ongoing filter failed")
                    return False

        except Exception as e:
            print(f"❌ Categories test error: {e}")
            return False

    async def test_get_category_items(self):
        """Test GET /api/checklist/items/{category_id}"""
        print("\n🧪 Testing GET /api/checklist/items/{category_id}")
        
        try:
            # First get a category ID
            async with self.session.get(
                f"{BASE_URL}/api/checklist/categories",
                headers=self.get_auth_headers()
            ) as response:
                if response.status != 200:
                    print("❌ Failed to get categories for items test")
                    return False
                
                data = await response.json()
                categories = data["categories"]
                if not categories:
                    print("❌ No categories found for items test")
                    return False
                
                category_id = categories[0]["category_id"]
                category_name = categories[0]["name"]

            # Test getting items for this category
            async with self.session.get(
                f"{BASE_URL}/api/checklist/items/{category_id}",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data["items"]
                    print(f"✅ Items for '{category_name}': {len(items)} found")
                    
                    # Print first few items
                    for i, item in enumerate(items[:3]):
                        critical = "🔴" if item["is_critical"] else "⚪"
                        print(f"   {critical} {item['title']}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Failed: {error_data}")
                    return False

        except Exception as e:
            print(f"❌ Category items test error: {e}")
            return False

    async def test_categories_with_items(self):
        """Test GET /api/checklist/categories-with-items"""
        print("\n🧪 Testing GET /api/checklist/categories-with-items")
        
        try:
            # Test without restaurant ID
            async with self.session.get(
                f"{BASE_URL}/api/checklist/categories-with-items",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    categories = data["categories"]
                    total_items = sum(len(cat["items"]) for cat in categories)
                    print(f"✅ Categories with items: {len(categories)} categories, {total_items} total items")
                    
                    # Test with restaurant ID if available
                    if self.restaurant_id:
                        async with self.session.get(
                            f"{BASE_URL}/api/checklist/categories-with-items?restaurant_id={self.restaurant_id}",
                            headers=self.get_auth_headers()
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                print(f"✅ Categories with restaurant status included")
                                return True
                            else:
                                print(f"❌ Failed with restaurant ID")
                                return False
                    else:
                        print("ℹ️  No restaurant ID available for status test")
                        return True
                else:
                    error_data = await response.json()
                    print(f"❌ Failed: {error_data}")
                    return False

        except Exception as e:
            print(f"❌ Categories with items test error: {e}")
            return False

    async def test_update_item_status(self):
        """Test PUT /api/checklist/status/{restaurant_id}/{item_id}"""
        print("\n🧪 Testing PUT /api/checklist/status/{restaurant_id}/{item_id}")
        
        if not self.restaurant_id:
            print("⚠️  Skipping status update test - no restaurant ID available")
            return True
        
        try:
            # Get an item ID to test with
            async with self.session.get(
                f"{BASE_URL}/api/checklist/categories-with-items",
                headers=self.get_auth_headers()
            ) as response:
                if response.status != 200:
                    print("❌ Failed to get items for status test")
                    return False
                
                data = await response.json()
                categories = data["categories"]
                if not categories or not categories[0]["items"]:
                    print("❌ No items found for status test")
                    return False
                
                item_id = categories[0]["items"][0]["item_id"]
                item_title = categories[0]["items"][0]["title"]

            # Test updating status to completed
            async with self.session.put(
                f"{BASE_URL}/api/checklist/status/{self.restaurant_id}/{item_id}?status=completed&notes=Test completion from API test",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Status updated for '{item_title}' to completed")
                    
                    # Test updating to in_progress
                    async with self.session.put(
                        f"{BASE_URL}/api/checklist/status/{self.restaurant_id}/{item_id}?status=in_progress&notes=Test in progress status",
                        headers=self.get_auth_headers()
                    ) as response:
                        if response.status == 200:
                            print(f"✅ Status updated to in_progress")
                            return True
                        else:
                            print(f"❌ Failed to update to in_progress")
                            return False
                else:
                    error_data = await response.json()
                    print(f"❌ Failed: {error_data}")
                    return False

        except Exception as e:
            print(f"❌ Status update test error: {e}")
            return False

    async def test_get_restaurant_status(self):
        """Test GET /api/checklist/status/{restaurant_id}"""
        print("\n🧪 Testing GET /api/checklist/status/{restaurant_id}")
        
        if not self.restaurant_id:
            print("⚠️  Skipping restaurant status test - no restaurant ID available")
            return True
        
        try:
            async with self.session.get(
                f"{BASE_URL}/api/checklist/status/{self.restaurant_id}",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    statuses = data["statuses"]
                    print(f"✅ Restaurant status: {len(statuses)} items with status")
                    
                    # Show status breakdown
                    status_counts = {}
                    for status in statuses:
                        status_val = status["status"]
                        status_counts[status_val] = status_counts.get(status_val, 0) + 1
                    
                    for status, count in status_counts.items():
                        print(f"   {status}: {count} items")
                    
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Failed: {error_data}")
                    return False

        except Exception as e:
            print(f"❌ Restaurant status test error: {e}")
            return False

    async def test_get_progress(self):
        """Test GET /api/checklist/progress/{restaurant_id}"""
        print("\n🧪 Testing GET /api/checklist/progress/{restaurant_id}")
        
        if not self.restaurant_id:
            print("⚠️  Skipping progress test - no restaurant ID available")
            return True
        
        try:
            # Test overall progress
            async with self.session.get(
                f"{BASE_URL}/api/checklist/progress/{self.restaurant_id}",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    progress = data["progress"]
                    print(f"✅ Overall progress retrieved")
                    
                    for category_type, stats in progress.items():
                        completion = stats["completionPercentage"]
                        critical_completion = stats["criticalCompletionPercentage"]
                        print(f"   {category_type}: {completion}% complete ({critical_completion}% critical)")
                    
                    # Test foundational progress
                    async with self.session.get(
                        f"{BASE_URL}/api/checklist/progress/{self.restaurant_id}?type=foundational",
                        headers=self.get_auth_headers()
                    ) as response:
                        if response.status == 200:
                            print(f"✅ Foundational progress filter works")
                            return True
                        else:
                            print(f"❌ Foundational progress filter failed")
                            return False
                else:
                    error_data = await response.json()
                    print(f"❌ Failed: {error_data}")
                    return False

        except Exception as e:
            print(f"❌ Progress test error: {e}")
            return False

    async def run_all_tests(self):
        """Run all checklist endpoint tests"""
        print("🚀 Starting Checklist API Tests")
        print("=" * 50)
        
        await self.setup_session()
        
        try:
            # Login first
            if not await self.login():
                print("❌ Cannot proceed without login")
                return False
            
            # Run all tests
            tests = [
                self.test_get_categories,
                self.test_get_category_items,
                self.test_categories_with_items,
                self.test_update_item_status,
                self.test_get_restaurant_status,
                self.test_get_progress
            ]
            
            results = []
            for test in tests:
                result = await test()
                results.append(result)
            
            # Summary
            print("\n" + "=" * 50)
            print("📊 TEST SUMMARY")
            print("=" * 50)
            
            passed = sum(results)
            total = len(results)
            
            print(f"✅ Passed: {passed}/{total}")
            if passed == total:
                print("🎉 All checklist endpoint tests passed!")
                return True
            else:
                print(f"❌ {total - passed} tests failed")
                return False
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test function"""
    tester = ChecklistTester()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)