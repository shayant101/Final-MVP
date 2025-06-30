#!/usr/bin/env python3
"""
Direct test of web scraping functionality without authentication
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_grader_service import ai_grader_service

async def test_scraping_direct():
    """Test web scraping directly without API layer"""
    print("🧪 Testing web scraping functionality directly...")
    
    # Test data
    restaurant_data = {
        "name": "Test Restaurant",
        "website": "https://google.com",
        "google_business_url": "https://maps.google.com/maps?cid=12345",
        "cuisine_type": "Italian",
        "location": "San Francisco, CA",
        "user_id": "test_user_123"
    }
    
    try:
        print(f"📊 Analyzing digital presence for: {restaurant_data['name']}")
        print(f"🌐 Website: {restaurant_data['website']}")
        print(f"📍 Google Business: {restaurant_data['google_business_url']}")
        
        # Call the service directly
        result = await ai_grader_service.analyze_digital_presence(restaurant_data)
        
        print("\n✅ Analysis completed!")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('success'):
            # Print key results
            overall_grade = result.get('overall_grade', {})
            print(f"Overall Grade: {overall_grade.get('grade', 'N/A')} ({overall_grade.get('score', 'N/A')}/100)")
            
            # Check if real data was used
            website_analysis = result.get('website_analysis', {})
            if website_analysis.get('scraped_data'):
                print("🎉 REAL WEB SCRAPING DATA DETECTED!")
                scraped_info = website_analysis.get('scraped_data', {})
                print(f"   - Title: {scraped_info.get('title', 'N/A')}")
                print(f"   - Description: {scraped_info.get('description', 'N/A')[:100]}...")
                print(f"   - Status Code: {scraped_info.get('status_code', 'N/A')}")
            else:
                print("⚠️  Using AI analysis (no real scraping data)")
                
            # Check Google Business data
            google_analysis = result.get('google_business_analysis', {})
            if google_analysis.get('scraped_data'):
                print("🎉 REAL GOOGLE BUSINESS DATA DETECTED!")
                google_info = google_analysis.get('scraped_data', {})
                print(f"   - Business Name: {google_info.get('business_name', 'N/A')}")
                print(f"   - Rating: {google_info.get('rating', 'N/A')}")
            else:
                print("⚠️  Using AI analysis for Google Business (no real scraping data)")
        else:
            print("❌ Analysis failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Direct test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scraping_direct())