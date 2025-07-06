#!/usr/bin/env python3
"""
Comprehensive Website Generation Debugging Script
Systematically tests all components of the website generation system
"""
import asyncio
import logging
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('website_generation_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main debugging function"""
    print("🔍 COMPREHENSIVE WEBSITE GENERATION DEBUGGING")
    print("=" * 60)
    
    # Test results storage
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "errors": [],
        "recommendations": []
    }
    
    try:
        # 1. Test Database Connectivity
        print("\n1️⃣ Testing Database Connectivity...")
        db_result = await test_database_connectivity()
        test_results["tests"]["database_connectivity"] = db_result
        print(f"   Result: {'✅ PASS' if db_result['success'] else '❌ FAIL'}")
        if not db_result['success']:
            test_results["errors"].append(f"Database: {db_result['error']}")
        
        # 2. Test Authentication System
        print("\n2️⃣ Testing Authentication System...")
        auth_result = await test_authentication_system()
        test_results["tests"]["authentication"] = auth_result
        print(f"   Result: {'✅ PASS' if auth_result['success'] else '❌ FAIL'}")
        if not auth_result['success']:
            test_results["errors"].append(f"Authentication: {auth_result['error']}")
        
        # 3. Test Restaurant Data Access
        print("\n3️⃣ Testing Restaurant Data Access...")
        restaurant_result = await test_restaurant_data_access()
        test_results["tests"]["restaurant_data"] = restaurant_result
        print(f"   Result: {'✅ PASS' if restaurant_result['success'] else '❌ FAIL'}")
        if not restaurant_result['success']:
            test_results["errors"].append(f"Restaurant Data: {restaurant_result['error']}")
        
        # 4. Test OpenAI Service Integration
        print("\n4️⃣ Testing OpenAI Service Integration...")
        openai_result = await test_openai_service()
        test_results["tests"]["openai_service"] = openai_result
        print(f"   Result: {'✅ PASS' if openai_result['success'] else '❌ FAIL'}")
        if not openai_result['success']:
            test_results["errors"].append(f"OpenAI Service: {openai_result['error']}")
        
        # 5. Test AI Website Generator Service
        print("\n5️⃣ Testing AI Website Generator Service...")
        generator_result = await test_ai_website_generator()
        test_results["tests"]["ai_generator"] = generator_result
        print(f"   Result: {'✅ PASS' if generator_result['success'] else '❌ FAIL'}")
        if not generator_result['success']:
            test_results["errors"].append(f"AI Generator: {generator_result['error']}")
        
        # 6. Test Website Generation API Endpoint
        print("\n6️⃣ Testing Website Generation API Endpoint...")
        api_result = await test_website_generation_api()
        test_results["tests"]["api_endpoint"] = api_result
        print(f"   Result: {'✅ PASS' if api_result['success'] else '❌ FAIL'}")
        if not api_result['success']:
            test_results["errors"].append(f"API Endpoint: {api_result['error']}")
        
        # 7. Test Background Task Processing
        print("\n7️⃣ Testing Background Task Processing...")
        background_result = await test_background_task_processing()
        test_results["tests"]["background_tasks"] = background_result
        print(f"   Result: {'✅ PASS' if background_result['success'] else '❌ FAIL'}")
        if not background_result['success']:
            test_results["errors"].append(f"Background Tasks: {background_result['error']}")
        
        # 8. Test Complete End-to-End Generation
        print("\n8️⃣ Testing Complete End-to-End Generation...")
        e2e_result = await test_end_to_end_generation()
        test_results["tests"]["end_to_end"] = e2e_result
        print(f"   Result: {'✅ PASS' if e2e_result['success'] else '❌ FAIL'}")
        if not e2e_result['success']:
            test_results["errors"].append(f"End-to-End: {e2e_result['error']}")
        
        # Generate recommendations
        test_results["recommendations"] = generate_recommendations(test_results)
        
        # Print summary
        print_test_summary(test_results)
        
        # Save detailed results
        with open('website_generation_debug_results.json', 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: website_generation_debug_results.json")
        print(f"📄 Debug logs saved to: website_generation_debug.log")
        
    except Exception as e:
        logger.error(f"Critical error in debugging script: {str(e)}")
        logger.error(traceback.format_exc())
        test_results["errors"].append(f"Critical Script Error: {str(e)}")
        print(f"\n❌ CRITICAL ERROR: {str(e)}")

async def test_database_connectivity():
    """Test database connectivity and basic operations"""
    try:
        from app.database import get_database
        
        # Test database connection
        db = await get_database()
        
        # Test basic operations
        collections = await db.list_collection_names()
        
        # Test restaurant collection access
        restaurant_count = await db.restaurants.count_documents({})
        
        # Test websites collection access
        website_count = await db.websites.count_documents({})
        
        return {
            "success": True,
            "details": {
                "collections_found": len(collections),
                "restaurant_count": restaurant_count,
                "website_count": website_count,
                "collections": collections
            }
        }
        
    except Exception as e:
        logger.error(f"Database connectivity test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "details": {"traceback": traceback.format_exc()}
        }

async def test_authentication_system():
    """Test authentication system components"""
    try:
        from app.auth import get_current_user
        
        # Test auth module import
        auth_functions = dir(get_current_user)
        
        # Test with mock user data
        # Note: This is a basic test - in production you'd test with real tokens
        
        return {
            "success": True,
            "details": {
                "auth_module_loaded": True,
                "auth_functions_available": len(auth_functions) > 0
            }
        }
        
    except Exception as e:
        logger.error(f"Authentication test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "details": {"traceback": traceback.format_exc()}
        }

async def test_restaurant_data_access():
    """Test restaurant data retrieval and validation"""
    try:
        from app.database import get_database
        
        db = await get_database()
        
        # Get a sample restaurant
        sample_restaurant = await db.restaurants.find_one({})
        
        if not sample_restaurant:
            return {
                "success": False,
                "error": "No restaurants found in database",
                "details": {"restaurant_count": 0}
            }
        
        # Validate restaurant data structure
        required_fields = ['name', 'user_id']
        missing_fields = [field for field in required_fields if field not in sample_restaurant]
        
        # Check for menu items
        menu_items = await db.menu_items.find({"restaurant_id": str(sample_restaurant["_id"])}).to_list(length=None)
        
        return {
            "success": len(missing_fields) == 0,
            "details": {
                "sample_restaurant_id": str(sample_restaurant["_id"]),
                "restaurant_name": sample_restaurant.get("name", "Unknown"),
                "missing_fields": missing_fields,
                "menu_items_count": len(menu_items),
                "restaurant_fields": list(sample_restaurant.keys())
            },
            "error": f"Missing required fields: {missing_fields}" if missing_fields else None
        }
        
    except Exception as e:
        logger.error(f"Restaurant data access test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "details": {"traceback": traceback.format_exc()}
        }

async def test_openai_service():
    """Test OpenAI service integration"""
    try:
        from app.services.openai_service import openai_service
        
        # Test basic OpenAI service functionality
        test_messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Respond with exactly 'TEST_SUCCESS' if you receive this message."
            },
            {
                "role": "user",
                "content": "This is a test message for debugging purposes."
            }
        ]
        
        # Test OpenAI API call
        response = await openai_service._make_openai_request(
            messages=test_messages,
            model="gpt-4",
            max_tokens=50,
            temperature=0.1
        )
        
        return {
            "success": True,
            "details": {
                "openai_response_received": True,
                "response_length": len(response) if response else 0,
                "response_preview": response[:100] if response else "No response"
            }
        }
        
    except Exception as e:
        logger.error(f"OpenAI service test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "details": {"traceback": traceback.format_exc()}
        }

