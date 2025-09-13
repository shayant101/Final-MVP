#!/usr/bin/env python3
"""
Test script for Google Profile Grader
Tests the standalone Google Profile grading functionality
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.google_profile_grader import google_profile_grader

async def test_google_profile_grader():
    """Test the Google Profile grader with various scenarios"""
    
    print("🧪 Testing Google Profile Grader")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Valid Restaurant Profile",
            "restaurant_name": "Joe's Pizza",
            "google_business_url": "https://www.google.com/maps/place/Joe's+Pizza/@40.7505,-73.9934,17z"
        },
        {
            "name": "Short URL Format",
            "restaurant_name": "Pizza Palace",
            "google_business_url": "https://g.co/kgs/abc123"
        },
        {
            "name": "No URL Provided",
            "restaurant_name": "Test Restaurant",
            "google_business_url": ""
        },
        {
            "name": "Invalid URL Format",
            "restaurant_name": "Bad URL Restaurant",
            "google_business_url": "https://example.com/not-google"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            result = await google_profile_grader.grade_google_profile(
                restaurant_name=test_case["restaurant_name"],
                google_business_url=test_case["google_business_url"]
            )
            
            print(f"✅ Overall Score: {result['overall_score']}/100")
            print(f"📊 Grade: {result['grade']}")
            print(f"🎯 Priority: {result['priority']}")
            print(f"🔧 Analysis Method: {result['analysis_method']}")
            
            if result.get('scraped_data'):
                scraped = result['scraped_data']
                print(f"📋 Business Name: {scraped.get('business_name', 'N/A')}")
                print(f"⭐ Rating: {scraped.get('rating', 'N/A')}")
                print(f"👥 Reviews: {scraped.get('review_count', 'N/A')}")
                print(f"🏷️ Categories: {', '.join(scraped.get('categories', []))}")
            
            if result.get('issues'):
                print(f"⚠️ Issues ({len(result['issues'])}):")
                for issue in result['issues'][:3]:  # Show first 3 issues
                    print(f"   - {issue}")
            
            if result.get('recommendations'):
                print(f"💡 Recommendations ({len(result['recommendations'])}):")
                for rec in result['recommendations'][:3]:  # Show first 3 recommendations
                    print(f"   - {rec}")
            
            if result.get('strengths'):
                print(f"💪 Strengths ({len(result['strengths'])}):")
                for strength in result['strengths'][:2]:  # Show first 2 strengths
                    print(f"   - {strength}")
                    
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()

async def test_api_endpoint():
    """Test the Google Profile grading API endpoint"""
    print("\n🌐 Testing API Endpoint")
    print("=" * 50)
    
    import httpx
    
    test_data = {
        "restaurant_name": "Test Restaurant API",
        "google_business_url": "https://maps.google.com/place/test"
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
                print(f"🔧 Method: {result['analysis_method']}")
            else:
                print(f"❌ API returned status code: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")

async def test_quick_check():
    """Test the quick check endpoint"""
    print("\n⚡ Testing Quick Check Endpoint")
    print("=" * 50)
    
    import httpx
    
    test_data = {
        "restaurant_name": "Quick Check Test",
        "google_business_url": "https://maps.google.com/place/test"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/google-profile/quick-check",
                json=test_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Quick Check successful")
                print(f"🔍 Profile Accessible: {result['profile_accessible']}")
                print(f"📋 Business Name Found: {result['business_name_found']}")
                print(f"⭐ Rating Available: {result['rating_available']}")
                print(f"👥 Review Count Available: {result['review_count_available']}")
                print(f"🏷️ Categories Found: {result['categories_found']}")
                
                if result.get('error'):
                    print(f"⚠️ Error: {result['error']}")
            else:
                print(f"❌ Quick check returned status code: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Quick check test failed: {str(e)}")

async def test_scoring_criteria():
    """Test the scoring criteria endpoint"""
    print("\n📋 Testing Scoring Criteria Endpoint")
    print("=" * 50)
    
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/api/google-profile/scoring-criteria",
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Scoring criteria retrieved successfully")
                print(f"📊 Total Possible Points: {result['total_possible_points']}")
                print(f"🎯 Score Capped At: {result['score_capped_at']}")
                
                print("\n📊 Scoring Breakdown:")
                for component, details in result['scoring_breakdown'].items():
                    print(f"  {component.replace('_', ' ').title()}: {details['max_points']} pts ({details['weight']})")
                
                print("\n🎓 Grade Scale:")
                for grade, description in result['grade_scale'].items():
                    print(f"  {grade}: {description}")
            else:
                print(f"❌ Scoring criteria returned status code: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Scoring criteria test failed: {str(e)}")

async def main():
    """Run all tests"""
    print("🚀 Starting Google Profile Grader Tests")
    print("=" * 60)
    
    # Test the grader service directly
    await test_google_profile_grader()
    
    # Test API endpoints
    await test_api_endpoint()
    await test_quick_check()
    await test_scoring_criteria()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())