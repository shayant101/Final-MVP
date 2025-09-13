"""
AI Digital Presence Grader Service
Analyzes restaurant's digital presence and provides actionable recommendations
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from .openai_service import openai_service
from .web_scraper_service import web_scraper_service
from .google_business_scraper import google_business_scraper
from .openai_grader_service import openai_grader_service

logger = logging.getLogger(__name__)

class AIGraderService:
    def __init__(self):
        self.openai_service = openai_service
        
    async def analyze_digital_presence(self, restaurant_data: Dict[str, Any], mode: str = "classic") -> Dict[str, Any]:
        if mode == "openai":
            logger.info("Routing to OpenAI Digital Presence Grader")
            return await openai_grader_service.analyze_digital_presence(restaurant_data)
        else:
            logger.info("Using Classic Digital Presence Grader")
            return await self.classic_analyze_digital_presence(restaurant_data)

    async def classic_analyze_digital_presence(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze restaurant's digital presence and generate comprehensive grade using real web scraping
        """
        try:
            # Extract restaurant information
            restaurant_name = restaurant_data.get('name', 'Restaurant')
            website_url = restaurant_data.get('website', '')
            google_business_url = restaurant_data.get('google_business_url', '')
            social_media = restaurant_data.get('social_media', {})
            menu_items = restaurant_data.get('menu_items', [])
            current_marketing = restaurant_data.get('current_marketing', {})
            
            # Basic website validation - minimal approach
            website_validation = await self._validate_website_basic(website_url)
            logger.info(f"✅ Website validation completed: accessible={website_validation.get('accessible', False)}")
            
            # Analyze each component with real scraping data
            website_analysis = await self._analyze_website_with_validation(restaurant_name, website_url, website_validation)
            social_analysis = await self._analyze_social_media(restaurant_name, social_media)
            
            # Try real Google Business scraping first, fallback to basic if it fails
            google_analysis = await self._analyze_google_business_with_scraping(restaurant_name, google_business_url)
            menu_analysis = await self._analyze_menu_optimization(restaurant_name, menu_items)
            marketing_analysis = await self._analyze_marketing_strategy(restaurant_name, current_marketing)
            
            # Calculate overall grade and recommendations
            overall_grade = await self._calculate_overall_grade({
                'website': website_analysis,
                'social': social_analysis,
                'google': google_analysis,
                'menu': menu_analysis,
                'marketing': marketing_analysis
            })
            
            # Generate priority action plan
            action_plan = await self._generate_action_plan(overall_grade, {
                'website': website_analysis,
                'social': social_analysis,
                'google': google_analysis,
                'menu': menu_analysis,
                'marketing': marketing_analysis
            })
            
            return {
                "success": True,
                "overall_grade": overall_grade,
                "component_scores": {
                    "website": website_analysis,
                    "social_media": social_analysis,
                    "google_business": google_analysis,
                    "menu_optimization": menu_analysis,
                    "marketing_strategy": marketing_analysis
                },
                "action_plan": action_plan,
                "revenue_impact": self._calculate_revenue_impact(overall_grade),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze digital presence: {str(e)}")
            return await self._generate_mock_analysis(restaurant_data)
    
    async def _validate_website_basic(self, website_url: str) -> Dict[str, Any]:
        """
        Basic website validation - just check if URL is accessible
        """
        validation_result = {
            "accessible": False,
            "has_ssl": False,
            "status_code": 0,
            "response_time": 0,
            "error": None
        }
        
        if not website_url:
            validation_result["error"] = "No website URL provided"
            return validation_result
        
        try:
            import httpx
            import time
            
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(website_url, follow_redirects=True)
                
                validation_result["accessible"] = response.status_code == 200
                validation_result["has_ssl"] = website_url.startswith('https://')
                validation_result["status_code"] = response.status_code
                validation_result["response_time"] = round(time.time() - start_time, 2)
                
                logger.info(f"✅ Website validation: {website_url} - Status: {response.status_code}, Time: {validation_result['response_time']}s")
                
        except Exception as e:
            validation_result["error"] = str(e)
            logger.warning(f"⚠️ Website validation failed for {website_url}: {str(e)}")
        
        return validation_result
    
    async def _analyze_website_with_validation(self, restaurant_name: str, website_url: str, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze website using basic validation data"""
        try:
            if not website_url:
                return {
                    "score": 20,
                    "grade": "F",
                    "issues": ["No website URL provided"],
                    "recommendations": [
                        "Create a professional restaurant website",
                        "Include menu, hours, location, and contact info",
                        "Optimize for mobile devices",
                        "Add online ordering capability"
                    ],
                    "priority": "HIGH",
                    "validation_data": validation_result
                }
            
            # Calculate score based on basic validation
            score = 0
            issues = []
            recommendations = []
            
            # Website accessibility (30 points)
            if validation_result.get('accessible'):
                score += 30
                logger.info(f"✅ Website is accessible: {website_url}")
            else:
                issues.append("Website is not accessible or returns errors")
                recommendations.append("Fix website accessibility issues")
                logger.warning(f"⚠️ Website not accessible: {website_url}")
            
            # SSL certificate (15 points)
            if validation_result.get('has_ssl'):
                score += 15
            else:
                issues.append("No SSL certificate (not using HTTPS)")
                recommendations.append("Enable SSL certificate for security and SEO")
            
            # Response time (15 points)
            response_time = validation_result.get('response_time', 0)
            if response_time > 0:
                if response_time <= 2.0:
                    score += 15
                elif response_time <= 4.0:
                    score += 10
                    issues.append("Website loads slowly")
                    recommendations.append("Optimize website loading speed")
                else:
                    score += 5
                    issues.append("Website loads very slowly")
                    recommendations.append("Significantly improve website loading speed")
            
            # Online ordering analysis (25 points potential)
            if validation_result.get('accessible'):
                score += 5  # Small bonus for being accessible
                
                # Try to detect online ordering capabilities
                try:
                    from .web_scraper_service import web_scraper_service
                    
                    # Properly await the order analysis since we're already in an async function
                    logger.info(f"🔍 Analyzing online ordering capabilities for: {website_url}")
                    order_analysis = await web_scraper_service._analyze_order_capabilities(website_url)
                    
                    if order_analysis.get("has_ordering", False):
                        confidence = order_analysis.get("confidence", 0)
                        if confidence >= 80:
                            score += 15
                            logger.info(f"✅ Online ordering detected with high confidence: {confidence}% (+15 points)")
                        elif confidence >= 50:
                            score += 10
                            logger.info(f"✅ Online ordering detected with medium confidence: {confidence}% (+10 points)")
                        else:
                            score += 5
                            logger.info(f"✅ Online ordering detected with low confidence: {confidence}% (+5 points)")
                        
                        # Add specific recommendations based on findings
                        order_details = order_analysis.get("details", {})
                        if order_details.get("platform_count", 0) > 0:
                            recommendations.append("Optimize delivery platform integrations")
                        if order_details.get("button_count", 0) > 0:
                            recommendations.append("Ensure order buttons are prominently displayed")
                    else:
                        issues.append("No online ordering capability detected")
                        recommendations.append("Add online ordering system to increase revenue")
                        logger.info(f"❌ No online ordering detected for: {website_url}")
                        
                except Exception as e:
                    logger.warning(f"Could not analyze online ordering: {str(e)}")
                    recommendations.append("Consider adding online ordering capability")
                
                # Standard recommendations
                recommendations.extend([
                    "Add online menu with photos and descriptions",
                    "Include clear contact information and hours",
                    "Optimize for mobile devices"
                ])
            
            # Convert to letter grade
            if score >= 90:
                grade = 'A'
                priority = 'LOW'
            elif score >= 80:
                grade = 'B'
                priority = 'LOW'
            elif score >= 70:
                grade = 'C'
                priority = 'MEDIUM'
            elif score >= 60:
                grade = 'D'
                priority = 'HIGH'
            else:
                grade = 'F'
                priority = 'HIGH'
            
            return {
                "score": min(score, 100),
                "grade": grade,
                "issues": issues,
                "recommendations": recommendations,
                "priority": priority,
                "validation_data": {
                    "accessible": validation_result.get('accessible', False),
                    "has_ssl": validation_result.get('has_ssl', False),
                    "status_code": validation_result.get('status_code', 0),
                    "response_time": validation_result.get('response_time', 0),
                    "validation_method": "basic_http_check"
                }
            }
            
        except Exception as e:
            logger.error(f"Website analysis with validation failed: {str(e)}")
            return await self._analyze_website(restaurant_name, website_url)
    
    async def _analyze_google_business_basic(self, restaurant_name: str, google_business_url: str) -> Dict[str, Any]:
        """Basic Google Business Profile analysis without scraping"""
        try:
            if not google_business_url:
                return {
                    "score": 30,
                    "grade": "F",
                    "issues": ["No Google Business Profile URL provided"],
                    "recommendations": [
                        "Create Google Business Profile",
                        "Verify business ownership",
                        "Add complete business information",
                        "Upload high-quality photos"
                    ],
                    "priority": "HIGH",
                    "analysis_method": "basic_url_check"
                }
            
            # Basic URL validation
            score = 50  # Base score for having a URL
            issues = []
            recommendations = []
            
            # Check if URL looks like a valid Google Business Profile
            valid_google_patterns = [
                'maps.google.com',
                'google.com/maps',
                'goo.gl/maps',
                'business.google.com',
                'g.co/kgs',  # Google's official URL shortener for business profiles
                'g.co',       # Google's URL shortener domain
                'share.google.com',
                'share.google'  # Newer Google sharing format
            ]
            
            is_valid_google_url = any(pattern in google_business_url.lower() for pattern in valid_google_patterns)
            
            if is_valid_google_url:
                score += 20
                logger.info(f"✅ Valid Google Business Profile URL format: {google_business_url}")
            else:
                issues.append("URL doesn't appear to be a valid Google Business Profile")
                recommendations.append("Verify Google Business Profile URL is correct")
                logger.warning(f"⚠️ Invalid Google Business Profile URL format: {google_business_url}")
            
            # Add standard recommendations
            recommendations.extend([
                "Ensure business information is complete and accurate",
                "Upload high-quality photos of food, interior, and exterior",
                "Encourage customers to leave reviews",
                "Respond to customer reviews promptly",
                "Keep business hours updated"
            ])
            
            # Convert to letter grade
            if score >= 90:
                grade = 'A'
                priority = 'LOW'
            elif score >= 80:
                grade = 'B'
                priority = 'LOW'
            elif score >= 70:
                grade = 'C'
                priority = 'MEDIUM'
            elif score >= 60:
                grade = 'D'
                priority = 'HIGH'
            else:
                grade = 'F'
                priority = 'HIGH'
            
            return {
                "score": min(score, 100),
                "grade": grade,
                "issues": issues,
                "recommendations": recommendations,
                "priority": priority,
                "analysis_method": "basic_url_validation",
                "url_provided": bool(google_business_url),
                "url_format_valid": is_valid_google_url
            }
            
        except Exception as e:
            logger.error(f"Google Business basic analysis failed: {str(e)}")
            return self._get_fallback_google_analysis()
    
    async def _analyze_google_business_with_scraping(self, restaurant_name: str, google_business_url: str) -> Dict[str, Any]:
        """Analyze Google Business Profile using real scraping data"""
        try:
            if not google_business_url:
                return {
                    "score": 30,
                    "grade": "F",
                    "issues": ["No Google Business Profile URL provided"],
                    "recommendations": [
                        "Create Google Business Profile",
                        "Verify business ownership",
                        "Add complete business information",
                        "Upload high-quality photos"
                    ],
                    "priority": "HIGH",
                    "analysis_method": "no_url_provided"
                }
            
            # First validate URL format
            valid_google_patterns = [
                'maps.google.com',
                'google.com/maps',
                'goo.gl/maps',
                'business.google.com',
                'g.co/kgs',
                'g.co',
                'share.google.com',
                'share.google'  # Newer Google sharing format
            ]
            
            is_valid_google_url = any(pattern in google_business_url.lower() for pattern in valid_google_patterns)
            
            if not is_valid_google_url:
                logger.warning(f"⚠️ Invalid Google Business Profile URL format: {google_business_url}")
                return await self._analyze_google_business_basic(restaurant_name, google_business_url)
            
            # Attempt real scraping
            logger.info(f"🔍 Attempting to scrape Google Business Profile: {google_business_url}")
            scraped_data = await google_business_scraper.scrape_basic_info(google_business_url)
            
            if not scraped_data.get("success"):
                logger.warning(f"⚠️ Scraping failed, falling back to basic analysis: {scraped_data.get('error')}")
                return await self._analyze_google_business_basic(restaurant_name, google_business_url)
            
            # Calculate score based on scraped data
            score = 0
            issues = []
            recommendations = []
            
            # Business name verification (20 points)
            scraped_name = scraped_data.get("business_name")
            if scraped_name:
                score += 20
                logger.info(f"✅ Found business name: {scraped_name}")
                
                # Check if scraped name matches provided name
                if restaurant_name.lower() in scraped_name.lower() or scraped_name.lower() in restaurant_name.lower():
                    score += 5  # Bonus for name consistency
                else:
                    issues.append(f"Business name mismatch: Profile shows '{scraped_name}' but you provided '{restaurant_name}'")
                    recommendations.append("Ensure business name consistency across all platforms")
            else:
                issues.append("Business name not found on profile")
                recommendations.append("Add clear business name to Google Business Profile")
            
            # Reviews and ratings (40 points)
            rating = scraped_data.get("rating")
            review_count = scraped_data.get("review_count")
            
            if rating is not None:
                if rating >= 4.5:
                    score += 25
                elif rating >= 4.0:
                    score += 20
                elif rating >= 3.5:
                    score += 15
                elif rating >= 3.0:
                    score += 10
                else:
                    score += 5
                    issues.append(f"Low rating: {rating}/5 stars")
                    recommendations.append("Focus on improving customer satisfaction and service quality")
                
                logger.info(f"✅ Found rating: {rating}/5 stars")
            else:
                issues.append("No customer ratings found")
                recommendations.append("Encourage customers to leave reviews")
            
            if review_count is not None:
                if review_count >= 100:
                    score += 15
                elif review_count >= 50:
                    score += 12
                elif review_count >= 20:
                    score += 8
                elif review_count >= 5:
                    score += 5
                else:
                    score += 2
                    issues.append(f"Low review count: {review_count} reviews")
                    recommendations.append("Actively request customer reviews")
                
                logger.info(f"✅ Found {review_count} reviews")
            else:
                issues.append("Review count not available")
                recommendations.append("Encourage more customer reviews")
            
            # Categories/Business type (20 points)
            categories = scraped_data.get("categories", [])
            if categories:
                score += 20
                logger.info(f"✅ Found categories: {categories}")
                
                # Check if categories match the provided cuisine type
                cuisine_type = restaurant_name  # You might want to pass cuisine_type as parameter
                category_text = " ".join(categories).lower()
                if any(cat.lower() in category_text for cat in ["restaurant", "food", "dining", "cafe", "bar"]):
                    score += 5  # Bonus for food-related categories
                
            else:
                issues.append("Business categories not found")
                recommendations.append("Add appropriate business categories to your profile")
            
            # URL accessibility bonus (15 points)
            if scraped_data.get("success"):
                score += 15  # Bonus for profile being accessible
            
            # Add standard recommendations
            recommendations.extend([
                "Keep business information updated",
                "Respond to customer reviews promptly",
                "Upload high-quality photos regularly",
                "Post updates about specials and events"
            ])
            
            # Convert to letter grade
            if score >= 90:
                grade = 'A'
                priority = 'LOW'
            elif score >= 80:
                grade = 'B'
                priority = 'LOW'
            elif score >= 70:
                grade = 'C'
                priority = 'MEDIUM'
            elif score >= 60:
                grade = 'D'
                priority = 'HIGH'
            else:
                grade = 'F'
                priority = 'HIGH'
            
            return {
                "score": min(score, 100),
                "grade": grade,
                "issues": issues,
                "recommendations": recommendations,
                "priority": priority,
                "analysis_method": "real_scraping",
                "scraped_data": {
                    "business_name": scraped_name,
                    "rating": rating,
                    "review_count": review_count,
                    "categories": categories,
                    "scraping_success": scraped_data.get("success"),
                    "final_url": scraped_data.get("scraped_data", {}).get("final_url")
                }
            }
            
        except Exception as e:
            logger.error(f"Google Business scraping analysis failed: {str(e)}")
            # Fallback to basic analysis
            return await self._analyze_google_business_basic(restaurant_name, google_business_url)

    async def analyze_google_business_with_openai(self, restaurant_name: str, google_business_url: str) -> Dict[str, Any]:
        """Analyze Google Business Profile using OpenAI"""
        try:
            logger.info(f"🤖 Analyzing Google Business Profile with OpenAI for: {restaurant_name}")
            
            # Scrape basic info first to get context
            scraped_data = await google_business_scraper.scrape_basic_info(google_business_url)
            
            if not scraped_data.get("success"):
                logger.warning(f"⚠️ Scraping failed for OpenAI analysis, falling back to basic analysis.")
                return await self._analyze_google_business_basic(restaurant_name, google_business_url)

            # Create a detailed prompt for OpenAI
            prompt = f"""
            Analyze the Google Business Profile for the restaurant '{restaurant_name}'.
            
            Scraped Data:
            - Business Name: {scraped_data.get('business_name', 'N/A')}
            - Rating: {scraped_data.get('rating', 'N/A')} stars
            - Review Count: {scraped_data.get('review_count', 'N/A')}
            - Categories: {', '.join(scraped_data.get('categories', []))}
            
            Based on this data and your expertise, provide a detailed analysis covering:
            1.  **Overall Score**: A score from 0-100.
            2.  **Grade**: A letter grade from A-F.
            3.  **Strengths**: 2-3 key strengths.
            4.  **Issues**: 3-4 major issues or areas for improvement.
            5.  **Recommendations**: A prioritized list of 5 actionable recommendations.
            
            Format the output as a JSON object with the following keys:
            "overall_score", "grade", "strengths", "issues", "recommendations"
            """
            
            messages = [{"role": "system", "content": "You are a Google Business Profile optimization expert for restaurants."},
                        {"role": "user", "content": prompt}]
            
            openai_response_str = await self.openai_service._make_openai_request(messages)
            
            try:
                # Clean the response string by removing markdown formatting
                if openai_response_str.startswith("```json"):
                    openai_response_str = openai_response_str[7:-3].strip()
                
                openai_response = json.loads(openai_response_str)
            except json.JSONDecodeError:
                logger.error("Failed to parse OpenAI response as JSON.")
                return await self._analyze_google_business_basic(restaurant_name, google_business_url)

            return {
                "overall_score": openai_response.get("overall_score", 0),
                "grade": openai_response.get("grade", "N/A"),
                "priority": "HIGH" if openai_response.get("overall_score", 100) < 70 else "MEDIUM",
                "strengths": openai_response.get("strengths", []),
                "issues": openai_response.get("issues", []),
                "recommendations": openai_response.get("recommendations", []),
                "scraped_data": scraped_data,
                "analysis_method": "openai_enhanced",
                "grader_version": "2.0-openai"
            }

        except Exception as e:
            logger.error(f"Google Business OpenAI analysis failed: {str(e)}")
            return await self._analyze_google_business_basic(restaurant_name, google_business_url)
    
    async def _analyze_website_with_real_data(self, restaurant_name: str, website_url: str, scraped_website_data: Optional[Dict]) -> Dict[str, Any]:
        """Analyze website using real scraped data"""
        try:
            if not website_url:
                return {
                    "score": 20,
                    "grade": "F",
                    "issues": ["No website URL provided"],
                    "recommendations": [
                        "Create a professional restaurant website",
                        "Include menu, hours, location, and contact info",
                        "Optimize for mobile devices",
                        "Add online ordering capability"
                    ],
                    "priority": "HIGH"
                }
            
            if not scraped_website_data:
                # Fallback to original analysis if scraping failed
                return await self._analyze_website(restaurant_name, website_url)
            
            # Calculate score based on real data
            score = 0
            issues = []
            recommendations = []
            
            # Title analysis (20 points)
            if scraped_website_data.get('title'):
                score += 15
                title_length = len(scraped_website_data['title'])
                if 30 <= title_length <= 60:
                    score += 5
                else:
                    issues.append("Page title length not optimal")
                    recommendations.append("Optimize page title to 30-60 characters")
            else:
                issues.append("Missing page title")
                recommendations.append("Add descriptive page title")
            
            # Meta description (15 points)
            if scraped_website_data.get('description'):
                score += 10
                desc_length = len(scraped_website_data['description'])
                if 120 <= desc_length <= 160:
                    score += 5
                else:
                    issues.append("Meta description length not optimal")
                    recommendations.append("Optimize meta description to 120-160 characters")
            else:
                issues.append("Missing meta description")
                recommendations.append("Add compelling meta description")
            
            # SSL and security (10 points)
            if scraped_website_data.get('has_ssl'):
                score += 10
            else:
                issues.append("No SSL certificate")
                recommendations.append("Enable SSL certificate for security")
            
            # Mobile friendliness (15 points)
            if scraped_website_data.get('mobile_friendly'):
                score += 15
            else:
                issues.append("Not mobile-friendly")
                recommendations.append("Make website mobile-responsive")
            
            # Restaurant-specific content (25 points)
            content_score = 0
            if scraped_website_data.get('has_menu'):
                content_score += 8
            else:
                issues.append("No menu found")
                recommendations.append("Add online menu")
            
            if scraped_website_data.get('has_contact'):
                content_score += 8
            else:
                issues.append("Contact information unclear")
                recommendations.append("Add clear contact information")
            
            if scraped_website_data.get('has_hours'):
                content_score += 5
            else:
                issues.append("Business hours not found")
                recommendations.append("Display business hours prominently")
            
            if scraped_website_data.get('has_online_ordering'):
                content_score += 4
            else:
                recommendations.append("Consider adding online ordering")
            
            score += content_score
            
            # SEO score (15 points)
            seo_score = scraped_website_data.get('seo_score', 0)
            score += int(seo_score * 0.15)
            
            if seo_score < 70:
                issues.append("SEO optimization needed")
                recommendations.append("Improve SEO with better structure and content")
            
            # Convert to letter grade
            if score >= 90:
                grade = 'A'
                priority = 'LOW'
            elif score >= 80:
                grade = 'B'
                priority = 'LOW'
            elif score >= 70:
                grade = 'C'
                priority = 'MEDIUM'
            elif score >= 60:
                grade = 'D'
                priority = 'HIGH'
            else:
                grade = 'F'
                priority = 'HIGH'
            
            return {
                "score": min(score, 100),
                "grade": grade,
                "issues": issues,
                "recommendations": recommendations,
                "priority": priority,
                "scraped_data": {
                    "title": scraped_website_data.get('title', ''),
                    "has_ssl": scraped_website_data.get('has_ssl', False),
                    "mobile_friendly": scraped_website_data.get('mobile_friendly', False),
                    "seo_score": scraped_website_data.get('seo_score', 0),
                    "images_count": scraped_website_data.get('images_count', 0),
                    "social_links_found": len(scraped_website_data.get('social_links', {}))
                }
            }
            
        except Exception as e:
            logger.error(f"Website analysis with real data failed: {str(e)}")
            return await self._analyze_website(restaurant_name, website_url)
    
    async def _analyze_social_media_with_real_data(self, restaurant_name: str, provided_social: Dict[str, Any], scraped_social_links: Dict[str, str]) -> Dict[str, Any]:
        """Analyze social media presence using real scraped data"""
        try:
            # Combine provided social media info with scraped links
            all_social_platforms = set()
            
            # Add provided platforms
            if provided_social:
                all_social_platforms.update(provided_social.keys())
            
            # Add scraped platforms
            if scraped_social_links:
                all_social_platforms.update(scraped_social_links.keys())
            
            platform_count = len(all_social_platforms)
            
            # Calculate score based on platform presence
            score = 0
            issues = []
            recommendations = []
            
            # Platform coverage (40 points)
            essential_platforms = ['facebook', 'instagram', 'google']
            found_essential = sum(1 for platform in essential_platforms if platform in all_social_platforms)
            score += found_essential * 13  # 13 points per essential platform
            
            if 'facebook' not in all_social_platforms:
                issues.append("No Facebook presence found")
                recommendations.append("Create Facebook business page")
            
            if 'instagram' not in all_social_platforms:
                issues.append("No Instagram presence found")
                recommendations.append("Create Instagram business account")
            
            if 'google' not in all_social_platforms:
                issues.append("No Google My Business found")
                recommendations.append("Set up Google My Business profile")
            
            # Additional platforms (20 points)
            additional_platforms = ['twitter', 'linkedin', 'youtube', 'tiktok', 'yelp']
            found_additional = sum(1 for platform in additional_platforms if platform in all_social_platforms)
            score += min(found_additional * 4, 20)  # Max 20 points for additional platforms
            
            # Consistency bonus (20 points)
            if platform_count >= 3:
                score += 20
            elif platform_count >= 2:
                score += 10
            else:
                issues.append("Limited social media presence")
                recommendations.append("Expand to multiple social platforms")
            
            # Integration bonus (20 points)
            if scraped_social_links:
                score += 20  # Bonus for having social links on website
            else:
                issues.append("Social media not linked from website")
                recommendations.append("Add social media links to website")
            
            # Convert to letter grade
            if score >= 90:
                grade = 'A'
                priority = 'LOW'
            elif score >= 80:
                grade = 'B'
                priority = 'LOW'
            elif score >= 70:
                grade = 'C'
                priority = 'MEDIUM'
            elif score >= 60:
                grade = 'D'
                priority = 'HIGH'
            else:
                grade = 'F'
                priority = 'HIGH'
            
            return {
                "score": min(score, 100),
                "grade": grade,
                "issues": issues,
                "recommendations": recommendations,
                "priority": priority,
                "found_platforms": list(all_social_platforms),
                "scraped_links": scraped_social_links,
                "platform_analysis": {
                    "total_platforms": platform_count,
                    "essential_platforms": found_essential,
                    "additional_platforms": found_additional,
                    "website_integration": bool(scraped_social_links)
                }
            }
            
        except Exception as e:
            logger.error(f"Social media analysis with real data failed: {str(e)}")
            return await self._analyze_social_media(restaurant_name, provided_social)
    
    async def _analyze_google_business_with_real_data(self, restaurant_name: str, google_business_url: str, scraped_google_data: Optional[Dict]) -> Dict[str, Any]:
        """Analyze Google Business Profile using real scraped data"""
        try:
            if not google_business_url:
                return {
                    "score": 30,
                    "grade": "F",
                    "issues": ["No Google Business Profile URL provided"],
                    "recommendations": [
                        "Create Google Business Profile",
                        "Verify business ownership",
                        "Add complete business information",
                        "Upload high-quality photos"
                    ],
                    "priority": "HIGH"
                }
            
            if not scraped_google_data:
                # Fallback if scraping failed
                return {
                    "score": 50,
                    "grade": "F",
                    "issues": ["Could not access Google Business Profile"],
                    "recommendations": [
                        "Ensure Google Business Profile is public",
                        "Verify business ownership",
                        "Complete all profile sections"
                    ],
                    "priority": "HIGH"
                }
            
            score = 0
            issues = []
            recommendations = []
            
            # Basic profile setup (30 points)
            if scraped_google_data.get('name'):
                score += 10
            else:
                issues.append("Business name missing")
            
            if scraped_google_data.get('address'):
                score += 10
            else:
                issues.append("Address information incomplete")
                recommendations.append("Add complete address information")
            
            if scraped_google_data.get('phone'):
                score += 10
            else:
                issues.append("Phone number missing")
                recommendations.append("Add business phone number")
            
            # Verification status (20 points)
            if scraped_google_data.get('verified'):
                score += 20
            else:
                issues.append("Business not verified")
                recommendations.append("Verify Google Business Profile ownership")
            
            # Reviews and ratings (25 points)
            rating = scraped_google_data.get('rating', 0)
            review_count = scraped_google_data.get('review_count', 0)
            
            if rating >= 4.0:
                score += 15
            elif rating >= 3.0:
                score += 10
            elif rating > 0:
                score += 5
            else:
                issues.append("No customer ratings")
                recommendations.append("Encourage customers to leave reviews")
            
            if review_count >= 50:
                score += 10
            elif review_count >= 20:
                score += 7
            elif review_count >= 5:
                score += 5
            else:
                issues.append("Insufficient customer reviews")
                recommendations.append("Actively request customer reviews")
            
            # Photos (15 points)
            photos_count = scraped_google_data.get('photos_count', 0)
            if photos_count >= 20:
                score += 15
            elif photos_count >= 10:
                score += 10
            elif photos_count >= 5:
                score += 5
            else:
                issues.append("Insufficient photos")
                recommendations.append("Upload high-quality photos of food, interior, and exterior")
            
            # Website link (10 points)
            if scraped_google_data.get('website'):
                score += 10
            else:
                issues.append("No website linked")
                recommendations.append("Link business website to Google profile")
            
            # Convert to letter grade
            if score >= 90:
                grade = 'A'
                priority = 'LOW'
            elif score >= 80:
                grade = 'B'
                priority = 'LOW'
            elif score >= 70:
                grade = 'C'
                priority = 'MEDIUM'
            elif score >= 60:
                grade = 'D'
                priority = 'HIGH'
            else:
                grade = 'F'
                priority = 'HIGH'
            
            return {
                "score": min(score, 100),
                "grade": grade,
                "issues": issues,
                "recommendations": recommendations,
                "priority": priority,
                "scraped_data": {
                    "name": scraped_google_data.get('name', ''),
                    "rating": rating,
                    "review_count": review_count,
                    "verified": scraped_google_data.get('verified', False),
                    "photos_count": photos_count,
                    "has_website": bool(scraped_google_data.get('website')),
                    "address": scraped_google_data.get('address', ''),
                    "phone": scraped_google_data.get('phone', '')
                }
            }
            
        except Exception as e:
            logger.error(f"Google Business analysis with real data failed: {str(e)}")
            return self._get_fallback_google_analysis()
    
    async def _analyze_website(self, restaurant_name: str, website_url: str) -> Dict[str, Any]:
        """Analyze website presence and optimization"""
        try:
            if not website_url:
                return {
                    "score": 20,
                    "grade": "F",
                    "issues": ["No website URL provided"],
                    "recommendations": [
                        "Create a professional restaurant website",
                        "Include menu, hours, location, and contact info",
                        "Optimize for mobile devices",
                        "Add online ordering capability"
                    ],
                    "priority": "HIGH"
                }
            
            # Mock website analysis (in real implementation, would crawl website)
            messages = [
                {
                    "role": "system",
                    "content": """You are a restaurant digital marketing expert. Analyze the website information provided and give a score from 0-100 with specific recommendations.
                    
                    Consider:
                    - Mobile optimization
                    - Menu accessibility
                    - Contact information clarity
                    - Online ordering integration
                    - SEO optimization
                    - Loading speed
                    - Visual appeal
                    
                    Format response as:
                    SCORE: [0-100]
                    GRADE: [A-F]
                    ISSUES: [list of issues]
                    RECOMMENDATIONS: [list of recommendations]
                    PRIORITY: [HIGH/MEDIUM/LOW]"""
                },
                {
                    "role": "user",
                    "content": f"Analyze website for {restaurant_name} at {website_url}. Provide detailed assessment and recommendations."
                }
            ]
            
            response = await self.openai_service._make_openai_request(messages, max_tokens=400)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Website analysis failed: {str(e)}")
            return self._get_fallback_website_analysis()
    
    async def _analyze_social_media(self, restaurant_name: str, social_media: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze social media presence"""
        try:
            platforms = social_media.keys() if social_media else []
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a social media marketing expert for restaurants. Analyze the social media presence and provide actionable recommendations.
                    
                    Consider:
                    - Platform coverage (Instagram, Facebook, TikTok, etc.)
                    - Content quality and frequency
                    - Engagement rates
                    - Visual consistency
                    - Local community engagement
                    - User-generated content
                    
                    Format response as:
                    SCORE: [0-100]
                    GRADE: [A-F]
                    ISSUES: [list of issues]
                    RECOMMENDATIONS: [list of recommendations]
                    PRIORITY: [HIGH/MEDIUM/LOW]"""
                },
                {
                    "role": "user",
                    "content": f"Analyze social media presence for {restaurant_name}. Current platforms: {', '.join(platforms) if platforms else 'None'}. Provide detailed assessment."
                }
            ]
            
            response = await self.openai_service._make_openai_request(messages, max_tokens=400)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Social media analysis failed: {str(e)}")
            return self._get_fallback_social_analysis()
    
    async def _analyze_google_business(self, restaurant_name: str, google_business: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Google Business Profile optimization"""
        try:
            has_profile = google_business.get('verified', False)
            reviews_count = google_business.get('reviews_count', 0)
            avg_rating = google_business.get('avg_rating', 0)
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a local SEO expert for restaurants. Analyze Google Business Profile optimization and provide recommendations.
                    
                    Consider:
                    - Profile completeness
                    - Review quantity and quality
                    - Photo quality and quantity
                    - Business information accuracy
                    - Response to reviews
                    - Local SEO optimization
                    
                    Format response as:
                    SCORE: [0-100]
                    GRADE: [A-F]
                    ISSUES: [list of issues]
                    RECOMMENDATIONS: [list of recommendations]
                    PRIORITY: [HIGH/MEDIUM/LOW]"""
                },
                {
                    "role": "user",
                    "content": f"Analyze Google Business Profile for {restaurant_name}. Verified: {has_profile}, Reviews: {reviews_count}, Rating: {avg_rating}/5. Provide assessment."
                }
            ]
            
            response = await self.openai_service._make_openai_request(messages, max_tokens=400)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Google Business analysis failed: {str(e)}")
            return self._get_fallback_google_analysis()
    
    async def _analyze_menu_optimization(self, restaurant_name: str, menu_items: List[Dict]) -> Dict[str, Any]:
        """Analyze menu optimization for digital marketing"""
        try:
            menu_count = len(menu_items)
            has_descriptions = any(item.get('description') for item in menu_items)
            has_photos = any(item.get('photo') for item in menu_items)
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a restaurant menu optimization expert. Analyze menu digital readiness and marketing potential.
                    
                    Consider:
                    - Item descriptions quality
                    - Photo availability and quality
                    - Pricing strategy
                    - Menu organization
                    - Promotional opportunities
                    - Dietary information
                    
                    Format response as:
                    SCORE: [0-100]
                    GRADE: [A-F]
                    ISSUES: [list of issues]
                    RECOMMENDATIONS: [list of recommendations]
                    PRIORITY: [HIGH/MEDIUM/LOW]"""
                },
                {
                    "role": "user",
                    "content": f"Analyze menu optimization for {restaurant_name}. Items: {menu_count}, Has descriptions: {has_descriptions}, Has photos: {has_photos}. Provide assessment."
                }
            ]
            
            response = await self.openai_service._make_openai_request(messages, max_tokens=400)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Menu analysis failed: {str(e)}")
            return self._get_fallback_menu_analysis()
    
    async def _analyze_marketing_strategy(self, restaurant_name: str, current_marketing: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current marketing strategy effectiveness"""
        try:
            active_campaigns = current_marketing.get('active_campaigns', [])
            marketing_budget = current_marketing.get('monthly_budget', 0)
            target_audience = current_marketing.get('target_audience', 'general')
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a restaurant marketing strategist. Analyze current marketing approach and provide strategic recommendations.
                    
                    Consider:
                    - Campaign diversity and effectiveness
                    - Budget allocation
                    - Target audience definition
                    - Marketing channel mix
                    - ROI tracking
                    - Seasonal strategies
                    
                    Format response as:
                    SCORE: [0-100]
                    GRADE: [A-F]
                    ISSUES: [list of issues]
                    RECOMMENDATIONS: [list of recommendations]
                    PRIORITY: [HIGH/MEDIUM/LOW]"""
                },
                {
                    "role": "user",
                    "content": f"Analyze marketing strategy for {restaurant_name}. Active campaigns: {len(active_campaigns)}, Budget: ${marketing_budget}/month, Target: {target_audience}. Provide assessment."
                }
            ]
            
            response = await self.openai_service._make_openai_request(messages, max_tokens=400)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Marketing analysis failed: {str(e)}")
            return self._get_fallback_marketing_analysis()
    
    async def _calculate_overall_grade(self, component_scores: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate overall digital presence grade"""
        try:
            # Weight different components
            weights = {
                'website': 0.25,
                'social': 0.20,
                'google': 0.25,
                'menu': 0.15,
                'marketing': 0.15
            }
            
            total_score = 0
            for component, weight in weights.items():
                score = component_scores.get(component, {}).get('score', 0)
                total_score += score * weight
            
            # Convert to letter grade
            if total_score >= 90:
                letter_grade = 'A'
                status = 'Excellent'
            elif total_score >= 80:
                letter_grade = 'B'
                status = 'Good'
            elif total_score >= 70:
                letter_grade = 'C'
                status = 'Average'
            elif total_score >= 60:
                letter_grade = 'D'
                status = 'Below Average'
            else:
                letter_grade = 'F'
                status = 'Needs Improvement'
            
            return {
                "score": round(total_score, 1),
                "letter_grade": letter_grade,
                "status": status,
                "improvement_potential": round(100 - total_score, 1)
            }
            
        except Exception as e:
            logger.error(f"Grade calculation failed: {str(e)}")
            return {
                "score": 65.0,
                "letter_grade": "D",
                "status": "Needs Assessment",
                "improvement_potential": 35.0
            }
    
    async def _generate_action_plan(self, overall_grade: Dict, component_scores: Dict) -> Dict[str, Any]:
        """Generate prioritized action plan"""
        try:
            # Collect all high-priority recommendations
            high_priority = []
            medium_priority = []
            low_priority = []
            
            for component, analysis in component_scores.items():
                priority = analysis.get('priority', 'MEDIUM')
                recommendations = analysis.get('recommendations', [])
                
                for rec in recommendations:
                    item = {
                        "action": rec,
                        "component": component,
                        "estimated_impact": self._estimate_impact(component, rec),
                        "effort_level": self._estimate_effort(rec)
                    }
                    
                    if priority == 'HIGH':
                        high_priority.append(item)
                    elif priority == 'MEDIUM':
                        medium_priority.append(item)
                    else:
                        low_priority.append(item)
            
            return {
                "immediate_actions": high_priority[:3],  # Top 3 high priority
                "short_term_goals": medium_priority[:5],  # Top 5 medium priority
                "long_term_improvements": low_priority[:3],  # Top 3 low priority
                "estimated_timeline": "2-8 weeks for immediate actions",
                "success_metrics": [
                    "Increase in online visibility",
                    "Higher customer engagement",
                    "Improved review ratings",
                    "More online orders/reservations"
                ]
            }
            
        except Exception as e:
            logger.error(f"Action plan generation failed: {str(e)}")
            return self._get_fallback_action_plan()
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        try:
            lines = response.split('\n')
            result = {
                "score": 70,
                "grade": "C",
                "issues": [],
                "recommendations": [],
                "priority": "MEDIUM"
            }
            
            for line in lines:
                if line.startswith("SCORE:"):
                    try:
                        result["score"] = int(line.replace("SCORE:", "").strip())
                    except:
                        pass
                elif line.startswith("GRADE:"):
                    result["grade"] = line.replace("GRADE:", "").strip()
                elif line.startswith("ISSUES:"):
                    issues_text = line.replace("ISSUES:", "").strip()
                    result["issues"] = [issue.strip() for issue in issues_text.split(',') if issue.strip()]
                elif line.startswith("RECOMMENDATIONS:"):
                    rec_text = line.replace("RECOMMENDATIONS:", "").strip()
                    result["recommendations"] = [rec.strip() for rec in rec_text.split(',') if rec.strip()]
                elif line.startswith("PRIORITY:"):
                    result["priority"] = line.replace("PRIORITY:", "").strip()
            
            return result
            
        except Exception as e:
            logger.error(f"Response parsing failed: {str(e)}")
            return {
                "score": 65,
                "grade": "D",
                "issues": ["Analysis parsing error"],
                "recommendations": ["Review digital presence manually"],
                "priority": "MEDIUM"
            }
    
    def _calculate_revenue_impact(self, overall_grade: Dict) -> Dict[str, Any]:
        """Calculate potential revenue impact of improvements"""
        current_score = overall_grade.get('score', 65)
        improvement_potential = overall_grade.get('improvement_potential', 35)
        
        # Estimate revenue impact based on digital presence improvements
        monthly_impact_low = improvement_potential * 25  # $25 per point improvement (conservative)
        monthly_impact_high = improvement_potential * 75  # $75 per point improvement (optimistic)
        
        return {
            "monthly_revenue_increase": {
                "low_estimate": f"${monthly_impact_low:,.0f}",
                "high_estimate": f"${monthly_impact_high:,.0f}"
            },
            "annual_potential": {
                "low_estimate": f"${monthly_impact_low * 12:,.0f}",
                "high_estimate": f"${monthly_impact_high * 12:,.0f}"
            },
            "improvement_areas": [
                "Increased online visibility",
                "Better customer engagement",
                "Higher conversion rates",
                "Improved customer retention"
            ]
        }
    
    def _estimate_impact(self, component: str, recommendation: str) -> str:
        """Estimate impact level of a recommendation"""
        high_impact_keywords = ['website', 'google', 'reviews', 'seo', 'online ordering']
        medium_impact_keywords = ['social media', 'content', 'photos', 'menu']
        
        rec_lower = recommendation.lower()
        
        if any(keyword in rec_lower for keyword in high_impact_keywords):
            return "HIGH"
        elif any(keyword in rec_lower for keyword in medium_impact_keywords):
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_effort(self, recommendation: str) -> str:
        """Estimate effort level required for a recommendation"""
        high_effort_keywords = ['create', 'build', 'develop', 'redesign', 'implement']
        low_effort_keywords = ['update', 'add', 'optimize', 'improve', 'respond']
        
        rec_lower = recommendation.lower()
        
        if any(keyword in rec_lower for keyword in high_effort_keywords):
            return "HIGH"
        elif any(keyword in rec_lower for keyword in low_effort_keywords):
            return "LOW"
        else:
            return "MEDIUM"
    
    # Fallback methods for when AI analysis fails
    async def _generate_mock_analysis(self, restaurant_data: Dict) -> Dict[str, Any]:
        """Generate mock analysis when AI fails"""
        return {
            "success": True,
            "overall_grade": {
                "score": 68.5,
                "letter_grade": "D+",
                "status": "Needs Improvement",
                "improvement_potential": 31.5
            },
            "component_scores": {
                "website": self._get_fallback_website_analysis(),
                "social_media": self._get_fallback_social_analysis(),
                "google_business": self._get_fallback_google_analysis(),
                "menu_optimization": self._get_fallback_menu_analysis(),
                "marketing_strategy": self._get_fallback_marketing_analysis()
            },
            "action_plan": self._get_fallback_action_plan(),
            "revenue_impact": {
                "monthly_revenue_increase": {
                    "low_estimate": "$785",
                    "high_estimate": "$2,365"
                },
                "annual_potential": {
                    "low_estimate": "$9,420",
                    "high_estimate": "$28,380"
                }
            },
            "generated_at": datetime.now().isoformat(),
            "note": "Mock analysis - AI service unavailable"
        }
    
    def _get_fallback_website_analysis(self) -> Dict[str, Any]:
        return {
            "score": 65,
            "grade": "D",
            "issues": ["Mobile optimization needed", "Missing online ordering"],
            "recommendations": ["Optimize for mobile", "Add online ordering", "Improve loading speed"],
            "priority": "HIGH"
        }
    
    def _get_fallback_social_analysis(self) -> Dict[str, Any]:
        return {
            "score": 70,
            "grade": "C",
            "issues": ["Inconsistent posting", "Low engagement"],
            "recommendations": ["Post daily content", "Engage with followers", "Use local hashtags"],
            "priority": "MEDIUM"
        }
    
    def _get_fallback_google_analysis(self) -> Dict[str, Any]:
        return {
            "score": 75,
            "grade": "C+",
            "issues": ["Need more reviews", "Missing photos"],
            "recommendations": ["Request customer reviews", "Add high-quality photos", "Update business hours"],
            "priority": "HIGH"
        }
    
    def _get_fallback_menu_analysis(self) -> Dict[str, Any]:
        return {
            "score": 60,
            "grade": "D-",
            "issues": ["Missing item descriptions", "No photos"],
            "recommendations": ["Add appetizing descriptions", "Include food photos", "Highlight specials"],
            "priority": "MEDIUM"
        }
    
    def _get_fallback_marketing_analysis(self) -> Dict[str, Any]:
        return {
            "score": 55,
            "grade": "F",
            "issues": ["No clear strategy", "Limited channels"],
            "recommendations": ["Define target audience", "Create marketing calendar", "Track ROI"],
            "priority": "HIGH"
        }
    
    def _get_fallback_action_plan(self) -> Dict[str, Any]:
        return {
            "immediate_actions": [
                {
                    "action": "Optimize Google Business Profile",
                    "component": "google_business",
                    "estimated_impact": "HIGH",
                    "effort_level": "LOW"
                },
                {
                    "action": "Create mobile-friendly website",
                    "component": "website",
                    "estimated_impact": "HIGH",
                    "effort_level": "HIGH"
                },
                {
                    "action": "Start daily social media posting",
                    "component": "social_media",
                    "estimated_impact": "MEDIUM",
                    "effort_level": "LOW"
                }
            ],
            "short_term_goals": [
                {
                    "action": "Add menu item photos and descriptions",
                    "component": "menu_optimization",
                    "estimated_impact": "MEDIUM",
                    "effort_level": "MEDIUM"
                },
                {
                    "action": "Implement customer review strategy",
                    "component": "google_business",
                    "estimated_impact": "HIGH",
                    "effort_level": "LOW"
                }
            ],
            "long_term_improvements": [
                {
                    "action": "Develop comprehensive marketing strategy",
                    "component": "marketing_strategy",
                    "estimated_impact": "HIGH",
                    "effort_level": "HIGH"
                }
            ],
            "estimated_timeline": "2-8 weeks for immediate actions",
            "success_metrics": [
                "Increase in online visibility",
                "Higher customer engagement",
                "Improved review ratings",
                "More online orders/reservations"
            ]
        }

# Create service instance
ai_grader_service = AIGraderService()