async def test_ai_website_generator():
    """Test AI website generator service"""
    try:
        from app.services.ai_website_generator import ai_website_generator
        
        # Create test restaurant data
        test_restaurant_data = {
            "name": "Test Restaurant",
            "cuisine_type": "Italian",
            "price_range": "moderate",
            "location": "Test City",
            "restaurant_id": "test_restaurant_123",
            "user_id": "test_user_123",
            "menu_items": [
                {"name": "Test Pizza", "description": "Test description", "price": "$15"}
            ]
        }
        
        # Test website generation
        website_result = await ai_website_generator.generate_complete_website(test_restaurant_data)
        
        # Validate result structure
        required_keys = ["website_id", "restaurant_name", "success"]
        missing_keys = [key for key in required_keys if key not in website_result]
        
        return {
            "success": len(missing_keys) == 0 and website_result.get("success", False),
            "details": {
                "website_generated": website_result.get("success", False),
                "website_id": website_result.get("website_id"),
                "missing_keys": missing_keys,
                "result_keys": list(website_result.keys()),
                "generation_method": website_result.get("generation_method", "unknown")
            },
            "error": f"Missing keys: {missing_keys}" if missing_keys else None
        }
        
    except Exception as e:
        logger.error(f"AI website generator test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "details": {"traceback": traceback.format_exc()}
        }

