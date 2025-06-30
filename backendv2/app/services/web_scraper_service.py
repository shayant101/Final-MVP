"""
Web Scraper Service
Handles real web scraping for Google Business Profile and website analysis
"""
import asyncio
import logging
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
import httpx

# Try to import selenium with graceful fallback
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not available - will use requests-only scraping")

logger = logging.getLogger(__name__)

class WebScraperService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.timeout = 5  # Reduced timeout
        self.max_retries = 2  # Reduced retries
        
    async def scrape_google_business_profile(self, google_url: str) -> Dict[str, Any]:
        """
        Scrape Google Business Profile data from Google Maps URL
        """
        try:
            logger.info(f"Scraping Google Business Profile: {google_url}")
            
            # Validate Google URL
            if not self._is_valid_google_url(google_url):
                return self._get_fallback_google_data("Invalid Google Business Profile URL")
            
            # Try selenium first if available, then fallback to requests
            if SELENIUM_AVAILABLE:
                try:
                    driver = self._setup_selenium_driver()
                    driver.get(google_url)
                    
                    # Wait for page to load with shorter timeout
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Extract business data
                    business_data = await self._extract_google_business_data(driver)
                    driver.quit()
                    
                    return {
                        "success": True,
                        "data": business_data,
                        "scraped_at": time.time(),
                        "source_url": google_url
                    }
                    
                except Exception as e:
                    logger.error(f"Selenium scraping failed: {str(e)}")
                    if 'driver' in locals():
                        driver.quit()
                    # Fall through to requests-based scraping
            
            # Fallback to requests-based scraping
            return await self._scrape_google_with_requests(google_url)
                    
        except Exception as e:
            logger.error(f"Google Business Profile scraping failed: {str(e)}")
            return self._get_fallback_google_data(str(e))
    
    async def scrape_website_data(self, website_url: str) -> Dict[str, Any]:
        """
        Scrape website for SEO and performance analysis
        """
        try:
            logger.info(f"Scraping website: {website_url}")
            
            # Validate URL
            if not self._is_valid_url(website_url):
                return self._get_fallback_website_data("Invalid website URL")
            
            # Perform HTTP request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(website_url, follow_redirects=True)
                
                if response.status_code != 200:
                    return self._get_fallback_website_data(f"HTTP {response.status_code}")
                
                # Parse HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract website data
                website_data = await self._extract_website_data(soup, website_url, response)
                
                return {
                    "success": True,
                    "data": website_data,
                    "scraped_at": time.time(),
                    "source_url": website_url
                }
                
        except Exception as e:
            logger.error(f"Website scraping failed: {str(e)}")
            return self._get_fallback_website_data(str(e))
    
    async def find_social_media_links(self, website_url: str) -> Dict[str, Any]:
        """
        Find social media links from website
        """
        try:
            logger.info(f"Finding social media links for: {website_url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(website_url, follow_redirects=True)
                
                if response.status_code != 200:
                    return {"success": False, "social_links": {}}
                
                soup = BeautifulSoup(response.content, 'html.parser')
                social_links = self._extract_social_media_links(soup)
                
                return {
                    "success": True,
                    "social_links": social_links,
                    "found_count": len(social_links)
                }
                
        except Exception as e:
            logger.error(f"Social media link extraction failed: {str(e)}")
            return {"success": False, "social_links": {}, "error": str(e)}
    
    async def analyze_website_performance(self, website_url: str) -> Dict[str, Any]:
        """
        Analyze website performance metrics
        """
        try:
            logger.info(f"Analyzing website performance: {website_url}")
            
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(website_url, follow_redirects=True)
                
                load_time = time.time() - start_time
                
                # Analyze response
                performance_data = {
                    "load_time_seconds": round(load_time, 2),
                    "status_code": response.status_code,
                    "content_size_kb": round(len(response.content) / 1024, 2),
                    "has_ssl": website_url.startswith('https://'),
                    "response_headers": dict(response.headers),
                    "redirects": len(response.history)
                }
                
                # Parse content for additional metrics
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    performance_data.update(self._analyze_page_structure(soup))
                
                return {
                    "success": True,
                    "performance": performance_data,
                    "recommendations": self._generate_performance_recommendations(performance_data)
                }
                
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "performance": self._get_fallback_performance_data()
            }
    
    def _setup_selenium_driver(self):
        """Setup Chrome driver with appropriate options"""
        if not SELENIUM_AVAILABLE:
            raise Exception("Selenium not available")
            
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        return webdriver.Chrome(options=chrome_options)
    
    async def _extract_google_business_data(self, driver) -> Dict[str, Any]:
        """Extract data from Google Business Profile page"""
        try:
            business_data = {
                "name": "",
                "rating": 0.0,
                "review_count": 0,
                "address": "",
                "phone": "",
                "website": "",
                "hours": {},
                "photos_count": 0,
                "categories": [],
                "verified": False,
                "claimed": False
            }
            
            # Extract business name
            try:
                name_element = driver.find_element(By.CSS_SELECTOR, "h1[data-attrid='title']")
                business_data["name"] = name_element.text.strip()
            except:
                try:
                    name_element = driver.find_element(By.CSS_SELECTOR, "h1")
                    business_data["name"] = name_element.text.strip()
                except:
                    pass
            
            # Extract rating and reviews
            try:
                rating_element = driver.find_element(By.CSS_SELECTOR, "[data-value='Reviews'] span")
                rating_text = rating_element.text
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    business_data["rating"] = float(rating_match.group(1))
                
                review_match = re.search(r'\((\d+(?:,\d+)*)\)', rating_text)
                if review_match:
                    business_data["review_count"] = int(review_match.group(1).replace(',', ''))
            except:
                pass
            
            # Extract address
            try:
                address_element = driver.find_element(By.CSS_SELECTOR, "[data-item-id='address']")
                business_data["address"] = address_element.text.strip()
            except:
                pass
            
            # Extract phone
            try:
                phone_element = driver.find_element(By.CSS_SELECTOR, "[data-item-id='phone']")
                business_data["phone"] = phone_element.text.strip()
            except:
                pass
            
            # Extract website
            try:
                website_element = driver.find_element(By.CSS_SELECTOR, "[data-item-id='authority']")
                business_data["website"] = website_element.get_attribute('href')
            except:
                pass
            
            # Check if verified/claimed
            try:
                verified_element = driver.find_element(By.CSS_SELECTOR, "[aria-label*='Verified']")
                business_data["verified"] = True
            except:
                pass
            
            # Count photos
            try:
                photos_elements = driver.find_elements(By.CSS_SELECTOR, "[data-photo-index]")
                business_data["photos_count"] = len(photos_elements)
            except:
                pass
            
            return business_data
            
        except Exception as e:
            logger.error(f"Google data extraction failed: {str(e)}")
            return self._get_fallback_google_data(str(e))["data"]
    
    async def _scrape_google_with_requests(self, google_url: str) -> Dict[str, Any]:
        """Fallback scraping with requests"""
        try:
            response = self.session.get(google_url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Basic extraction from HTML
            business_data = {
                "name": "Business Name Not Found",
                "rating": 0.0,
                "review_count": 0,
                "address": "",
                "phone": "",
                "website": "",
                "hours": {},
                "photos_count": 0,
                "categories": [],
                "verified": False,
                "claimed": False,
                "extraction_method": "requests_fallback"
            }
            
            # Try to extract basic info from meta tags
            title_tag = soup.find('title')
            if title_tag:
                business_data["name"] = title_tag.text.split(' - ')[0]
            
            return {
                "success": True,
                "data": business_data,
                "scraped_at": time.time(),
                "source_url": google_url,
                "note": "Limited data - dynamic content requires JavaScript"
            }
            
        except Exception as e:
            logger.error(f"Requests fallback failed: {str(e)}")
            return self._get_fallback_google_data(str(e))
    
    async def _extract_website_data(self, soup: BeautifulSoup, url: str, response) -> Dict[str, Any]:
        """Extract comprehensive website data"""
        website_data = {
            "title": "",
            "description": "",
            "keywords": [],
            "has_menu": False,
            "has_contact": False,
            "has_hours": False,
            "has_online_ordering": False,
            "mobile_friendly": False,
            "has_ssl": url.startswith('https://'),
            "page_count": 1,
            "images_count": 0,
            "internal_links": 0,
            "external_links": 0,
            "social_links": {},
            "seo_score": 0,
            "content_quality": "unknown"
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            website_data["title"] = title_tag.text.strip()
        
        # Extract meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            website_data["description"] = desc_tag.get('content', '')
        
        # Extract keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            website_data["keywords"] = [k.strip() for k in keywords_tag.get('content', '').split(',')]
        
        # Check for restaurant-specific content
        text_content = soup.get_text().lower()
        website_data["has_menu"] = any(word in text_content for word in ['menu', 'food', 'dishes', 'cuisine'])
        website_data["has_contact"] = any(word in text_content for word in ['contact', 'phone', 'address', 'location'])
        website_data["has_hours"] = any(word in text_content for word in ['hours', 'open', 'closed', 'monday', 'tuesday'])
        website_data["has_online_ordering"] = any(word in text_content for word in ['order online', 'delivery', 'takeout', 'grubhub', 'doordash'])
        
        # Check mobile friendliness
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        website_data["mobile_friendly"] = viewport_tag is not None
        
        # Count elements
        website_data["images_count"] = len(soup.find_all('img'))
        
        # Count links
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href']
            if href.startswith('http') and urlparse(href).netloc != urlparse(url).netloc:
                website_data["external_links"] += 1
            else:
                website_data["internal_links"] += 1
        
        # Extract social media links
        website_data["social_links"] = self._extract_social_media_links(soup)
        
        # Calculate basic SEO score
        website_data["seo_score"] = self._calculate_seo_score(website_data, soup)
        
        return website_data
    
    def _extract_social_media_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links from page"""
        social_links = {}
        social_patterns = {
            'facebook': r'facebook\.com/[^/\s]+',
            'instagram': r'instagram\.com/[^/\s]+',
            'twitter': r'twitter\.com/[^/\s]+',
            'linkedin': r'linkedin\.com/[^/\s]+',
            'youtube': r'youtube\.com/[^/\s]+',
            'tiktok': r'tiktok\.com/[^/\s]+',
            'yelp': r'yelp\.com/[^/\s]+'
        }
        
        # Find all links
        links = soup.find_all('a', href=True)
        page_text = soup.get_text()
        
        for platform, pattern in social_patterns.items():
            # Check in links
            for link in links:
                href = link.get('href', '')
                if platform in href.lower():
                    social_links[platform] = href
                    break
            
            # Check in text content
            if platform not in social_links:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    social_links[platform] = f"https://{match.group()}"
        
        return social_links
    
    def _analyze_page_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze page structure for performance insights"""
        return {
            "h1_count": len(soup.find_all('h1')),
            "h2_count": len(soup.find_all('h2')),
            "h3_count": len(soup.find_all('h3')),
            "script_count": len(soup.find_all('script')),
            "css_count": len(soup.find_all('link', rel='stylesheet')),
            "form_count": len(soup.find_all('form')),
            "table_count": len(soup.find_all('table')),
            "has_structured_data": bool(soup.find('script', type='application/ld+json'))
        }
    
    def _calculate_seo_score(self, website_data: Dict, soup: BeautifulSoup) -> int:
        """Calculate basic SEO score"""
        score = 0
        
        # Title (20 points)
        if website_data["title"]:
            score += 20
            if 30 <= len(website_data["title"]) <= 60:
                score += 10
        
        # Description (20 points)
        if website_data["description"]:
            score += 20
            if 120 <= len(website_data["description"]) <= 160:
                score += 10
        
        # SSL (10 points)
        if website_data["has_ssl"]:
            score += 10
        
        # Mobile friendly (10 points)
        if website_data["mobile_friendly"]:
            score += 10
        
        # Content structure (20 points)
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 1:
            score += 10
        if soup.find_all('h2'):
            score += 10
        
        # Images with alt text (10 points)
        images = soup.find_all('img')
        if images:
            images_with_alt = [img for img in images if img.get('alt')]
            if len(images_with_alt) / len(images) > 0.8:
                score += 10
        
        return min(score, 100)
    
    def _generate_performance_recommendations(self, performance_data: Dict) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if performance_data["load_time_seconds"] > 3:
            recommendations.append("Optimize page load time - currently over 3 seconds")
        
        if not performance_data["has_ssl"]:
            recommendations.append("Enable SSL certificate for security and SEO")
        
        if performance_data["content_size_kb"] > 1000:
            recommendations.append("Optimize images and content size")
        
        if performance_data["redirects"] > 2:
            recommendations.append("Minimize redirect chains")
        
        return recommendations
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _is_valid_google_url(self, url: str) -> bool:
        """Validate Google Business Profile URL"""
        google_patterns = [
            'maps.google.com',
            'google.com/maps',
            'goo.gl/maps',
            'business.google.com'
        ]
        return any(pattern in url.lower() for pattern in google_patterns)
    
    def _get_fallback_google_data(self, error_msg: str = "") -> Dict[str, Any]:
        """Return fallback Google Business data"""
        return {
            "success": False,
            "data": {
                "name": "Unable to extract",
                "rating": 0.0,
                "review_count": 0,
                "address": "",
                "phone": "",
                "website": "",
                "hours": {},
                "photos_count": 0,
                "categories": [],
                "verified": False,
                "claimed": False,
                "error": error_msg
            },
            "scraped_at": time.time(),
            "note": "Scraping failed - using fallback data"
        }
    
    def _get_fallback_website_data(self, error_msg: str = "") -> Dict[str, Any]:
        """Return fallback website data"""
        return {
            "success": False,
            "data": {
                "title": "Unable to extract",
                "description": "",
                "keywords": [],
                "has_menu": False,
                "has_contact": False,
                "has_hours": False,
                "has_online_ordering": False,
                "mobile_friendly": False,
                "has_ssl": False,
                "page_count": 0,
                "images_count": 0,
                "internal_links": 0,
                "external_links": 0,
                "social_links": {},
                "seo_score": 0,
                "content_quality": "unknown",
                "error": error_msg
            },
            "scraped_at": time.time(),
            "note": "Scraping failed - using fallback data"
        }
    
    def _get_fallback_performance_data(self) -> Dict[str, Any]:
        """Return fallback performance data"""
        return {
            "load_time_seconds": 0,
            "status_code": 0,
            "content_size_kb": 0,
            "has_ssl": False,
            "response_headers": {},
            "redirects": 0,
            "error": "Performance analysis failed"
        }

# Create service instance
web_scraper_service = WebScraperService()