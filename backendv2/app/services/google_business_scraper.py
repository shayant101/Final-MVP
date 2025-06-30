"""
Google Business Profile Scraper
Focused scraper for extracting specific data points from Google Business Profiles
"""
import asyncio
import logging
import re
from typing import Dict, Any, Optional, List
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class GoogleBusinessScraper:
    def __init__(self):
        self.timeout = 10.0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def scrape_basic_info(self, google_business_url: str) -> Dict[str, Any]:
        """
        Scrape basic information from Google Business Profile:
        - Business Name
        - Reviews & Ratings
        - Categories/Business Type
        """
        result = {
            "success": False,
            "business_name": None,
            "rating": None,
            "review_count": None,
            "categories": [],
            "error": None,
            "scraped_data": {}
        }
        
        if not google_business_url:
            result["error"] = "No Google Business URL provided"
            return result
        
        try:
            logger.info(f"🔍 Attempting to scrape Google Business Profile: {google_business_url}")
            
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers,
                follow_redirects=True
            ) as client:
                
                # First, resolve any redirects (g.co URLs redirect to full Google Maps URLs)
                response = await client.get(google_business_url)
                final_url = str(response.url)
                
                logger.info(f"📍 Resolved URL: {final_url}")
                
                # Get the page content
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract business name
                business_name = self._extract_business_name(soup, html_content)
                if business_name:
                    result["business_name"] = business_name
                    logger.info(f"✅ Found business name: {business_name}")
                
                # Extract rating and review count
                rating_info = self._extract_rating_info(soup, html_content)
                if rating_info:
                    result["rating"] = rating_info.get("rating")
                    result["review_count"] = rating_info.get("review_count")
                    logger.info(f"✅ Found rating: {rating_info.get('rating')} ({rating_info.get('review_count')} reviews)")
                
                # Extract categories
                categories = self._extract_categories(soup, html_content)
                if categories:
                    result["categories"] = categories
                    logger.info(f"✅ Found categories: {categories}")
                
                # Mark as successful if we got at least one piece of data
                if business_name or rating_info or categories:
                    result["success"] = True
                    result["scraped_data"] = {
                        "final_url": final_url,
                        "page_title": soup.title.string if soup.title else None,
                        "extraction_method": "html_parsing"
                    }
                else:
                    result["error"] = "Could not extract any business information from the page"
                    logger.warning(f"⚠️ No data extracted from {final_url}")
                
        except asyncio.TimeoutError:
            result["error"] = "Request timed out"
            logger.error(f"⏰ Timeout scraping {google_business_url}")
        except Exception as e:
            result["error"] = f"Scraping failed: {str(e)}"
            logger.error(f"❌ Error scraping {google_business_url}: {str(e)}")
        
        return result
    
    def _extract_business_name(self, soup: BeautifulSoup, html_content: str) -> Optional[str]:
        """Extract business name from various possible locations"""
        try:
            # Method 1: Look for business name in Google search results
            # Check for knowledge panel business name
            knowledge_panel_selectors = [
                'h2[data-attrid="title"]',
                'h1[data-attrid="title"]',
                '[data-attrid="title"] h2',
                '[data-attrid="title"] h1'
            ]
            
            for selector in knowledge_panel_selectors:
                elements = soup.select(selector)
                for element in elements:
                    name = element.get_text().strip()
                    if name and len(name) > 2 and not name.lower().startswith('google'):
                        return name
            
            # Method 2: Look for h1/h2/h3 tags with business name
            heading_tags = soup.find_all(['h1', 'h2', 'h3'])
            for heading in heading_tags:
                text = heading.get_text().strip()
                if text and len(text) > 2 and len(text) < 100:
                    # Skip common Google page elements and JavaScript code
                    skip_patterns = ['google', 'search', 'maps', 'images', 'videos', 'function', 'var ', '(', ')', '{', '}', '=', ';']
                    if not any(skip in text.lower() for skip in skip_patterns):
                        return text
            
            # Method 3: Look in page title for business name
            if soup.title:
                title = soup.title.string
                if title:
                    # Handle different title formats
                    if ' - Google Search' in title:
                        name = title.replace(' - Google Search', '').strip()
                        if len(name) > 2:
                            return name
                    elif ' - Google Maps' in title:
                        name = title.replace(' - Google Maps', '').strip()
                        if len(name) > 2:
                            return name
            
            # Method 4: Look for data attributes or JSON-LD
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'name' in data:
                        return data['name']
                except:
                    continue
            
            # Method 5: Extract from URL query parameter (most reliable for Google search results)
            # The resolved URL contains q=Bee+%26+Tea which is the business name
            final_url = str(soup.find('link', rel='canonical')['href']) if soup.find('link', rel='canonical') else html_content
            
            # Look for q= parameter in URL or HTML
            url_patterns = [
                r'q=([^&]+)',  # Query parameter often contains business name
                r'"q":"([^"]+)"',
                r'&q=([^&]+)'
            ]
            
            for pattern in url_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    # URL decode if needed
                    try:
                        import urllib.parse
                        name = urllib.parse.unquote_plus(name)
                        # Clean up the name
                        name = name.replace('+', ' ').replace('%26', '&')
                    except:
                        pass
                    
                    if len(name) > 2 and not name.lower().startswith('google'):
                        return name
            
            # Method 6: Other regex patterns
            name_patterns = [
                r'"name":"([^"]+)"',
                r'data-value="([^"]+)"[^>]*aria-label="[^"]*name[^"]*"'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    if len(name) > 2 and not name.lower().startswith('google'):
                        return name
            
        except Exception as e:
            logger.error(f"Error extracting business name: {str(e)}")
        
        return None
    
    def _extract_rating_info(self, soup: BeautifulSoup, html_content: str) -> Optional[Dict[str, Any]]:
        """Extract rating and review count"""
        try:
            rating_info = {}
            
            # Method 1: Look for rating in Google search results knowledge panel
            # Common selectors for ratings in Google search results
            rating_selectors = [
                '[data-attrid="kc:/business/consumer_rating:rating"] span',
                '[data-attrid="kc:/business/consumer_rating:num_ratings"] span',
                '.review-rating span',
                '.rating span'
            ]
            
            for selector in rating_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # Look for rating pattern like "4.5" or "4.5 stars"
                    rating_match = re.search(r'(\d+\.?\d*)', text)
                    if rating_match:
                        try:
                            rating = float(rating_match.group(1))
                            if 0 <= rating <= 5:
                                rating_info["rating"] = rating
                                break
                        except:
                            continue
            
            # Method 2: Look for rating patterns in HTML content
            rating_patterns = [
                r'"rating":(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*stars?',
                r'rating["\s:]+(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*out of 5',
                r'(\d+\.?\d*)\s*★',  # Star symbol
                r'★\s*(\d+\.?\d*)'
            ]
            
            for pattern in rating_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    try:
                        rating = float(match.group(1))
                        if 0 <= rating <= 5:
                            rating_info["rating"] = rating
                            break
                    except:
                        continue
            
            # Method 3: Look for review count patterns
            review_patterns = [
                r'"reviewCount":(\d+)',
                r'(\d+)\s*reviews?',
                r'(\d+)\s*Google reviews?',
                r'Based on (\d+) reviews?',
                r'(\d+)\s*customer reviews?',
                r'(\d+)\s*ratings?',
                r'\((\d+)\)',  # Numbers in parentheses often indicate review count
            ]
            
            for pattern in review_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    try:
                        review_count = int(match)
                        # Reasonable review count range
                        if 1 <= review_count <= 100000:
                            rating_info["review_count"] = review_count
                            break
                    except:
                        continue
                if "review_count" in rating_info:
                    break
            
            # Method 4: Look in structured data
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if 'aggregateRating' in data:
                            agg_rating = data['aggregateRating']
                            if 'ratingValue' in agg_rating:
                                rating_info["rating"] = float(agg_rating['ratingValue'])
                            if 'reviewCount' in agg_rating:
                                rating_info["review_count"] = int(agg_rating['reviewCount'])
                except:
                    continue
            
            return rating_info if rating_info else None
            
        except Exception as e:
            logger.error(f"Error extracting rating info: {str(e)}")
            return None
    
    def _extract_categories(self, soup: BeautifulSoup, html_content: str) -> List[str]:
        """Extract business categories/types"""
        try:
            categories = []
            
            # Method 1: Look for category information in JSON-LD
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if '@type' in data:
                            categories.append(data['@type'])
                        if 'category' in data:
                            if isinstance(data['category'], list):
                                categories.extend(data['category'])
                            else:
                                categories.append(data['category'])
                except:
                    continue
            
            # Method 2: Look for category patterns in HTML
            category_patterns = [
                r'"category":"([^"]+)"',
                r'category["\s:]+([^",\n]+)',
                r'business type["\s:]+([^",\n]+)'
            ]
            
            for pattern in category_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    category = match.strip()
                    if len(category) > 2 and category not in categories:
                        categories.append(category)
            
            # Method 3: Common restaurant/business type keywords
            restaurant_keywords = [
                'restaurant', 'cafe', 'coffee shop', 'bar', 'bistro', 'diner',
                'pizzeria', 'bakery', 'fast food', 'food truck', 'catering',
                'italian restaurant', 'chinese restaurant', 'mexican restaurant',
                'american restaurant', 'asian restaurant', 'seafood restaurant'
            ]
            
            html_lower = html_content.lower()
            for keyword in restaurant_keywords:
                if keyword in html_lower and keyword not in [c.lower() for c in categories]:
                    categories.append(keyword.title())
            
            # Clean and deduplicate categories
            cleaned_categories = []
            for cat in categories:
                if isinstance(cat, str) and len(cat.strip()) > 2:
                    cleaned_cat = cat.strip().title()
                    if cleaned_cat not in cleaned_categories:
                        cleaned_categories.append(cleaned_cat)
            
            return cleaned_categories[:5]  # Limit to top 5 categories
            
        except Exception as e:
            logger.error(f"Error extracting categories: {str(e)}")
            return []

# Create service instance
google_business_scraper = GoogleBusinessScraper()