#!/usr/bin/env python3
"""
Order Online Button Detection Test
Tests various methods to detect online ordering capabilities on restaurant websites
"""
import asyncio
import re
from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup

class OrderButtonDetector:
    def __init__(self):
        self.timeout = 10.0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    async def detect_order_online_features(self, website_url: str) -> Dict[str, Any]:
        """
        Comprehensive detection of online ordering capabilities
        """
        result = {
            "has_order_online": False,
            "order_buttons": [],
            "delivery_platforms": [],
            "ordering_methods": [],
            "confidence_score": 0,
            "details": {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                response = await client.get(website_url, follow_redirects=True)
                
                if response.status_code != 200:
                    result["error"] = f"HTTP {response.status_code}"
                    return result
                
                soup = BeautifulSoup(response.content, 'html.parser')
                html_content = response.text.lower()
                
                # Method 1: Button Text Detection
                order_buttons = self._detect_order_buttons(soup)
                result["order_buttons"] = order_buttons
                
                # Method 2: Delivery Platform Detection
                delivery_platforms = self._detect_delivery_platforms(soup, html_content)
                result["delivery_platforms"] = delivery_platforms
                
                # Method 3: Ordering Method Detection
                ordering_methods = self._detect_ordering_methods(soup, html_content)
                result["ordering_methods"] = ordering_methods
                
                # Method 4: URL Pattern Detection
                ordering_urls = self._detect_ordering_urls(soup)
                result["ordering_urls"] = ordering_urls
                
                # Method 5: Form Detection
                ordering_forms = self._detect_ordering_forms(soup)
                result["ordering_forms"] = ordering_forms
                
                # Calculate confidence and final determination
                confidence = self._calculate_confidence(result)
                result["confidence_score"] = confidence
                result["has_order_online"] = confidence > 50
                
                # Detailed analysis
                result["details"] = {
                    "button_count": len(order_buttons),
                    "platform_count": len(delivery_platforms),
                    "method_count": len(ordering_methods),
                    "url_indicators": len(ordering_urls),
                    "form_indicators": len(ordering_forms)
                }
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _detect_order_buttons(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Detect order online buttons by text content and attributes"""
        order_buttons = []
        
        # Common order button text patterns
        order_patterns = [
            r'order\s+online',
            r'order\s+now',
            r'place\s+order',
            r'start\s+order',
            r'order\s+delivery',
            r'order\s+pickup',
            r'order\s+takeout',
            r'delivery\s+order',
            r'pickup\s+order',
            r'online\s+menu',
            r'view\s+menu\s+&\s+order',
            r'menu\s+&\s+order'
        ]
        
        # Find all clickable elements
        clickable_elements = soup.find_all(['a', 'button', 'div', 'span'], 
                                         attrs={'href': True, 'onclick': True, 'class': True, 'id': True})
        clickable_elements.extend(soup.find_all(['a', 'button']))
        
        for element in clickable_elements:
            text = element.get_text().strip().lower()
            href = element.get('href', '').lower()
            class_attr = ' '.join(element.get('class', [])).lower()
            id_attr = element.get('id', '').lower()
            onclick = element.get('onclick', '').lower()
            
            # Check text content
            for pattern in order_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    order_buttons.append({
                        "type": "text_match",
                        "text": element.get_text().strip(),
                        "pattern": pattern,
                        "element": element.name,
                        "href": element.get('href', ''),
                        "confidence": 90
                    })
                    break
            
            # Check attributes for order-related keywords
            all_attrs = f"{href} {class_attr} {id_attr} {onclick}"
            order_keywords = ['order', 'delivery', 'pickup', 'takeout', 'menu', 'grubhub', 'doordash', 'ubereats']
            
            for keyword in order_keywords:
                if keyword in all_attrs:
                    order_buttons.append({
                        "type": "attribute_match",
                        "text": element.get_text().strip(),
                        "keyword": keyword,
                        "element": element.name,
                        "href": element.get('href', ''),
                        "confidence": 70
                    })
                    break
        
        return order_buttons
    
    def _detect_delivery_platforms(self, soup: BeautifulSoup, html_content: str) -> List[Dict[str, str]]:
        """Detect third-party delivery platform integrations"""
        platforms = []
        
        platform_patterns = {
            'doordash': [
                r'doordash\.com',
                r'door\s*dash',
                r'dd\.com'
            ],
            'ubereats': [
                r'ubereats\.com',
                r'uber\s*eats',
                r'uber\.com/eats'
            ],
            'grubhub': [
                r'grubhub\.com',
                r'grub\s*hub',
                r'seamless\.com'
            ],
            'postmates': [
                r'postmates\.com',
                r'post\s*mates'
            ],
            'seamless': [
                r'seamless\.com',
                r'seamless'
            ],
            'caviar': [
                r'trycaviar\.com',
                r'caviar'
            ],
            'slice': [
                r'slicelife\.com',
                r'slice'
            ],
            'menufy': [
                r'menufy\.com',
                r'menufy'
            ],
            'chownow': [
                r'chownow\.com',
                r'chow\s*now'
            ],
            'toast': [
                r'toasttab\.com',
                r'toast\s*tab'
            ]
        }
        
        # Check links and text content
        links = soup.find_all('a', href=True)
        
        for platform, patterns in platform_patterns.items():
            for pattern in patterns:
                # Check in links
                for link in links:
                    href = link.get('href', '').lower()
                    text = link.get_text().lower()
                    
                    if re.search(pattern, href, re.IGNORECASE) or re.search(pattern, text, re.IGNORECASE):
                        platforms.append({
                            "platform": platform,
                            "type": "link",
                            "url": link.get('href', ''),
                            "text": link.get_text().strip(),
                            "confidence": 95
                        })
                        break
                
                # Check in general content
                if re.search(pattern, html_content, re.IGNORECASE):
                    platforms.append({
                        "platform": platform,
                        "type": "content_mention",
                        "confidence": 80
                    })
        
        return platforms
    
    def _detect_ordering_methods(self, soup: BeautifulSoup, html_content: str) -> List[str]:
        """Detect different ordering methods available"""
        methods = []
        
        method_patterns = {
            'online_ordering': [
                r'order\s+online',
                r'online\s+ordering',
                r'web\s+ordering'
            ],
            'phone_ordering': [
                r'call\s+to\s+order',
                r'phone\s+orders?',
                r'order\s+by\s+phone'
            ],
            'delivery': [
                r'delivery\s+available',
                r'we\s+deliver',
                r'home\s+delivery'
            ],
            'pickup': [
                r'pickup\s+available',
                r'takeout',
                r'take\s+out',
                r'curbside\s+pickup'
            ],
            'dine_in': [
                r'dine\s+in',
                r'eat\s+in',
                r'restaurant\s+seating'
            ],
            'catering': [
                r'catering\s+available',
                r'catering\s+orders?',
                r'party\s+orders?'
            ]
        }
        
        for method, patterns in method_patterns.items():
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    methods.append(method)
                    break
        
        return list(set(methods))  # Remove duplicates
    
    def _detect_ordering_urls(self, soup: BeautifulSoup) -> List[str]:
        """Detect URLs that likely lead to ordering systems"""
        ordering_urls = []
        
        url_patterns = [
            r'order',
            r'menu',
            r'delivery',
            r'pickup',
            r'takeout',
            r'cart',
            r'checkout'
        ]
        
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '').lower()
            for pattern in url_patterns:
                if pattern in href:
                    ordering_urls.append({
                        "url": link.get('href'),
                        "text": link.get_text().strip(),
                        "pattern": pattern
                    })
                    break
        
        return ordering_urls
    
    def _detect_ordering_forms(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Detect forms that might be used for ordering"""
        ordering_forms = []
        
        forms = soup.find_all('form')
        
        for form in forms:
            form_text = form.get_text().lower()
            action = form.get('action', '').lower()
            form_id = form.get('id', '').lower()
            form_class = ' '.join(form.get('class', [])).lower()
            
            # Look for order-related keywords in form
            order_keywords = ['order', 'cart', 'checkout', 'delivery', 'pickup', 'menu']
            
            for keyword in order_keywords:
                if (keyword in form_text or keyword in action or 
                    keyword in form_id or keyword in form_class):
                    
                    # Check for input fields that suggest ordering
                    inputs = form.find_all(['input', 'select', 'textarea'])
                    input_types = [inp.get('type', '') for inp in inputs]
                    input_names = [inp.get('name', '').lower() for inp in inputs]
                    
                    ordering_forms.append({
                        "keyword": keyword,
                        "action": form.get('action', ''),
                        "input_count": len(inputs),
                        "input_types": input_types,
                        "input_names": input_names,
                        "confidence": 75
                    })
                    break
        
        return ordering_forms
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> int:
        """Calculate confidence score for online ordering detection"""
        confidence = 0
        
        # Button detection (high confidence)
        for button in result["order_buttons"]:
            if button["type"] == "text_match":
                confidence += 30
            elif button["type"] == "attribute_match":
                confidence += 20
        
        # Platform detection (very high confidence)
        for platform in result["delivery_platforms"]:
            if platform["type"] == "link":
                confidence += 35
            elif platform["type"] == "content_mention":
                confidence += 25
        
        # Method detection (medium confidence)
        methods = result["ordering_methods"]
        if "online_ordering" in methods:
            confidence += 25
        if "delivery" in methods:
            confidence += 15
        if "pickup" in methods:
            confidence += 15
        
        # URL detection (medium confidence)
        confidence += min(len(result["ordering_urls"]) * 10, 30)
        
        # Form detection (medium confidence)
        confidence += min(len(result["ordering_forms"]) * 15, 30)
        
        return min(confidence, 100)

async def test_order_detection():
    """Test order button detection on various restaurant websites"""
    detector = OrderButtonDetector()
    
    test_urls = [
        "https://charminarexpresssv.com/",
        "https://www.dominos.com/",
        "https://www.pizzahut.com/",
        "https://www.mcdonalds.com/"
    ]
    
    print("🍽️ TESTING ORDER ONLINE BUTTON DETECTION")
    print("=" * 60)
    
    for url in test_urls:
        print(f"\n🌐 Testing: {url}")
        print("-" * 40)
        
        try:
            result = await detector.detect_order_online_features(url)
            
            print(f"✅ Has Order Online: {result['has_order_online']}")
            print(f"📊 Confidence Score: {result['confidence_score']}%")
            
            if result["order_buttons"]:
                print(f"🔘 Order Buttons Found: {len(result['order_buttons'])}")
                for button in result["order_buttons"][:3]:  # Show first 3
                    print(f"   - '{button['text']}' ({button['type']})")
            
            if result["delivery_platforms"]:
                print(f"🚚 Delivery Platforms: {len(result['delivery_platforms'])}")
                for platform in result["delivery_platforms"]:
                    print(f"   - {platform['platform']} ({platform['type']})")
            
            if result["ordering_methods"]:
                print(f"📋 Ordering Methods: {', '.join(result['ordering_methods'])}")
            
            print(f"📈 Details: {result['details']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_order_detection())