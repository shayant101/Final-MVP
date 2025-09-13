#!/usr/bin/env python3
"""
Test a specific Google Profile URL through the grader
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.google_profile_grader import google_profile_grader

async def test_specific_profile():
    """Test the provided Google Profile URL"""
    
    print("🧪 Testing Specific Google Profile")
    print("=" * 50)
    
    # The provided Google Maps URL
    test_url = "https://maps.app.goo.gl/nRnCfUfAWF5v2AnC9"
    restaurant_name = "Al Watan Halal Tandoori Restaurant"  # We know the name from previous test
    
    print(f"🔗 Testing URL: {test_url}")
    print(f"📋 Restaurant Name: {restaurant_name}")
    print("-" * 50)
    
    try:
        result = await google_profile_grader.grade_google_profile(
            restaurant_name=restaurant_name,
            google_business_url=test_url
        )
        
        print(f"✅ **OVERALL RESULTS**")
        print(f"📊 Score: {result['overall_score']}/100")
        print(f"🎯 Grade: {result['grade']}")
        print(f"🚨 Priority: {result['priority']}")
        print(f"🔧 Analysis Method: {result['analysis_method']}")
        print()
        
        # Show scraped data if available
        if result.get('scraped_data'):
            scraped = result['scraped_data']
            print(f"📋 **SCRAPED PROFILE DATA**")
            print(f"   Business Name: {scraped.get('business_name', 'N/A')}")
            print(f"   Rating: {scraped.get('rating', 'N/A')}")
            print(f"   Review Count: {scraped.get('review_count', 'N/A')}")
            print(f"   Categories: {', '.join(scraped.get('categories', []))}")
            print(f"   Profile URL: {scraped.get('profile_url', 'N/A')}")
            print()
        
        # Show detailed score breakdown if available
        if result.get('score_breakdown'):
            breakdown = result['score_breakdown']
            print(f"📊 **DETAILED SCORE BREAKDOWN**")
            for component, details in breakdown.items():
                component_name = component.replace('_', ' ').title()
                percentage = int((details['score'] / details['max']) * 100)
                print(f"   {component_name}: {details['score']}/{details['max']} pts ({percentage}%) - Weight: {details['weight']}")
            print()
        
        # Show strengths
        if result.get('strengths'):
            print(f"💪 **PROFILE STRENGTHS** ({len(result['strengths'])})")
            for i, strength in enumerate(result['strengths'], 1):
                print(f"   {i}. {strength}")
            print()
        
        # Show issues
        if result.get('issues'):
            print(f"⚠️ **ISSUES FOUND** ({len(result['issues'])})")
            for i, issue in enumerate(result['issues'], 1):
                print(f"   {i}. {issue}")
            print()
        
        # Show recommendations
        if result.get('recommendations'):
            print(f"💡 **RECOMMENDATIONS** ({len(result['recommendations'])})")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"   {i}. {rec}")
            print()
                    
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_via_api():
    """Test the same URL via the API endpoint"""
    print("\n🌐 Testing via API Endpoint")
    print("=" * 50)
    
    import httpx
    
    test_data = {
        "restaurant_name": "Al Watan Halal Tandoori Restaurant",
        "google_business_url": "https://maps.app.goo.gl/nRnCfUfAWF5v2AnC9"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/google-profile/grade",
                json=test_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API Response successful")
                print(f"📊 Score: {result['overall_score']}/100")
                print(f"🎯 Grade: {result['grade']}")
                print(f"🚨 Priority: {result['priority']}")
                print(f"🔧 Method: {result['analysis_method']}")
                
                if result.get('scraped_data'):
                    scraped = result['scraped_data']
                    print(f"\n📋 API Scraped Data:")
                    print(f"   Business Name: {scraped.get('business_name', 'N/A')}")
                    print(f"   Rating: {scraped.get('rating', 'N/A')}")
                    print(f"   Reviews: {scraped.get('review_count', 'N/A')}")
            else:
                print(f"❌ API returned status code: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")

async def main():
    """Run the test"""
    print("🚀 Testing Specific Google Profile URL")
    print("🔗 URL: https://maps.app.goo.gl/nRnCfUfAWF5v2AnC9")
    print("=" * 60)
    
    # Test directly via service
    await test_specific_profile()
    
    # Test via API
    await test_via_api()
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(main())