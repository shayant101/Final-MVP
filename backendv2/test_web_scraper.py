#!/usr/bin/env python3.9
"""
Test script for web scraper service
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.web_scraper_service import web_scraper_service

async def test_website_scraping():
    """Test basic website scraping"""
    print("🔍 Testing website scraping...")
    
    try:
        result = await web_scraper_service.scrape_website_data("https://example.com")
        print(f"✅ Website scraping result: {result['success']}")
        if result['success']:
            print(f"   - Title: {result['data'].get('title', 'N/A')}")
            print(f"   - SSL: {result['data'].get('has_ssl', False)}")
            print(f"   - Mobile friendly: {result['data'].get('mobile_friendly', False)}")
        else:
            print(f"   - Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Website scraping failed: {str(e)}")

async def test_google_scraping():
    """Test Google Business Profile scraping"""
    print("\n🔍 Testing Google Business Profile scraping...")
    
    try:
        result = await web_scraper_service.scrape_google_business_profile("https://maps.google.com/maps?cid=12345")
        print(f"✅ Google scraping result: {result['success']}")
        if result['success']:
            print(f"   - Name: {result['data'].get('name', 'N/A')}")
            print(f"   - Rating: {result['data'].get('rating', 0)}")
            print(f"   - Reviews: {result['data'].get('review_count', 0)}")
        else:
            print(f"   - Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Google scraping failed: {str(e)}")

async def main():
    """Run all tests"""
    print("🚀 Starting web scraper tests...\n")
    
    await test_website_scraping()
    await test_google_scraping()
    
    print("\n✅ Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())