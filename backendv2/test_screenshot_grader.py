#!/usr/bin/env python3
"""
Test the screenshot-based Google Profile grader
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.google_profile_grader import google_profile_grader

async def test_screenshot_grader():
    """Test the screenshot-based grader with the Google Maps URL"""
    
    print("🎯 Testing Screenshot-Based Google Profile Grader")
    print("=" * 60)
    
    # Test with the Google Maps URL that should trigger screenshot analysis
    test_url = "https://maps.app.goo.gl/nRnCfUfAWF5v2AnC9"
    restaurant_name = "Al Watan Halal Tandoori Restaurant"
    
    print(f"🔗 Testing URL: {test_url}")
    print(f"📋 Restaurant Name: {restaurant_name}")
    print(f"🔧 Method: Screenshot + Vision AI Analysis")
    print("-" * 60)
    
    try:
        print("📸 Starting screenshot-based grading...")
        result = await google_profile_grader.grade_google_profile(
            restaurant_name=restaurant_name,
            google_business_url=test_url
        )
        
        print(f"\n✅ **GRADING RESULTS**")
        print(f"📊 Overall Score: {result['overall_score']}/100")
        print(f"🎯 Grade: {result['grade']}")
        print(f"🚨 Priority: {result['priority']}")
        print(f"🔧 Analysis Method: {result['analysis_method']}")
        print(f"📋 Grader Version: {result['grader_version']}")
        print()
        
        # Show extracted data from screenshot
        if result.get('scraped_data'):
            scraped = result['scraped_data']
            print(f"📸 **SCREENSHOT EXTRACTED DATA**")
            print(f"   Business Name: {scraped.get('business_name', 'N/A')}")
            print(f"   Rating: {scraped.get('rating', 'N/A')}")
            print(f"   Review Count: {scraped.get('review_count', 'N/A')}")
            print(f"   Categories: {scraped.get('categories', [])}")
            print(f"   Address: {scraped.get('address', 'N/A')}")
            print(f"   Phone: {scraped.get('phone', 'N/A')}")
            print(f"   Website: {scraped.get('website', 'N/A')}")
            print(f"   Verified: {scraped.get('verified', 'N/A')}")
            print(f"   Claimed: {scraped.get('claimed', 'N/A')}")
            print()
        
        # Show detailed score breakdown
        if result.get('score_breakdown'):
            breakdown = result['score_breakdown']
            print(f"📊 **DETAILED SCORE BREAKDOWN**")
            for component, details in breakdown.items():
                component_name = component.replace('_', ' ').title()
                percentage = int((details['score'] / details['max']) * 100) if details['max'] > 0 else 0
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
        
        # Compare with previous results
        if result['analysis_method'] == 'screenshot_vision_analysis':
            print(f"🎉 **SUCCESS**: Screenshot analysis was used!")
            print(f"📈 This should provide much more accurate data than HTML scraping")
        else:
            print(f"⚠️ **NOTE**: Fallback method used: {result['analysis_method']}")
            print(f"📋 Screenshot analysis may not have been triggered")
                    
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Run the screenshot grader test"""
    print("🚀 Testing Screenshot-Based Google Profile Grading")
    print("🔗 URL: https://maps.app.goo.gl/nRnCfUfAWF5v2AnC9")
    print("🎯 Expected: 1.9k reviews, high rating, full business info")
    print("=" * 80)
    
    await test_screenshot_grader()
    
    print("\n" + "=" * 80)
    print("✅ Screenshot grader test completed!")
    print("📸 Check the screenshots/ directory for captured images")

if __name__ == "__main__":
    asyncio.run(main())