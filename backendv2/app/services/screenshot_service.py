"""
Screenshot Service for Google Business Profile Scraping
Simple proof-of-concept using Selenium WebDriver
"""
import asyncio
import logging
import base64
import os
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class ScreenshotService:
    def __init__(self):
        self.timeout = 15
        self.screenshot_dir = "screenshots"
        
        # Create screenshots directory if it doesn't exist
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def _get_chrome_options(self) -> Options:
        """Configure Chrome options for headless browsing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Disable images and CSS for faster loading (optional)
        # chrome_options.add_argument("--disable-images")
        
        return chrome_options
    
    async def capture_google_business_screenshot(self, url: str) -> Dict[str, Any]:
        """
        Capture screenshot of Google Business Profile page
        Returns screenshot data and metadata
        """
        result = {
            "success": False,
            "screenshot_path": None,
            "screenshot_base64": None,
            "page_title": None,
            "final_url": None,
            "error": None,
            "metadata": {}
        }
        
        driver = None
        
        try:
            logger.info(f"📸 Starting screenshot capture for: {url}")
            
            # Initialize Chrome driver with webdriver-manager
            chrome_options = self._get_chrome_options()
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set page load timeout
            driver.set_page_load_timeout(self.timeout)
            
            # Navigate to the URL
            driver.get(url)
            
            # Wait for page to load and get final URL after redirects
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            final_url = driver.current_url
            page_title = driver.title
            
            logger.info(f"📍 Page loaded: {page_title}")
            logger.info(f"🔗 Final URL: {final_url}")
            
            # Wait for Google Business content to load
            # Look for common Google Business Profile elements
            try:
                # Wait for business name or rating to appear
                WebDriverWait(driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-attrid='title']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".rating")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'reviews')]"))
                    )
                )
                logger.info("✅ Google Business content detected")
            except TimeoutException:
                logger.warning("⚠️ Timeout waiting for business content, proceeding with screenshot")
            
            # Additional wait for dynamic content
            await asyncio.sleep(2)
            
            # Take screenshot
            screenshot_filename = f"google_business_{hash(url) % 10000}.png"
            screenshot_path = os.path.join(self.screenshot_dir, screenshot_filename)
            
            # Capture full page screenshot
            driver.save_screenshot(screenshot_path)
            
            # Also get screenshot as base64 for API usage
            screenshot_base64 = driver.get_screenshot_as_base64()
            
            # Get page dimensions and other metadata
            page_height = driver.execute_script("return document.body.scrollHeight")
            page_width = driver.execute_script("return document.body.scrollWidth")
            viewport_height = driver.execute_script("return window.innerHeight")
            viewport_width = driver.execute_script("return window.innerWidth")
            
            result.update({
                "success": True,
                "screenshot_path": screenshot_path,
                "screenshot_base64": screenshot_base64,
                "page_title": page_title,
                "final_url": final_url,
                "metadata": {
                    "page_height": page_height,
                    "page_width": page_width,
                    "viewport_height": viewport_height,
                    "viewport_width": viewport_width,
                    "screenshot_size": len(screenshot_base64) if screenshot_base64 else 0
                }
            })
            
            logger.info(f"✅ Screenshot captured successfully: {screenshot_path}")
            logger.info(f"📏 Page dimensions: {page_width}x{page_height}")
            
        except TimeoutException:
            result["error"] = "Page load timeout"
            logger.error(f"⏰ Timeout loading page: {url}")
        except WebDriverException as e:
            result["error"] = f"WebDriver error: {str(e)}"
            logger.error(f"🚫 WebDriver error: {str(e)}")
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            logger.error(f"❌ Unexpected error: {str(e)}")
        finally:
            # Clean up driver
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        return result
    
    async def test_screenshot_capture(self, url: str) -> Dict[str, Any]:
        """
        Test method to capture screenshot and return basic info
        """
        logger.info(f"🧪 Testing screenshot capture for: {url}")
        
        result = await self.capture_google_business_screenshot(url)
        
        if result["success"]:
            logger.info("✅ Screenshot test successful!")
            return {
                "status": "success",
                "screenshot_captured": True,
                "file_path": result["screenshot_path"],
                "page_title": result["page_title"],
                "final_url": result["final_url"],
                "page_dimensions": f"{result['metadata']['page_width']}x{result['metadata']['page_height']}",
                "screenshot_size_kb": round(result['metadata']['screenshot_size'] * 3/4 / 1024, 2)  # base64 to bytes to KB
            }
        else:
            logger.error(f"❌ Screenshot test failed: {result['error']}")
            return {
                "status": "failed",
                "error": result["error"],
                "screenshot_captured": False
            }

# Create service instance
screenshot_service = ScreenshotService()