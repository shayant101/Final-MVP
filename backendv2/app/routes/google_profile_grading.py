from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..services.ai_grader_service import ai_grader_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/google-profile", tags=["Google Profile Grading"])

@router.post("/grade")
async def grade_google_profile(
    request_data: Dict[str, Any]
):
    """
    Grade Google Business Profile using classic or OpenAI mode
    """
    try:
        mode = request_data.get("mode", "classic")
        restaurant_name = request_data.get("restaurant_name")
        google_business_url = request_data.get("google_business_url")

        if not restaurant_name or not google_business_url:
            raise HTTPException(status_code=400, detail="Restaurant name and Google Business URL are required")

        if mode == "openai":
            # First scrape the actual Google Business data, then send to OpenAI for analysis
            from ..services.google_business_scraper import google_business_scraper
            from ..services.openai_grader_service import openai_grader_service
            
            # Step 1: Get real data from Google Business Profile
            logger.info(f"🔍 Scraping real data from Google Business Profile: {google_business_url}")
            scraped_data = await google_business_scraper.scrape_basic_info(google_business_url)
            
            if not scraped_data.get("success"):
                logger.warning(f"⚠️ Scraping failed: {scraped_data.get('error', 'Unknown error')}")
                # Fallback to classic mode if scraping fails
                analysis_result = await ai_grader_service._analyze_google_business_with_scraping(restaurant_name, google_business_url)
            else:
                # Step 2: Send scraped real data to OpenAI for intelligent analysis
                real_business_data = scraped_data.get("scraped_data", {})
                scraped_name = real_business_data.get('business_name')
                
                if scraped_name:
                    logger.info(f"✅ Successfully scraped business name from profile: '{scraped_name}'")
                else:
                    logger.warning(f"⚠️ Failed to scrape business name, falling back to provided name: '{restaurant_name}'")
                
                # Create enhanced prompt with real data
                enhanced_prompt = f"""
Analyze this REAL restaurant data that I've already scraped from their Google Business Profile.

Restaurant Name: {real_business_data.get('business_name', restaurant_name)}
Rating: {real_business_data.get('rating', 'Not available')}/5 stars
Review Count: {real_business_data.get('review_count', 'Not available')} reviews
Categories: {', '.join(real_business_data.get('categories', []))}
Website: {real_business_data.get('website', 'Not available')}
Phone: {real_business_data.get('phone', 'Not available')}
Address: {real_business_data.get('address', 'Not available')}

Based on this REAL data (not dummy data), provide a comprehensive digital presence analysis following the format specified in your system prompt. Focus on the actual performance metrics and real data provided above.
"""
                
                restaurant_data = {
                    "name": real_business_data.get('business_name', restaurant_name),
                    "google_business_url": google_business_url,
                    "real_data": real_business_data,
                    "enhanced_prompt": enhanced_prompt
                }
                analysis_result = await openai_grader_service.analyze_digital_presence(restaurant_data)
            
            # Transform the result to match the expected format
            if analysis_result.get("success"):
                openai_data = analysis_result.get("data", {})
                
                # Transform OpenAI result to match expected frontend format
                def extract_grade_info(openai_data):
                    # Try to find overall grade from multiple possible locations
                    overall_grade = openai_data.get("overall_grade", {})
                    if isinstance(overall_grade, dict) and overall_grade.get("grade"):
                        grade = overall_grade.get("grade", "C")
                    else:
                        # If no overall grade, calculate from individual grades
                        grades_section = openai_data.get("Grades", openai_data.get("grades", {}))
                        if grades_section:
                            # Take the first grade as representative, or calculate average
                            first_grade = list(grades_section.values())[0]
                            if isinstance(first_grade, str):
                                grade = first_grade
                            else:
                                grade = "C"  # Default fallback
                        else:
                            grade = "C"  # Default fallback
                    
                    # Convert letter grade to numeric score
                    grade_letter = grade.replace("+", "").replace("-", "")[0] if grade else "C"
                    score_map = {"A": 95, "B": 85, "C": 75, "D": 65, "F": 55}
                    score = score_map.get(grade_letter, 75)
                    
                    # Add modifiers for + and -
                    if "+" in grade:
                        score += 3
                    elif "-" in grade:
                        score -= 3
                        
                    return min(max(score, 0), 100), grade
                
                score, grade = extract_grade_info(openai_data)
                
                # Handle different possible response structures from OpenAI
                # First try the expected structure, then fall back to variations
                
                # Extract issues from grades section (handle actual OpenAI structure)
                issues = []
                recommendations = []
                grades_section = openai_data.get("grades", openai_data.get("Grades", {}))
                
                for category, grade_value in grades_section.items():
                    # OpenAI returns grades as simple strings like "C" or "B+"
                    if isinstance(grade_value, str):
                        # Consider C, D, F grades as issues
                        if grade_value[0] in ["C", "D", "F"]:
                            issues.append(f"{category}: Grade {grade_value} - needs improvement")
                    elif isinstance(grade_value, dict):
                        # Handle if it's the expected object structure
                        notes = grade_value.get("notes", grade_value.get("Notes", ""))
                        grade = grade_value.get("grade", grade_value.get("Grade", ""))
                        if notes and any(word in notes.lower() for word in ["needs", "missing", "low", "poor", "lacks"]):
                            issues.append(f"{category.replace('_', ' ').title()}: {notes}")
                        elif grade and grade[0] in ["C", "D", "F"]:
                            issues.append(f"{category}: Grade {grade} - needs improvement")
                
                # Extract recommendations - handle the actual structure from OpenAI
                recommendations_section = openai_data.get("Recommendations", openai_data.get("recommendations", {}))
                
                if isinstance(recommendations_section, dict):
                    # Handle structure: {"Quick Wins": [...], "Longer-Term Plays": [...]}
                    quick_wins = recommendations_section.get("Quick Wins", recommendations_section.get("quick_wins", []))
                    longer_term = recommendations_section.get("Longer-Term Plays", recommendations_section.get("longer_term_plays", []))
                    
                    # Add all quick wins
                    for item in quick_wins:
                        if isinstance(item, str) and item.strip():
                            recommendations.append(f"Quick Win: {item}")
                        elif isinstance(item, dict):
                            rec = item.get("recommendation", str(item))
                            if rec:
                                recommendations.append(f"Quick Win: {rec}")
                    
                    # Add all longer term recommendations
                    for item in longer_term:
                        if isinstance(item, str) and item.strip():
                            recommendations.append(f"Long-term: {item}")
                        elif isinstance(item, dict):
                            rec = item.get("recommendation", str(item))
                            if rec:
                                recommendations.append(f"Long-term: {rec}")
                
                elif isinstance(recommendations_section, list):
                    # Handle if recommendations is just a flat list
                    for item in recommendations_section:
                        if isinstance(item, str) and item.strip():
                            recommendations.append(item)
                        elif isinstance(item, dict):
                            rec = item.get("recommendation", str(item))
                            if rec:
                                recommendations.append(rec)
                
                # Extract strengths from snapshot or grades (try both cases)
                strengths = []
                snapshot = openai_data.get("snapshot", openai_data.get("Snapshot", {}))
                if snapshot:
                    for key, value in snapshot.items():
                        if value and value != "null" and value != "N/A":
                            if isinstance(value, str) and len(value) > 0:
                                strengths.append(f"Has {key.replace('_', ' ').lower()}")
                
                # If no strengths found from snapshot, try to extract from grades
                if not strengths:
                    for category, grade_info in grades_section.items():
                        if isinstance(grade_info, dict):
                            grade = grade_info.get("grade", grade_info.get("Grade", ""))
                            if grade and grade[0] in ["A", "B"]:
                                strengths.append(f"Good {category.replace('_', ' ').lower()}")
                
                logger.info(f"Extracted from OpenAI: {len(issues)} issues, {len(recommendations)} recommendations, {len(strengths)} strengths")
                
                analysis_result = {
                    "overall_score": score,
                    "grade": grade,
                    "priority": "HIGH" if grade[0] in ["D", "F"] else ("MEDIUM" if grade[0] == "C" else "LOW"),
                    "issues": [issue for issue in issues if issue],
                    "recommendations": [rec for rec in recommendations if rec],
                    "strengths": strengths[:3],  # Limit to top 3 strengths
                    "analysis_method": "openai_enhanced",
                    "grader_version": "2.0-openai",
                    "openai_analysis": openai_data  # Include full OpenAI response
                }
            else:
                # Fallback to classic mode if OpenAI fails
                analysis_result = await ai_grader_service._analyze_google_business_with_scraping(restaurant_name, google_business_url)
        else:
            analysis_result = await ai_grader_service._analyze_google_business_with_scraping(restaurant_name, google_business_url)

        return analysis_result

    except Exception as e:
        logger.error(f"Google Profile grading error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Grading failed: {str(e)}")