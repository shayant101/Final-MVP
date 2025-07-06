#!/usr/bin/env python3
"""
Debug script to test website generation and identify the source of errors
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.openai_service import openai_service
from app.services.ai_website_generator import ai_website_generator
from app.database import get_database

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_website_generation_debug():
    """Test website generation with detailed debugging"""
    print("=" * 60)
    print("WEBSITE GENERATION DEBUG TEST")
    print("=" * 60)
    
    # Test 1: Check OpenAI Service Configuration
    print("\n1. Testing OpenAI Service Configuration...")
    try:
        openai_test = await openai_service.test_connection()
        print(f"   OpenAI Status: {openai_test}")
        
        if not openai_test.get('success'):
            print("   ❌ ISSUE FOUND: OpenAI service is not properly configured")
            print("   This is likely the source of website generation errors")
        else:
            print("   ✅ OpenAI service is working correctly")
            
    except Exception as e:
        print(f"   ❌ CRITICAL ERROR: OpenAI service test failed: {str(e)}")
    
    # Test 2: Check Database Connection
    print("\n2. Testing Database Connection...")
    try:
        db = await get_database()
        # Test database access
        test_collection = db.test_collection
        await test_collection.insert_one({"test": "debug", "timestamp": datetime.now()})
        await test_collection.delete_one({"test": "debug"})
        print("   ✅ Database connection is working correctly")
    except Exception as e:
        print(f"   ❌ CRITICAL ERROR: Database connection failed: {str(e)}")
    
    # Test 3: Test Website Generation with Mock Data
    print("\n3. Testing Website Generation Process...")
    try:
        # Create mock restaurant data
        mock_restaurant_data = {
            "name": "Test Restaurant",
            "cuisine_type": "Italian",
            "price_range": "moderate",
            "location": "San Francisco, CA",
            "restaurant_id": "test_restaurant_123",
            "user_id": "test_user_123",
            "menu_items": [
                {"name": "Margherita Pizza", "ingredients": "Fresh mozzarella, tomato sauce, basil"},
                {"name": "Caesar Salad", "ingredients": "Romaine lettuce, parmesan, croutons"}
            ],
            "target_audience": {"age_range": "25-45", "interests": ["food", "dining"]}
        }
        
        print("   Starting website generation...")
        result = await ai_website_generator.generate_complete_website(mock_restaurant_data)
        
        if result.get('success'):
            print("   ✅ Website generation completed successfully")
            print(f"   Generated website ID: {result.get('website_id')}")
            print(f"   Design category: {result.get('design_analysis', {}).get('recommended_category')}")
        else:
            print("   ❌ Website generation failed")
            print(f"   Error details: {result}")
            
    except Exception as e:
        print(f"   ❌ CRITICAL ERROR: Website generation failed: {str(e)}")
        import traceback
        print(f"   Full traceback: {traceback.format_exc()}")
    
    # Test 4: Check Environment Variables
    print("\n4. Checking Environment Variables...")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"   ✅ OPENAI_API_KEY is set (length: {len(openai_key)} characters)")
    else:
        print("   ❌ ISSUE FOUND: OPENAI_API_KEY is not set")
        print("   This explains why website generation is failing")
    
    # Test 5: Check for .env file
    print("\n5. Checking for .env file...")
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file_path):
        print(f"   ✅ .env file found at: {env_file_path}")
        # Read and check contents (without exposing sensitive data)
        with open(env_file_path, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content:
                print("   ✅ OPENAI_API_KEY found in .env file")
            else:
                print("   ❌ OPENAI_API_KEY not found in .env file")
    else:
        print("   ❌ .env file not found")
        print("   This could be why the OpenAI API key is not being loaded")
    
    print("\n" + "=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    
    # Provide diagnosis
    if not openai_key:
        print("🔍 DIAGNOSIS: Missing OpenAI API Key")
        print("   The website generation is failing because the OpenAI API key is not configured.")
        print("   The system is falling back to mock service, which may not provide complete functionality.")
        print("\n💡 SOLUTION:")
        print("   1. Add OPENAI_API_KEY to the .env file in the backendv2 directory")
        print("   2. Restart the backend server to load the new environment variable")
        print("   3. Test the website generation again")
    else:
        print("🔍 DIAGNOSIS: OpenAI API key is configured")
        print("   The issue may be with the API key validity or network connectivity.")

if __name__ == "__main__":
    asyncio.run(test_website_generation_debug())