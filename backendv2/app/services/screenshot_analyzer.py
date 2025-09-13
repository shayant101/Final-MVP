"""
Screenshot-based Business Profile Analyzer
Uses Playwright to capture screenshots and OpenAI Vision to extract business information
"""
import asyncio
import logging
import base64
import re
from typing import Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class ScreenshotAnalyzer:
    """
    Captures screenshots of Google Business Profiles and analyzes them using Vision AI
    """
    
    def __init__(self):
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
    
    async def analyze_google_profile_screenshot(self, url: str, business_name: str = "") -> Dict[str, Any]:
        """
        Main method to analyze a Google Business Profile via screenshot
        
        Args:
            url: Google Business Profile URL
            business_name: Expected business name for verification
            
        Returns:
            Dictionary with extracted business information
        """
        try:
            logger.info(f"📸 Starting screenshot analysis for: {url}")
            
            # Step 1: Capture screenshot
            screenshot_path = await self._capture_screenshot(url)
            if not screenshot_path:
                return self._generate_error_result("Failed to capture screenshot")
            
            # Step 2: Analyze screenshot with Vision AI
            extracted_data = await self._analyze_screenshot_with_vision(screenshot_path, business_name)
            
            # Step 3: Parse and structure the data
            structured_data = await self._structure_extracted_data(extracted_data, business_name)
            
            logger.info(f"✅ Screenshot analysis completed successfully")
            return structured_data
            
        except Exception as e:
            logger.error(f"❌ Screenshot analysis failed: {str(e)}")
            return self._generate_error_result(str(e))
    
    async def _capture_screenshot(self, url: str) -> Optional[str]:
        """Capture screenshot using Playwright"""
        try:
            from playwright.async_api import async_playwright
            
            logger.info(f"🌐 Capturing screenshot of: {url}")
            
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security'
                    ]
                )
                
                # Create context with realistic user agent
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = await context.new_page()
                
                # Navigate to URL with timeout
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load
                await asyncio.sleep(3)
                
                # Take screenshot
                screenshot_filename = f"profile_{hash(url) % 10000}.png"
                screenshot_path = self.screenshots_dir / screenshot_filename
                
                await page.screenshot(
                    path=str(screenshot_path),
                    full_page=True,
                    quality=90
                )
                
                await browser.close()
                
                logger.info(f"📸 Screenshot saved: {screenshot_path}")
                return str(screenshot_path)
                
        except ImportError:
            logger.error("❌ Playwright not installed. Run: pip install playwright && playwright install chromium")
            return None
        except Exception as e:
            logger.error(f"❌ Screenshot capture failed: {str(e)}")
            return None
    
    async def _analyze_screenshot_with_vision(self, screenshot_path: str, business_name: str) -> Dict[str, Any]:
        """Analyze screenshot using OpenAI Vision API"""
        try:
            from openai import AsyncOpenAI
            import os
            
            # Initialize OpenAI client
            client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Read and encode screenshot
            with open(screenshot_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            logger.info(f"🤖 Analyzing screenshot with OpenAI Vision...")
            
            # Create vision prompt
            vision_prompt = f"""
            Analyze this Google Business Profile screenshot and extract ALL visible business information.
            Expected business name: "{business_name}" (if provided)
            
            Please extract and return a JSON object with the following information:
            
            {{
                "business_name": "exact business name as shown",
                "rating": "star rating (e.g., 4.2)",
                "review_count": "number of reviews (e.g., 1947 or 1.9k)",
                "categories": ["business category 1", "business category 2"],
                "address": "full address if visible",
                "phone": "phone number if visible",
                "website": "website URL if visible",
                "hours": "business hours if visible",
                "price_range": "price range (e.g., $$) if visible",
                "popular_times": "any popular times info if visible",
                "amenities": ["amenity 1", "amenity 2"],
                "photos_count": "number of photos if visible",
                "description": "business description if visible",
                "verified": "whether business appears verified",
                "claimed": "whether business appears claimed",
                "additional_info": "any other relevant business information visible"
            }}
            
            IMPORTANT:
            1. Extract EXACT text as it appears on screen
            2. For review count, preserve original format (1.9k, 1,947, etc.)
            3. Include ALL visible categories/types
            4. If information is not visible, use null
            5. Be precise with numbers and ratings
            6. Include any special badges, verification marks, or status indicators
            
            Return only the JSON object, no additional text.
            """
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": vision_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Extract JSON from response
            vision_response = response.choices[0].message.content
            logger.info(f"🤖 Vision analysis completed")
            
            # Parse JSON response
            try:
                extracted_data = json.loads(vision_response)
                return extracted_data
            except json.JSONDecodeError:
                # Try to extract JSON from response if it's wrapped in text
                json_match = re.search(r'\{.*\}', vision_response, re.DOTALL)
                if json_match:
                    extracted_data = json.loads(json_match.group())
                    return extracted_data
                else:
                    logger.error(f"Failed to parse JSON from vision response: {vision_response}")
                    return {"error": "Failed to parse vision response"}
                    
        except Exception as e:
            logger.error(f"❌ Vision analysis failed: {str(e)}")
            return {"error": str(e)}
    
    async def _structure_extracted_data(self, extracted_data: Dict[str, Any], expected_name: str) -> Dict[str, Any]:
        """Structure the extracted data into our standard format"""
        try:
            if "error" in extracted_data:
                return self._generate_error_result(extracted_data["error"])
            
            # Parse review count to handle various formats
            review_count = self._parse_review_count(extracted_data.get("review_count"))
            
            # Parse rating
            rating = self._parse_rating(extracted_data.get("rating"))
            
            structured = {
                "success": True,
                "business_name": extracted_data.get("business_name"),
                "rating": rating,
                "review_count": review_count,
                "categories": extracted_data.get("categories", []),
                "address": extracted_data.get("address"),
                "phone": extracted_data.get("phone"),
                "website": extracted_data.get("website"),
                "hours": extracted_data.get("hours"),
                "price_range": extracted_data.get("price_range"),
                "amenities": extracted_data.get("amenities", []),
                "photos_count": extracted_data.get("photos_count"),
                "description": extracted_data.get("description"),
                "verified": extracted_data.get("verified"),
                "claimed": extracted_data.get("claimed"),
                "additional_info": extracted_data.get("additional_info"),
                "extraction_method": "screenshot_vision_analysis",
                "raw_extracted_data": extracted_data
            }
            
            return structured
            
        except Exception as e:
            logger.error(f"❌ Data structuring failed: {str(e)}")
            return self._generate_error_result(str(e))
    
    def _parse_review_count(self, review_count_str: Any) -> Optional[int]:
        """Parse review count from various formats"""
        if not review_count_str:
            return None
            
        try:
            count_str = str(review_count_str).lower().replace(',', '').replace(' ', '')
            
            if 'k' in count_str:
                # Handle 1.9k format
                number = float(count_str.replace('k', ''))
                return int(number * 1000)
            elif 'm' in count_str:
                # Handle 1.2m format
                number = float(count_str.replace('m', ''))
                return int(number * 1000000)
            else:
                # Handle regular numbers
                # Extract just the numeric part
                numeric = re.search(r'(\d+)', count_str)
                if numeric:
                    return int(numeric.group(1))
                    
        except:
            pass
            
        return None
    
    def _parse_rating(self, rating_str: Any) -> Optional[float]:
        """Parse rating from string"""
        if not rating_str:
            return None
            
        try:
            # Extract numeric rating
            rating_match = re.search(r'(\d+\.?\d*)', str(rating_str))
            if rating_match:
                rating = float(rating_match.group(1))
                if 0 <= rating <= 5:
                    return rating
        except:
            pass
            
        return None
    
    def _generate_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Generate error result"""
        return {
            "success": False,
            "error": error_msg,
            "extraction_method": "screenshot_vision_analysis_failed"
        }

# Create service instance
screenshot_analyzer = ScreenshotAnalyzer()