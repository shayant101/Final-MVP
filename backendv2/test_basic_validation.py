#!/usr/bin/env python3
"""
Test basic website validation functionality
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_grader_service import ai_grader_service

async def test_basic_validation():
    """Test basic validation approach"""
    print("🧪 Testing basic website validation...")
    
    # Test data with a real accessible website
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
            print(f"Overall Grade: {overall_grade.get('letter_grade', 'N/A')} ({overall_grade.get('score', 'N/A')}/100)")
            
            # Check website analysis
            website_analysis = result.get('component_scores', {}).get('website', {})
            validation_data = website_analysis.get('validation_data', {})
            
            if validation_data.get('validation_method') == 'basic_http_check':
                print("🎉 BASIC VALIDATION WORKING!")
                print(f"   - Website Accessible: {validation_data.get('accessible', False)}")
                print(f"   - Has SSL: {validation_data.get('has_ssl', False)}")
                print(f"   - Status Code: {validation_data.get('status_code', 'N/A')}")
                print(f"   - Response Time: {validation_data.get('response_time', 'N/A')}s")
                print(f"   - Website Score: {website_analysis.get('score', 'N/A')}/100")
            else:
                print("⚠️  Using fallback analysis")
                
            # Check Google Business analysis
            google_analysis = result.get('component_scores', {}).get('google_business', {})
            if google_analysis.get('analysis_method') == 'basic_url_validation':
                print("🎉 GOOGLE BUSINESS BASIC VALIDATION WORKING!")
                print(f"   - URL Provided: {google_analysis.get('url_provided', False)}")
                print(f"   - URL Format Valid: {google_analysis.get('url_format_valid', False)}")
                print(f"   - Google Business Score: {google_analysis.get('score', 'N/A')}/100")
            else:
                print("⚠️  Using fallback Google Business analysis")
                
        else:
            print("❌ Analysis failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_validation())