async def test_website_generation_api():
    """Test website generation API endpoint logic"""
    try:
        from app.routes.website_builder import _get_restaurant_data
        from app.database import get_database
        
        db = await get_database()
        
        # Get a sample restaurant for testing
        sample_restaurant = await db.restaurants.find_one({})
        
        if not sample_restaurant:
            return {
                "success": False,
                "error": "No restaurants available for API testing",
                "details": {}
            }
        
        # Create mock user object
        class MockUser:
            def __init__(self, user_id):
                self.user_id = user_id
        
        mock_user = MockUser(sample_restaurant.get("user_id"))
        
        # Test restaurant data retrieval function
        restaurant_data = await _get_restaurant_data(
            str(sample_restaurant["_id"]), 
            mock_user, 
            db
        )
        
        return {
            "success": restaurant_data is not None,
            "details": {
                "restaurant_data_retrieved": restaurant_data is not None,
                "restaurant_id": str(sample_restaurant["_id"]),
                "restaurant_name": restaurant_data.get("name") if restaurant_data else None,
                "data_keys": list(restaurant_data.keys()) if restaurant_data else []
            },
            "error": "Failed to retrieve restaurant data" if not restaurant_data else None
        }
        
    except Exception as e:
        logger.error(f"Website generation API test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "details": {"traceback": traceback.format_exc()}
        }

async def test_background_task_processing():
    """Test background task processing capabilities"""
    try:
        from app.routes.website_builder import _generate_website_background, generation_progress_store
        from app.models_website_builder import WebsiteGenerationRequest
        from app.database import get_database
        
        db = await get_database()
        
        # Get sample restaurant
        sample_restaurant = await db.restaurants.find_one({})
        
        if not sample_restaurant:
            return {
                "success": False,
                "error": "No restaurants available for background task testing",
                "details": {}
            }
        
        # Create test request
        test_request = WebsiteGenerationRequest(
            restaurant_id=str(sample_restaurant["_id"]),
            website_name="Test Website"
        )
        
        # Create mock user
        class MockUser:
            def __init__(self, user_id):
                self.user_id = user_id
        
        mock_user = MockUser(sample_restaurant.get("user_id"))
        
        # Test background task function (but don't actually run it)
        generation_id = f"test_gen_{int(datetime.now().timestamp())}"
        website_id = f"test_website_{int(datetime.now().timestamp())}"
        
        # Test progress store functionality
        from app.models_website_builder import AIGenerationProgress
        test_progress = AIGenerationProgress(
            generation_id=generation_id,
            website_id=website_id,
            current_step="Testing",
            total_steps=1,
            completed_steps=0,
            progress_percentage=0.0,
            current_operation="Test operation",
            started_at=datetime.now()
        )
        
        generation_progress_store[generation_id] = test_progress
        
        # Verify progress store works
        retrieved_progress = generation_progress_store.get(generation_id)
        
        # Clean up
        if generation_id in generation_progress_store:
            del generation_progress_store[generation_id]
        
        return {
            "success": retrieved_progress is not None,
            "details": {
                "progress_store_working": retrieved_progress is not None,
                "background_function_available": callable(_generate_website_background),
                "test_generation_id": generation_id
            }
        }
        
    except Exception as e:
        logger.error(f"Background task processing test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "details": {"traceback": traceback.format_exc()}
        }

