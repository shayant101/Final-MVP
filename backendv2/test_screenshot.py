#!/usr/bin/env python3
"""
Test script for screenshot service
Tests capturing screenshots of Google Business Profile pages
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.screenshot_service import screenshot_service

async def test_google_business_screenshot():
    """Test screenshot capture with the Bee & Tea Google Business Profile"""
    
    print("🧪 Testing Google Business Profile Screenshot Capture")
    print("=" * 60)
    
    # Test URL - the g.co link that redirects to Google Business Profile
    test_url = "https://g.co/kgs/5go7bJx"
    
    print(f"📍 Testing URL: {test_url}")
    print("⏳ Capturing screenshot...")
    
    try:
        # Test the screenshot capture
        result = await screenshot_service.test_screenshot_capture(test_url)
        
        print("\n📊 Test Results:")
        print("-" * 40)
        
        if result["status"] == "success":
            print("✅ Screenshot capture: SUCCESS")
            print(f"📁 File saved to: {result['file_path']}")
            print(f"📄 Page title: {result['page_title']}")
            print(f"🔗 Final URL: {result['final_url']}")
            print(f"📏 Page dimensions: {result['page_dimensions']}")
            print(f"💾 Screenshot size: {result['screenshot_size_kb']} KB")
            
            # Check if file actually exists
            if os.path.exists(result['file_path']):
                file_size = os.path.getsize(result['file_path'])
                print(f"✅ File exists on disk: {file_size} bytes")
            else:
                print("❌ File not found on disk")
                
        else:
            print("❌ Screenshot capture: FAILED")
            print(f"🚫 Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_basic_website():
    """Test with a simple website first to verify setup"""
    
    print("\n🧪 Testing Basic Website Screenshot")
    print("=" * 60)
    
    test_url = "https://example.com"
    
    print(f"📍 Testing URL: {test_url}")
    print("⏳ Capturing screenshot...")
    
    try:
        result = await screenshot_service.test_screenshot_capture(test_url)
        
        print("\n📊 Basic Test Results:")
        print("-" * 40)
        
        if result["status"] == "success":
            print("✅ Basic screenshot: SUCCESS")
            print(f"📁 File: {result['file_path']}")
            print(f"📄 Title: {result['page_title']}")
        else:
            print("❌ Basic screenshot: FAILED")
            print(f"🚫 Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Basic test failed: {str(e)}")

async def main():
    """Run all tests"""
    print("🚀 Starting Screenshot Service Tests")
    print("=" * 60)
    
    # Test 1: Basic website
    await test_basic_website()
    
    # Test 2: Google Business Profile
    await test_google_business_screenshot()
    
    print("\n🏁 Tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())