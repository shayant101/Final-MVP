#!/usr/bin/env python3

import requests
import json

def test_openai_grader():
    """Test the OpenAI Google Profile Grader"""
    
    # Test data
    test_data = {
        "restaurant_name": "Al Watan Halal Tandoori Restaurant", 
        "google_business_url": "https://share.google/9OYvHvRbbzWr1r49N",
        "mode": "openai"
    }
    
    try:
        print("🧪 Testing OpenAI Google Profile Grader...")
        print(f"📍 Restaurant: {test_data['restaurant_name']}")
        print(f"🔗 URL: {test_data['google_business_url']}")
        print(f"⚙️  Mode: {test_data['mode']}")
        print("-" * 50)
        
        # Make request to the backend
        response = requests.post(
            "http://localhost:8000/api/google-profile/grade",
            json=test_data,
            timeout=30
        )
        
        print(f"📋 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS! OpenAI Analysis Results:")
            print(f"🎯 Overall Score: {result.get('overall_score', 'N/A')}")
            print(f"📊 Grade: {result.get('grade', 'N/A')}")
            print(f"⚠️  Priority: {result.get('priority', 'N/A')}")
            print(f"🔧 Analysis Method: {result.get('analysis_method', 'N/A')}")
            print(f"🏷️  Version: {result.get('grader_version', 'N/A')}")
            
            if result.get('issues'):
                print(f"🚨 Issues Found ({len(result['issues'])}):")
                for i, issue in enumerate(result['issues'][:3], 1):
                    print(f"   {i}. {issue}")
            else:
                print("🚨 Issues Found: None")
            
            if result.get('recommendations'):
                print(f"💡 Recommendations ({len(result['recommendations'])}):")
                for i, rec in enumerate(result['recommendations'][:3], 1):
                    print(f"   {i}. {rec}")
            else:
                print("💡 Recommendations: None")
                    
            if result.get('strengths'):
                print(f"💪 Strengths ({len(result['strengths'])}):")
                for i, strength in enumerate(result['strengths'][:3], 1):
                    print(f"   {i}. {strength}")
            else:
                print("💪 Strengths: None")
            
            # Show raw OpenAI response for debugging
            if result.get('openai_analysis'):
                print("\n📜 Raw OpenAI Analysis (sample):")
                openai_data = result['openai_analysis']
                print(f"   Overall Grade: {openai_data.get('overall_grade', {})}")
                print(f"   Snapshot: {list(openai_data.get('snapshot', {}).keys())}")
                print(f"   Grades: {list(openai_data.get('grades', {}).keys())}")
                print(f"   Quick Wins: {len(openai_data.get('quick_wins', []))} items")
                print(f"   Longer Term: {len(openai_data.get('longer_term_plays', []))} items")
            
            print("\n🎉 OpenAI integration is working correctly!")
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this might be normal for OpenAI processing")
    except Exception as e:
        print(f"❌ Error testing OpenAI grader: {e}")

if __name__ == "__main__":
    test_openai_grader()