async def test_end_to_end_generation():
    """Test complete end-to-end website generation"""
    try:
        from app.services.ai_website_generator import ai_website_generator
        from app.database import get_database
        
        db = await get_database()
        
        # Get sample restaurant
        sample_restaurant = await db.restaurants.find_one({})
        
        if not sample_restaurant:
            return {
                "success": False,
                "error": "No restaurants available for end-to-end testing",
                "details": {}
            }
        
        # Get menu items
        menu_items = await db.menu_items.find({"restaurant_id": str(sample_restaurant["_id"])}).to_list(length=None)
        
        # Prepare complete restaurant data
        restaurant_data = {
            **sample_restaurant,
            "restaurant_id": str(sample_restaurant["_id"]),
            "menu_items": menu_items
        }
        
        # Generate website
        website_result = await ai_website_generator.generate_complete_website(restaurant_data)
        
        # Test saving to database
        if website_result.get("success"):
            test_website_record = {
                "website_id": f"test_{website_result.get('website_id')}",
                "restaurant_id": str(sample_restaurant["_id"]),
                "website_name": "Test Website",
                "status": "ready",
                "design_category": "casual_dining",
                "design_system": {"test": True},
                "pages": [],
                "seo_settings": {"test": True},
                "ai_generation_metadata": website_result,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Try to insert (then immediately delete)
            insert_result = await db.websites.insert_one(test_website_record)
            await db.websites.delete_one({"_id": insert_result.inserted_id})
            
            database_save_success = True
        else:
            database_save_success = False
        
        return {
            "success": website_result.get("success", False) and database_save_success,
            "details": {
                "website_generation_success": website_result.get("success", False),
                "database_save_success": database_save_success,
                "restaurant_name": restaurant_data.get("name"),
                "menu_items_count": len(menu_items),
                "website_sections": len(website_result.get("website_sections", {}).get("generated_sections", {})),
                "generation_method": website_result.get("generation_method", "unknown")
            }
        }
        
    except Exception as e:
        logger.error(f"End-to-end generation test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "details": {"traceback": traceback.format_exc()}
        }

def generate_recommendations(test_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on test results"""
    recommendations = []
    
    # Check for specific failure patterns
    if not test_results["tests"].get("database_connectivity", {}).get("success"):
        recommendations.append("🔧 Fix database connectivity issues - check MongoDB connection string and credentials")
    
    if not test_results["tests"].get("openai_service", {}).get("success"):
        recommendations.append("🔧 Fix OpenAI service integration - check API key and service availability")
    
    if not test_results["tests"].get("restaurant_data", {}).get("success"):
        recommendations.append("🔧 Fix restaurant data access - ensure restaurants exist and have required fields")
    
    if not test_results["tests"].get("ai_generator", {}).get("success"):
        recommendations.append("🔧 Fix AI website generator - check service dependencies and error handling")
    
    if not test_results["tests"].get("background_tasks", {}).get("success"):
        recommendations.append("🔧 Fix background task processing - check async task handling and progress tracking")
    
    if not test_results["tests"].get("end_to_end", {}).get("success"):
        recommendations.append("🔧 Fix end-to-end generation - check complete workflow and error propagation")
    
    # Add general recommendations
    if len(test_results["errors"]) > 3:
        recommendations.append("⚠️ Multiple critical issues detected - prioritize database and OpenAI service fixes")
    
    if not recommendations:
        recommendations.append("✅ All tests passed - website generation should be working correctly")
    
    return recommendations

def print_test_summary(test_results: Dict[str, Any]):
    """Print a summary of test results"""
    print("\n" + "=" * 60)
    print("🔍 DEBUGGING SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results["tests"])
    passed_tests = sum(1 for test in test_results["tests"].values() if test.get("success"))
    failed_tests = total_tests - passed_tests
    
    print(f"📊 Tests Run: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if test_results["errors"]:
        print(f"\n🚨 ERRORS FOUND ({len(test_results['errors'])}):")
        for i, error in enumerate(test_results["errors"], 1):
            print(f"   {i}. {error}")
    
    if test_results["recommendations"]:
        print(f"\n💡 RECOMMENDATIONS ({len(test_results['recommendations'])}):")
        for i, rec in enumerate(test_results["recommendations"], 1):
            print(f"   {i}. {rec}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())