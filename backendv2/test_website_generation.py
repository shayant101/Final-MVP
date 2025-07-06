#!/usr/bin/env python3
"""
Test Website Generation End-to-End
Tests the complete website generation flow to verify the fix
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database, connect_to_mongo
from app.services.ai_website_generator import ai_website_generator
from app.models_website_builder import WebsiteGenerationRequest

async def test_website_generation():
    """Test the complete website generation flow"""
    print("🧪 TESTING WEBSITE GENERATION")
    print("=" * 50)
    
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        print("✅ Connected to database")
        
        # Get Roma Trattoria data (we know this exists)
        restaurant = await db.restaurants.find_one({"name": "Roma Trattoria"})
        if not restaurant:
            print("❌ Roma Trattoria not found")
            return
        
        print(f"✅ Found restaurant: {restaurant['name']}")
        print(f"   Restaurant ID: {restaurant['_id']}")
        print(f"   User ID: {restaurant['user_id']}")
        
        # Get menu items
        menu_items = await db.menu_items.find({"restaurant_id": str(restaurant['_id'])}).to_list(length=None)
        print(f"✅ Found {len(menu_items)} menu items")
        
        # Prepare restaurant data for AI generation
        restaurant_data = {
            **restaurant,
            "menu_items": menu_items,
            "restaurant_id": str(restaurant['_id'])
        }
        
        print("\n🤖 Testing AI Website Generation...")
        print("-" * 30)
        
        # Test the AI website generator directly
        website_result = await ai_website_generator.generate_complete_website(restaurant_data)
        
        if website_result.get("success"):
            print("✅ Website generation SUCCESSFUL!")
            print(f"   Website ID: {website_result.get('website_id')}")
            print(f"   Restaurant Name: {website_result.get('restaurant_name')}")
            print(f"   Design Category: {website_result.get('design_analysis', {}).get('recommended_category')}")
            print(f"   Generation Method: {website_result.get('generation_method', 'AI')}")
            print(f"   Sections Generated: {len(website_result.get('website_sections', {}).get('generated_sections', {}))}")
            
            if website_result.get('note'):
                print(f"   Note: {website_result.get('note')}")
                
        else:
            print("❌ Website generation FAILED!")
            print(f"   Error: {website_result}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_website_generation())