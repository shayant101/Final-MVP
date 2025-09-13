"""
Google Profile Grading API Routes
Dedicated endpoints for Google Business Profile analysis and grading
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional
from ..services.google_profile_grader import google_profile_grader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/google-profile", tags=["Google Profile Grading"])

class GoogleProfileGradeRequest(BaseModel):
    """Request model for Google Profile grading"""
    restaurant_name: str = Field(..., min_length=1, max_length=200, description="Name of the restaurant")
    google_business_url: str = Field(..., min_length=10, max_length=500, description="Google Business Profile URL")
    
    @validator('restaurant_name')
    def validate_restaurant_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Restaurant name cannot be empty')
        return v.strip()
    
    @validator('google_business_url')
    def validate_google_url(cls, v):
        if not v or not v.strip():
            raise ValueError('Google Business URL cannot be empty')
        
        # Basic URL validation
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        
        return v.strip()

class GoogleProfileGradeResponse(BaseModel):
    """Response model for Google Profile grading"""
    overall_score: int = Field(..., ge=0, le=100)
    grade: str = Field(..., pattern="^[A-F]$")
    priority: str = Field(..., pattern="^(LOW|MEDIUM|HIGH)$")
    score_breakdown: Optional[Dict[str, Any]] = None
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    strengths: Optional[list[str]] = Field(default_factory=list)
    scraped_data: Optional[Dict[str, Any]] = None
    analysis_method: str
    grader_version: str

@router.post("/grade", response_model=GoogleProfileGradeResponse)
async def grade_google_profile(request: GoogleProfileGradeRequest) -> GoogleProfileGradeResponse:
    """
    Grade a Google Business Profile
    
    This endpoint analyzes a Google Business Profile and provides:
    - Overall score (0-100)
    - Letter grade (A-F)
    - Priority level (LOW/MEDIUM/HIGH)
    - Detailed score breakdown
    - Specific issues found
    - Actionable recommendations
    - Profile strengths
    """
    try:
        logger.info(f"🎯 Grading Google Profile for: {request.restaurant_name}")
        
        # Call the grading service
        result = await google_profile_grader.grade_google_profile(
            restaurant_name=request.restaurant_name,
            google_business_url=request.google_business_url
        )
        
        logger.info(f"✅ Google Profile grading completed: {result.get('overall_score', 0)}/100 ({result.get('grade', 'F')})")
        
        return GoogleProfileGradeResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Google Profile grading failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google Profile grading failed: {str(e)}"
        )

@router.post("/quick-check", response_model=Dict[str, Any])
async def quick_google_profile_check(request: GoogleProfileGradeRequest) -> Dict[str, Any]:
    """
    Quick check of Google Business Profile status
    
    Returns basic validation without full grading:
    - URL validity
    - Profile accessibility
    - Basic information availability
    """
    try:
        logger.info(f"🔍 Quick checking Google Profile for: {request.restaurant_name}")
        
        # Import the scraper directly for quick check
        from ..services.google_business_scraper import google_business_scraper
        
        # Just scrape basic info without full grading
        scraped_data = await google_business_scraper.scrape_basic_info(request.google_business_url)
        
        quick_result = {
            "profile_accessible": scraped_data.get("success", False),
            "business_name_found": bool(scraped_data.get("business_name")),
            "rating_available": scraped_data.get("rating") is not None,
            "review_count_available": scraped_data.get("review_count") is not None,
            "categories_found": len(scraped_data.get("categories", [])) > 0,
            "scraped_data": {
                "business_name": scraped_data.get("business_name"),
                "rating": scraped_data.get("rating"),
                "review_count": scraped_data.get("review_count"),
                "categories": scraped_data.get("categories", [])
            },
            "error": scraped_data.get("error") if not scraped_data.get("success") else None
        }
        
        logger.info(f"✅ Quick check completed: Profile accessible: {quick_result['profile_accessible']}")
        
        return quick_result
        
    except Exception as e:
        logger.error(f"❌ Quick Google Profile check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick profile check failed: {str(e)}"
        )

@router.get("/test-scraper")
async def test_google_scraper() -> Dict[str, Any]:
    """
    Test endpoint to verify Google Business scraper functionality
    Uses a known Google Business Profile URL for testing
    """
    try:
        logger.info("🧪 Testing Google Business scraper")
        
        # Use a known restaurant for testing
        test_url = "https://www.google.com/maps/place/Joe's+Pizza/@40.7505,-73.9934,17z"
        test_name = "Joe's Pizza"
        
        from ..services.google_business_scraper import google_business_scraper
        
        scraped_data = await google_business_scraper.scrape_basic_info(test_url)
        
        test_result = {
            "scraper_working": scraped_data.get("success", False),
            "test_url": test_url,
            "test_restaurant": test_name,
            "scraped_data": scraped_data,
            "timestamp": "2025-09-11T04:45:00Z"
        }
        
        logger.info(f"✅ Scraper test completed: Working: {test_result['scraper_working']}")
        
        return test_result
        
    except Exception as e:
        logger.error(f"❌ Scraper test failed: {str(e)}")
        return {
            "scraper_working": False,
            "error": str(e),
            "timestamp": "2025-09-11T04:45:00Z"
        }

@router.get("/scoring-criteria")
async def get_scoring_criteria() -> Dict[str, Any]:
    """
    Get detailed information about Google Profile scoring criteria
    Useful for understanding how scores are calculated
    """
    return {
        "scoring_breakdown": {
            "business_name": {
                "max_points": 25,
                "weight": "30%",
                "criteria": [
                    "Business name clearly displayed (15 pts)",
                    "Name consistency with provided info (10 pts)"
                ]
            },
            "reviews_ratings": {
                "max_points": 40,
                "weight": "25%", 
                "criteria": [
                    "Customer rating (0-25 pts based on rating value)",
                    "Review count (0-15 pts based on number of reviews)"
                ]
            },
            "categories": {
                "max_points": 20,
                "weight": "20%",
                "criteria": [
                    "Business categories present (15 pts)",
                    "Food service categories identified (5 pts bonus)"
                ]
            },
            "accessibility": {
                "max_points": 15,
                "weight": "15%",
                "criteria": [
                    "Profile publicly accessible (15 pts)"
                ]
            },
            "verification": {
                "max_points": 20,
                "weight": "10%",
                "criteria": [
                    "Profile appears complete (10 pts)",
                    "Likely verified status (10 pts)"
                ]
            }
        },
        "grade_scale": {
            "A": "90-100 points (Excellent - Low Priority)",
            "B": "80-89 points (Good - Low Priority)",
            "C": "70-79 points (Average - Medium Priority)",
            "D": "60-69 points (Below Average - High Priority)",
            "F": "0-59 points (Needs Improvement - High Priority)"
        },
        "total_possible_points": 120,
        "score_capped_at": 100
    }