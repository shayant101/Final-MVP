#!/usr/bin/env python3
"""
Debug the specific Google Profile URL to understand the HTML structure
"""
import asyncio
import sys
import os
import httpx
from bs4 import BeautifulSoup
import re

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def debug_url_content():
    """Debug the HTML content of the specific URL"""
    
    test_url = "https://maps.app.goo.gl/nRnCfUfAWF5v2AnC9"
    
    print(f"🔍 Debugging URL: {test_url}")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            headers=headers,
            follow_redirects=True
        ) as client:
            
            print("📡 Making request...")
            response = await client.get(test_url)
            final_url = str(response.url)
            
            print(f"✅ Response Status: {response.status_code}")
            print(f"🔗 Original URL: {test_url}")
            print(f"📍 Final URL: {final_url}")
            print(f"📄 Content Length: {len(response.text)} characters")
            print()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print("🔍 BUSINESS NAME EXTRACTION")
            print("-" * 40)
            
            # Try different methods to extract business name
            print("Method 1 - Title tag:")
            if soup.title:
                print(f"   Title: {soup.title.string}")
            else:
                print("   No title tag found")
            
            print("\nMethod 2 - H1, H2, H3 tags:")
            headings = soup.find_all(['h1', 'h2', 'h3'])[:5]  # First 5 headings
            for i, heading in enumerate(headings):
                text = heading.get_text().strip()[:100]  # First 100 chars
                print(f"   H{heading.name[1]}: {text}")
            
            print("\nMethod 3 - Meta tags:")
            meta_title = soup.find('meta', {'property': 'og:title'})
            if meta_title:
                print(f"   og:title: {meta_title.get('content', '')}")
            else:
                print("   No og:title found")
            
            print("\n🔍 RATING EXTRACTION")
            print("-" * 40)
            
            # Look for rating patterns in the HTML
            html_text = response.text
            
            # Common rating patterns
            rating_patterns = [
                r'(\d+\.?\d*)\s*★',
                r'★\s*(\d+\.?\d*)',
                r'"rating["\s]*:\s*(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*stars?',
                r'(\d+\.?\d*)\s*out of 5',
                r'rating["\s:]+(\d+\.?\d*)',
            ]
            
            print("Rating patterns found:")
            for pattern in rating_patterns:
                matches = re.findall(pattern, html_text, re.IGNORECASE)
                if matches:
                    print(f"   Pattern '{pattern}': {matches[:3]}")  # First 3 matches
            
            print("\n🔍 REVIEW COUNT EXTRACTION")
            print("-" * 40)
            
            # Look for review count patterns
            review_patterns = [
                r'(\d+\.?\d*[kK]?)\s*reviews?',
                r'(\d+\.?\d*[kK]?)\s*Google reviews?',
                r'"reviewCount["\s]*:\s*(\d+)',
                r'Based on (\d+\.?\d*[kK]?) reviews?',
                r'(\d+\.?\d*[kK]?)\s*customer reviews?',
                r'(\d+\.?\d*[kK]?)\s*ratings?',
                r'\((\d+\.?\d*[kK]?)\)',  # Numbers in parentheses
                r'(\d+,\d+)\s*reviews?',  # Comma-separated numbers like 1,900
                r'(\d+\.\d+[kK])\s*reviews?',  # Numbers like 1.9k
            ]
            
            print("Review count patterns found:")
            for pattern in review_patterns:
                matches = re.findall(pattern, html_text, re.IGNORECASE)
                if matches:
                    print(f"   Pattern '{pattern}': {matches[:5]}")  # First 5 matches
            
            print("\n🔍 CATEGORY EXTRACTION")
            print("-" * 40)
            
            # Look for category patterns
            category_patterns = [
                r'"category["\s]*:\s*"([^"]+)"',
                r'@type["\s]*:\s*"([^"]+)"',
                r'business.*type["\s]*:\s*"([^"]+)"',
            ]
            
            print("Category patterns found:")
            for pattern in category_patterns:
                matches = re.findall(pattern, html_text, re.IGNORECASE)
                if matches:
                    print(f"   Pattern '{pattern}': {matches[:3]}")
            
            # Look for common restaurant keywords
            restaurant_keywords = [
                'restaurant', 'cafe', 'coffee shop', 'bar', 'bistro', 'diner',
                'pizzeria', 'bakery', 'fast food', 'food truck', 'catering',
            ]
            
            found_keywords = []
            html_lower = html_text.lower()
            for keyword in restaurant_keywords:
                if keyword in html_lower:
                    found_keywords.append(keyword)
            
            print(f"Restaurant keywords found: {found_keywords[:5]}")
            
            print("\n🔍 JSON-LD STRUCTURED DATA")
            print("-" * 40)
            
            scripts = soup.find_all('script', type='application/ld+json')
            print(f"Found {len(scripts)} JSON-LD scripts:")
            
            for i, script in enumerate(scripts[:3]):  # First 3 scripts
                try:
                    import json
                    data = json.loads(script.string)
                    print(f"   Script {i+1}: {type(data)} with keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    if isinstance(data, dict):
                        # Look for business-related data
                        if 'name' in data:
                            print(f"      name: {data['name']}")
                        if 'aggregateRating' in data:
                            rating_data = data['aggregateRating']
                            print(f"      rating: {rating_data}")
                        if '@type' in data:
                            print(f"      @type: {data['@type']}")
                except Exception as e:
                    print(f"   Script {i+1}: Error parsing JSON - {str(e)[:50]}")
            
            print(f"\n📄 Raw HTML Preview (first 1000 characters):")
            print("-" * 40)
            print(response.text[:1000])
            print("...")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    await debug_url_content()

if __name__ == "__main__":
    asyncio.run(main())