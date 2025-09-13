"""
Google Profile Grader Service
Standalone service for evaluating Google Business Profile quality and scoring
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from .google_business_scraper import google_business_scraper
from .screenshot_analyzer import screenshot_analyzer

logger = logging.getLogger(__name__)

class GoogleProfileGrader:
    """
    Dedicated service for grading Google Business Profiles
    
    Scoring breakdown:
    - Business Name Verification: 25 points (30% weight)
    - Reviews & Ratings: 40 points (25% weight) 
    - Business Categories: 20 points (20% weight)
    - Profile Accessibility: 15 points (15% weight)
    - Verification Status: 20 points (10% weight)
    Total: 100 points
    """
    
    def __init__(self):
        self.valid_google_patterns = [
            'maps.google.com',
            'google.com/maps', 
            'goo.gl/maps',
            'maps.app.goo.gl',  # Google Maps app URLs
            'business.google.com',
            'g.co/kgs',
            'g.co',
            'share.google'  # Google share URLs
        ]
    
    async def grade_google_profile(self, restaurant_name: str, google_business_url: str) -> Dict[str, Any]:
        """
        Main method to grade a Google Business Profile
        
        Args:
            restaurant_name: Name of the restaurant for verification
            google_business_url: URL to the Google Business Profile
            
        Returns:
            Dictionary containing score, grade, issues, recommendations, and detailed analysis
        """
        try:
            logger.info(f"🎯 Starting Google Profile grading for: {restaurant_name}")
            
            # Validate input
            if not google_business_url:
                return self._generate_no_url_result()
            
            # Check URL format
            if not self._is_valid_google_url(google_business_url):
                return self._generate_invalid_url_result(google_business_url)
            
            # Attempt to scrape profile data
            scraped_data = await google_business_scraper.scrape_basic_info(google_business_url)
            
            # Check if we got good data from scraping
            has_good_scraping_data = (
                scraped_data.get("success") and
                scraped_data.get("business_name") and
                not scraped_data.get("business_name", "").startswith("=") and  # Avoid JavaScript code
                scraped_data.get("rating") is not None and
                scraped_data.get("review_count", 0) > 10  # Reasonable review count
            )
            
            # If scraping didn't provide good data, try screenshot analysis
            if not has_good_scraping_data:
                logger.info(f"🔄 Scraping data insufficient, trying screenshot analysis...")
                screenshot_data = await screenshot_analyzer.analyze_google_profile_screenshot(
                    google_business_url, 
                    restaurant_name
                )
                
                if screenshot_data.get("success"):
                    logger.info(f"✅ Screenshot analysis successful, using vision data")
                    # Use screenshot data
                    return await self._calculate_detailed_score_from_screenshot(
                        restaurant_name, google_business_url, screenshot_data
                    )
                else:
                    logger.warning(f"⚠️ Both scraping and screenshot analysis failed")
                    if scraped_data.get("success"):
                        # Fall back to scraping data even if limited
                        return await self._calculate_detailed_score(restaurant_name, google_business_url, scraped_data)
                    else:
                        return self._generate_scraping_failed_result(google_business_url, "Both scraping and screenshot analysis failed")
            
            # Calculate detailed score using scraping data
            return await self._calculate_detailed_score(restaurant_name, google_business_url, scraped_data)
            
        except Exception as e:
            logger.error(f"❌ Google Profile grading failed: {str(e)}")
            return self._generate_error_result(str(e))
    
    def _is_valid_google_url(self, url: str) -> bool:
        """Check if URL matches Google Business Profile patterns"""
        return any(pattern in url.lower() for pattern in self.valid_google_patterns)
    
    async def _calculate_detailed_score(self, restaurant_name: str, url: str, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed score based on scraped data"""
        
        score_breakdown = {
            "business_name": {"score": 0, "max": 25, "weight": "30%"},
            "reviews_ratings": {"score": 0, "max": 40, "weight": "25%"}, 
            "categories": {"score": 0, "max": 20, "weight": "20%"},
            "accessibility": {"score": 0, "max": 15, "weight": "15%"},
            "verification": {"score": 0, "max": 20, "weight": "10%"}
        }
        
        issues = []
        recommendations = []
        strengths = []
        
        # 1. Business Name Verification (25 points - 30% weight)
        name_score = self._score_business_name(restaurant_name, scraped_data, issues, recommendations, strengths)
        score_breakdown["business_name"]["score"] = name_score
        
        # 2. Reviews & Ratings (40 points - 25% weight)
        review_score = self._score_reviews_ratings(scraped_data, issues, recommendations, strengths)
        score_breakdown["reviews_ratings"]["score"] = review_score
        
        # 3. Business Categories (20 points - 20% weight)
        category_score = self._score_categories(scraped_data, issues, recommendations, strengths)
        score_breakdown["categories"]["score"] = category_score
        
        # 4. Profile Accessibility (15 points - 15% weight)
        accessibility_score = self._score_accessibility(scraped_data, issues, recommendations, strengths)
        score_breakdown["accessibility"]["score"] = accessibility_score
        
        # 5. Verification Status (20 points - 10% weight)
        verification_score = self._score_verification(scraped_data, issues, recommendations, strengths)
        score_breakdown["verification"]["score"] = verification_score
        
        # Calculate total score
        total_score = sum(breakdown["score"] for breakdown in score_breakdown.values())
        
        # Generate grade and priority
        grade, priority = self._calculate_grade_and_priority(total_score)
        
        # Add universal recommendations
        self._add_universal_recommendations(recommendations)
        
        return {
            "overall_score": min(total_score, 100),
            "grade": grade,
            "priority": priority,
            "score_breakdown": score_breakdown,
            "issues": issues,
            "recommendations": recommendations[:8],  # Limit to top 8
            "strengths": strengths,
            "scraped_data": {
                "business_name": scraped_data.get("business_name"),
                "rating": scraped_data.get("rating"),
                "review_count": scraped_data.get("review_count"),
                "categories": scraped_data.get("categories", []),
                "profile_url": url
            },
            "analysis_method": "real_scraping_data",
            "grader_version": "1.0"
        }
    
    def _score_business_name(self, restaurant_name: str, scraped_data: Dict[str, Any], 
                           issues: List[str], recommendations: List[str], strengths: List[str]) -> int:
        """Score business name verification (25 points max)"""
        score = 0
        scraped_name = scraped_data.get("business_name")
        
        if scraped_name:
            score += 15  # Base points for having a name
            strengths.append(f"Business name found: '{scraped_name}'")
            
            # Check name consistency
            if self._names_match(restaurant_name, scraped_name):
                score += 10  # Full consistency bonus
                strengths.append("Business name matches across platforms")
            elif self._names_similar(restaurant_name, scraped_name):
                score += 5   # Partial similarity bonus
                issues.append(f"Name variation detected: Profile shows '{scraped_name}' vs provided '{restaurant_name}'")
                recommendations.append("Ensure consistent business name across all platforms")
            else:
                issues.append(f"Business name mismatch: Profile shows '{scraped_name}' but you provided '{restaurant_name}'")
                recommendations.append("Update business name for consistency")
        else:
            issues.append("Business name not clearly displayed on profile")
            recommendations.append("Add clear, prominent business name to Google Business Profile")
        
        return score
    
    def _score_reviews_ratings(self, scraped_data: Dict[str, Any], 
                             issues: List[str], recommendations: List[str], strengths: List[str]) -> int:
        """Score reviews and ratings (40 points max)"""
        score = 0
        rating = scraped_data.get("rating")
        review_count = scraped_data.get("review_count")
        
        # Rating scoring (25 points)
        if rating is not None:
            if rating >= 4.5:
                score += 25
                strengths.append(f"Excellent rating: {rating}/5 stars")
            elif rating >= 4.0:
                score += 20
                strengths.append(f"Good rating: {rating}/5 stars")
            elif rating >= 3.5:
                score += 15
                strengths.append(f"Average rating: {rating}/5 stars")
            elif rating >= 3.0:
                score += 10
                issues.append(f"Below average rating: {rating}/5 stars")
                recommendations.append("Focus on improving customer satisfaction and service quality")
            else:
                score += 5
                issues.append(f"Low rating: {rating}/5 stars - needs immediate attention")
                recommendations.append("Implement customer service improvement plan")
        else:
            issues.append("No customer ratings found")
            recommendations.append("Encourage customers to leave reviews")
        
        # Review count scoring (15 points)
        if review_count is not None:
            if review_count >= 100:
                score += 15
                strengths.append(f"Strong review base: {review_count} reviews")
            elif review_count >= 50:
                score += 12
                strengths.append(f"Good review count: {review_count} reviews")
            elif review_count >= 20:
                score += 8
                strengths.append(f"Moderate review count: {review_count} reviews")
            elif review_count >= 5:
                score += 5
                issues.append(f"Low review count: {review_count} reviews")
                recommendations.append("Actively request customer reviews")
            else:
                score += 2
                issues.append(f"Very low review count: {review_count} reviews")
                recommendations.append("Implement systematic review collection strategy")
        else:
            issues.append("Review count not available")
            recommendations.append("Enable review display on your profile")
        
        return score
    
    def _score_categories(self, scraped_data: Dict[str, Any], 
                        issues: List[str], recommendations: List[str], strengths: List[str]) -> int:
        """Score business categories (20 points max)"""
        score = 0
        categories = scraped_data.get("categories", [])
        
        if categories:
            score += 15  # Base points for having categories
            strengths.append(f"Business categories found: {', '.join(categories[:3])}")
            
            # Check for food-related categories
            category_text = " ".join(categories).lower()
            food_keywords = ["restaurant", "food", "dining", "cafe", "bar", "bistro", "eatery", "kitchen"]
            
            if any(keyword in category_text for keyword in food_keywords):
                score += 5  # Bonus for relevant categories
                strengths.append("Categories appropriately identify business as food service")
            else:
                recommendations.append("Add food service related categories to improve discoverability")
        else:
            issues.append("Business categories not found or not visible")
            recommendations.append("Add appropriate business categories (Restaurant, Food Service, etc.)")
        
        return score
    
    def _score_accessibility(self, scraped_data: Dict[str, Any], 
                           issues: List[str], recommendations: List[str], strengths: List[str]) -> int:
        """Score profile accessibility (15 points max)"""
        score = 0
        
        if scraped_data.get("success"):
            score += 15  # Full points for accessible profile
            strengths.append("Google Business Profile is publicly accessible")
        else:
            issues.append("Profile may not be publicly accessible or has visibility issues")
            recommendations.append("Ensure your Google Business Profile is public and properly configured")
        
        return score
    
    def _score_verification(self, scraped_data: Dict[str, Any], 
                          issues: List[str], recommendations: List[str], strengths: List[str]) -> int:
        """Score verification status (20 points max)"""
        score = 10  # Base points for having a profile
        
        # Note: Verification status is hard to determine from scraping alone
        # This is an estimate based on profile completeness
        business_name = scraped_data.get("business_name")
        rating = scraped_data.get("rating")
        categories = scraped_data.get("categories", [])
        
        completeness_indicators = [business_name, rating, categories]
        complete_fields = sum(1 for field in completeness_indicators if field)
        
        if complete_fields >= 3:
            score += 10  # Likely verified based on completeness
            strengths.append("Profile appears complete and likely verified")
        else:
            issues.append("Profile may not be verified or is incomplete")
            recommendations.append("Complete profile verification process with Google")
        
        return score
    
    def _names_match(self, name1: str, name2: str) -> bool:
        """Check if two business names match closely"""
        if not name1 or not name2:
            return False
        
        # Normalize names for comparison
        normalized1 = self._normalize_name(name1)
        normalized2 = self._normalize_name(name2)
        
        return normalized1 == normalized2
    
    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two business names are similar"""
        if not name1 or not name2:
            return False
        
        normalized1 = self._normalize_name(name1)
        normalized2 = self._normalize_name(name2)
        
        # Check if one name contains the other
        return normalized1 in normalized2 or normalized2 in normalized1
    
    def _normalize_name(self, name: str) -> str:
        """Normalize business name for comparison"""
        import re
        # Remove common business suffixes and punctuation
        normalized = re.sub(r'\b(restaurant|cafe|bar|bistro|llc|inc|ltd)\b', '', name.lower())
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        return normalized.strip()
    
    def _calculate_grade_and_priority(self, score: int) -> tuple:
        """Convert score to letter grade and priority level"""
        if score >= 90:
            return 'A', 'LOW'
        elif score >= 80:
            return 'B', 'LOW'
        elif score >= 70:
            return 'C', 'MEDIUM'
        elif score >= 60:
            return 'D', 'HIGH'
        else:
            return 'F', 'HIGH'
    
    def _add_universal_recommendations(self, recommendations: List[str]):
        """Add universal recommendations applicable to all profiles"""
        universal_recs = [
            "Keep business information updated",
            "Respond to customer reviews promptly",
            "Upload high-quality photos regularly",
            "Post updates about specials and events",
            "Monitor and maintain profile accuracy"
        ]
        
        # Add universal recommendations that aren't already included
        for rec in universal_recs:
            if rec not in recommendations and len(recommendations) < 8:
                recommendations.append(rec)
    
    async def _calculate_detailed_score_from_screenshot(self, restaurant_name: str, url: str, screenshot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed score based on screenshot analysis data"""
        
        score_breakdown = {
            "business_name": {"score": 0, "max": 25, "weight": "30%"},
            "reviews_ratings": {"score": 0, "max": 40, "weight": "25%"}, 
            "categories": {"score": 0, "max": 20, "weight": "20%"},
            "accessibility": {"score": 0, "max": 15, "weight": "15%"},
            "verification": {"score": 0, "max": 20, "weight": "10%"}
        }
        
        issues = []
        recommendations = []
        strengths = []
        
        # 1. Business Name Verification (25 points - 30% weight)
        name_score = self._score_business_name_from_screenshot(restaurant_name, screenshot_data, issues, recommendations, strengths)
        score_breakdown["business_name"]["score"] = name_score
        
        # 2. Reviews & Ratings (40 points - 25% weight)
        review_score = self._score_reviews_ratings_from_screenshot(screenshot_data, issues, recommendations, strengths)
        score_breakdown["reviews_ratings"]["score"] = review_score
        
        # 3. Business Categories (20 points - 20% weight)
        category_score = self._score_categories_from_screenshot(screenshot_data, issues, recommendations, strengths)
        score_breakdown["categories"]["score"] = category_score
        
        # 4. Profile Accessibility (15 points - 15% weight)
        accessibility_score = 15  # If we got screenshot data, profile is accessible
        score_breakdown["accessibility"]["score"] = accessibility_score
        strengths.append("Google Business Profile successfully captured via screenshot")
        
        # 5. Verification Status (20 points - 10% weight)
        verification_score = self._score_verification_from_screenshot(screenshot_data, issues, recommendations, strengths)
        score_breakdown["verification"]["score"] = verification_score
        
        # Calculate total score
        total_score = sum(breakdown["score"] for breakdown in score_breakdown.values())
        
        # Generate grade and priority
        grade, priority = self._calculate_grade_and_priority(total_score)
        
        # Add universal recommendations
        self._add_universal_recommendations(recommendations)
        
        return {
            "overall_score": min(total_score, 100),
            "grade": grade,
            "priority": priority,
            "score_breakdown": score_breakdown,
            "issues": issues,
            "recommendations": recommendations[:8],  # Limit to top 8
            "strengths": strengths,
            "scraped_data": {
                "business_name": screenshot_data.get("business_name"),
                "rating": screenshot_data.get("rating"),
                "review_count": screenshot_data.get("review_count"),
                "categories": screenshot_data.get("categories", []),
                "profile_url": url,
                "address": screenshot_data.get("address"),
                "phone": screenshot_data.get("phone"),
                "website": screenshot_data.get("website"),
                "verified": screenshot_data.get("verified"),
                "claimed": screenshot_data.get("claimed")
            },
            "analysis_method": "screenshot_vision_analysis",
            "grader_version": "1.0"
        }
    
    def _score_business_name_from_screenshot(self, restaurant_name: str, screenshot_data: Dict[str, Any], 
                                           issues: List[str], recommendations: List[str], strengths: List[str]) -> int:
        """Score business name from screenshot data"""
        score = 0
        business_name = screenshot_data.get("business_name")
        
        if business_name:
            score += 15  # Base points for having a name
            strengths.append(f"Business name clearly visible: '{business_name}'")
            
            # Check name consistency
            if self._names_match(restaurant_name, business_name):
                score += 10  # Full consistency bonus
                strengths.append("Business name matches provided information")
            elif self._names_similar(restaurant_name, business_name):
                score += 5   # Partial similarity bonus
                issues.append(f"Name variation detected: Profile shows '{business_name}' vs provided '{restaurant_name}'")
                recommendations.append("Ensure consistent business name across all platforms")
            else:
                issues.append(f"Business name mismatch: Profile shows '{business_name}' but you provided '{restaurant_name}'")
                recommendations.append("Update business name for consistency")
        else:
            issues.append("Business name not clearly visible in profile")
            recommendations.append("Ensure business name is prominently displayed")
        
        return score
    
    def _score_reviews_ratings_from_screenshot(self, screenshot_data: Dict[str, Any], 
                                             issues: List[str], recommendations: List[str], strengths: List[str]) -> int:
        """Score reviews and ratings from screenshot data"""
        score = 0
        rating = screenshot_data.get("rating")
        review_count = screenshot_data.get("review_count")
        
        # Rating scoring (25 points)
        if rating is not None:
            if rating >= 4.5:
                score += 25
                strengths.append(f"Excellent rating: {rating}/5 stars")
            elif rating >= 4.0:
                score += 20
                strengths.append(f"Good rating: {rating}/5 stars")
            elif rating >= 3.5:
                score += 15
                strengths.append(f"Average rating: {rating}/5 stars")
            elif rating >= 3.0:
                score += 10
                issues.append(f"Below average rating: {rating}/5 stars")
                recommendations.append("Focus on improving customer satisfaction")
            else:
                score += 5
                issues.append(f"Low rating: {rating}/5 stars - needs immediate attention")
                recommendations.append("Implement customer service improvement plan")
        else:
            issues.append("No customer rating visible")
            recommendations.append("Encourage customers to leave reviews")
        
        # Review count scoring (15 points)
        if review_count is not None:
            if review_count >= 1000:
                score += 15
                strengths.append(f"Strong review base: {review_count:,} reviews")
            elif review_count >= 500:
                score += 12
                strengths.append(f"Good review count: {review_count} reviews")
            elif review_count >= 100:
                score += 10
                strengths.append(f"Solid review count: {review_count} reviews")
            elif review_count >= 50:
                score += 8
                strengths.append(f"Moderate review count: {review_count} reviews")
            elif review_count >= 20:
                score += 5
                issues.append(f"Could use more reviews: {review_count} reviews")
                recommendations.append("Actively request customer reviews")
            else:
                score += 2
                issues.append(f"Low review count: {review_count} reviews")
                recommendations.append("Implement systematic review collection strategy")
        else:
            issues.append("Review count not visible")
            recommendations.append("Enable review display on your profile")
        
        return score
    
    def _score_categories_from_screenshot(self, screenshot_data: Dict[str, Any], 
                                        issues: List[str], recommendations: List[str], strengths: List[str]) -> int:
        """Score business categories from screenshot data"""
        score = 0
        categories = screenshot_data.get("categories", [])
        
        if categories:
            score += 15  # Base points for having categories
            strengths.append(f"Business categories visible: {', '.join(categories[:3])}")
            
            # Check for food-related categories
            category_text = " ".join(categories).lower()
            food_keywords = ["restaurant", "food", "dining", "cafe", "bar", "bistro", "eatery", "kitchen"]
            
            if any(keyword in category_text for keyword in food_keywords):
                score += 5  # Bonus for relevant categories
                strengths.append("Categories appropriately identify business as food service")
            else:
                recommendations.append("Add food service related categories")
        else:
            issues.append("Business categories not visible")
            recommendations.append("Add appropriate business categories")
        
        return score
    
    def _score_verification_from_screenshot(self, screenshot_data: Dict[str, Any], 
                                          issues: List[str], recommendations: List[str], strengths: List[str]) -> int:
        """Score verification status from screenshot data"""
        score = 10  # Base points for having a profile
        
        verified = screenshot_data.get("verified")
        claimed = screenshot_data.get("claimed")
        
        if verified:
            score += 10
            strengths.append("Business profile appears verified")
        elif claimed:
            score += 5
            strengths.append("Business profile is claimed")
        else:
            issues.append("Business profile verification status unclear")
            recommendations.append("Complete profile verification process with Google")
        
        return score
    
    def _generate_no_url_result(self) -> Dict[str, Any]:
        """Generate result when no URL is provided"""
        return {
            "overall_score": 0,
            "grade": "F",
            "priority": "HIGH",
            "issues": ["No Google Business Profile URL provided"],
            "recommendations": [
                "Create Google Business Profile",
                "Verify business ownership", 
                "Add complete business information",
                "Upload high-quality photos"
            ],
            "analysis_method": "no_url_provided",
            "grader_version": "1.0"
        }
    
    def _generate_invalid_url_result(self, url: str) -> Dict[str, Any]:
        """Generate result when URL format is invalid"""
        return {
            "overall_score": 20,
            "grade": "F",
            "priority": "HIGH",
            "issues": [f"Invalid Google Business Profile URL format: {url}"],
            "recommendations": [
                "Verify Google Business Profile URL is correct",
                "Ensure URL points to Google Maps or Business profile",
                "Create new Google Business Profile if needed"
            ],
            "analysis_method": "invalid_url_format",
            "grader_version": "1.0"
        }
    
    def _generate_scraping_failed_result(self, url: str, error: str) -> Dict[str, Any]:
        """Generate result when scraping fails"""
        return {
            "overall_score": 40,
            "grade": "D", 
            "priority": "HIGH",
            "issues": [
                "Could not access Google Business Profile",
                f"Technical error: {error}"
            ],
            "recommendations": [
                "Check if Google Business Profile is public",
                "Verify profile URL is correct",
                "Ensure profile is not restricted or private"
            ],
            "analysis_method": "scraping_failed",
            "grader_version": "1.0"
        }
    
    def _generate_error_result(self, error: str) -> Dict[str, Any]:
        """Generate result when an unexpected error occurs"""
        return {
            "overall_score": 0,
            "grade": "F",
            "priority": "HIGH", 
            "issues": [f"Analysis failed due to technical error: {error}"],
            "recommendations": [
                "Try again later",
                "Contact support if issue persists"
            ],
            "analysis_method": "error",
            "grader_version": "1.0"
        }

# Create service instance
google_profile_grader = GoogleProfileGrader()