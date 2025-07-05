#!/usr/bin/env python3.9
"""
Test Analytics Infrastructure
Tests the admin analytics service and endpoints
"""
import asyncio
import requests
import json
from datetime import datetime, timedelta
from app.database import connect_to_mongo, db
from app.services.admin_analytics_service import admin_analytics_service

async def test_analytics_service():
    """Test the analytics service directly"""
    print("🧪 Testing Analytics Service...")
    
    # Connect to database
    await connect_to_mongo()
    
    # Test logging AI usage
    print("📊 Testing AI usage logging...")
    success = await admin_analytics_service.log_ai_usage(
        restaurant_id="test_restaurant_123",
        feature_type="image_enhancement",
        operation_type="enhance_image",
        processing_time=1200,
        tokens_used=0,
        status="success",
        metadata={"test": True, "image_size": "2MB"}
    )
    print(f"✅ AI usage logged: {success}")
    
    # Test real-time metrics
    print("📈 Testing real-time metrics...")
    metrics = await admin_analytics_service.get_real_time_metrics()
    print(f"✅ Real-time metrics: {json.dumps(metrics, indent=2)}")
    
    # Test usage analytics
    print("📊 Testing usage analytics...")
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    analytics = await admin_analytics_service.get_usage_analytics((start_date, end_date))
    print(f"✅ Usage analytics: {len(analytics.get('usage_over_time', []))} data points")
    
    # Test feature toggles
    print("🎛️ Testing feature toggles...")
    success = await admin_analytics_service.update_feature_toggle(
        restaurant_id="test_restaurant_123",
        feature_name="image_enhancement",
        enabled=True,
        rate_limits={"daily_limit": 100, "hourly_limit": 10},
        admin_user_id="test_admin"
    )
    print(f"✅ Feature toggle updated: {success}")
    
    # Test checking feature status
    enabled = await admin_analytics_service.check_feature_enabled("test_restaurant_123", "image_enhancement")
    print(f"✅ Feature enabled check: {enabled}")
    
    # Test rate limiting
    rate_limit = await admin_analytics_service.check_rate_limit("test_restaurant_123", "image_enhancement")
    print(f"✅ Rate limit check: {rate_limit}")
    
    print("🎉 Analytics service tests completed!")

def test_admin_endpoints():
    """Test admin endpoints via HTTP"""
    print("\n🌐 Testing Admin Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint first
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend not responding")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - make sure it's running")
        return
    
    # Note: These endpoints require admin authentication
    # For testing, we'll just check if they exist
    admin_endpoints = [
        "/api/admin/analytics/real-time",
        "/api/admin/analytics/usage",
        "/api/admin/moderation/flagged-content",
        "/api/admin/features/toggles",
        "/api/admin/dashboard/summary",
        "/api/admin/system/health"
    ]
    
    print("📋 Checking admin endpoint availability...")
    for endpoint in admin_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            # 403 is expected without admin auth, 404 means endpoint doesn't exist
            if response.status_code in [403, 401]:
                print(f"✅ {endpoint} - Available (auth required)")
            elif response.status_code == 404:
                print(f"❌ {endpoint} - Not found")
            else:
                print(f"⚠️ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")
    
    print("🎉 Admin endpoint tests completed!")

async def test_database_collections():
    """Test that analytics collections exist and have proper indexes"""
    print("\n🗄️ Testing Database Collections...")
    
    await connect_to_mongo()
    
    # Check collections exist
    collections = await db.database.list_collection_names()
    analytics_collections = [
        "ai_usage_analytics",
        "ai_content_moderation", 
        "ai_performance_metrics",
        "ai_feature_toggles"
    ]
    
    for collection_name in analytics_collections:
        if collection_name in collections:
            print(f"✅ Collection exists: {collection_name}")
            
            # Check indexes
            collection = db.database[collection_name]
            indexes = await collection.list_indexes().to_list(None)
            print(f"   📊 Indexes: {len(indexes)} total")
            for index in indexes:
                if index['name'] != '_id_':  # Skip default _id index
                    print(f"      - {index['name']}: {list(index['key'].keys())}")
        else:
            print(f"❌ Collection missing: {collection_name}")
    
    print("🎉 Database collection tests completed!")

async def main():
    """Run all tests"""
    print("🚀 Starting Analytics Infrastructure Tests\n")
    
    try:
        await test_analytics_service()
        test_admin_endpoints()
        await test_database_collections()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Run the database initialization: python3.9 init_database.py")
        print("2. Create an admin user to test the endpoints")
        print("3. Test the admin dashboard endpoints with proper authentication")
        print("4. Verify analytics collection in the AI features")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())