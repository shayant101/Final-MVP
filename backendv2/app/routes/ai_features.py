"""
AI Features API Routes
Provides endpoints for all AI-powered restaurant marketing features
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..services.ai_grader_service import ai_grader_service
from ..services.ai_menu_optimizer import ai_menu_optimizer
from ..services.ai_marketing_assistant import ai_marketing_assistant
from ..services.ai_content_engine import ai_content_engine
from ..auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["AI Features"])

# AI Digital Presence Grader Endpoints
@router.post("/digital-presence/analyze")
async def analyze_digital_presence(
    restaurant_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """
    Analyze restaurant's digital presence and provide comprehensive grade and recommendations
    """
    try:
        logger.info(f"Analyzing digital presence for restaurant: {restaurant_data.get('name', 'Unknown')}")
        
        # Add user context to restaurant data
        restaurant_data['user_id'] = current_user.user_id
        restaurant_data['analysis_timestamp'] = datetime.now().isoformat()
        
        # Perform digital presence analysis
        analysis_result = await ai_grader_service.analyze_digital_presence(restaurant_data)
        
        if not analysis_result.get('success'):
            raise HTTPException(status_code=500, detail="Digital presence analysis failed")
        
        return {
            "success": True,
            "message": "Digital presence analysis completed successfully",
            "data": analysis_result
        }
        
    except Exception as e:
        logger.error(f"Digital presence analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/digital-presence/quick-score")
async def get_quick_digital_score(
    website_url: Optional[str] = None,
    has_social_media: bool = False,
    google_verified: bool = False,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get a quick digital presence score based on basic information
    """
    try:
        # Calculate quick score
        score = 0
        recommendations = []
        
        if website_url:
            score += 30
        else:
            recommendations.append("Create a professional website")
        
        if has_social_media:
            score += 25
        else:
            recommendations.append("Establish social media presence")
        
        if google_verified:
            score += 25
        else:
            recommendations.append("Verify Google Business Profile")
        
        # Base score for having basic restaurant info
        score += 20
        
        grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"
        
        return {
            "success": True,
            "quick_score": {
                "score": score,
                "grade": grade,
                "immediate_recommendations": recommendations,
                "next_step": "Run full analysis for detailed insights"
            }
        }
        
    except Exception as e:
        logger.error(f"Quick score calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quick score failed: {str(e)}")

# Smart Menu Optimization Endpoints
@router.post("/menu/analyze")
async def analyze_menu_performance(
    restaurant_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Analyze menu performance and generate optimization recommendations
    """
    try:
        logger.info(f"Analyzing menu for restaurant: {restaurant_data.get('name', 'Unknown')}")
        
        # Add user context
        restaurant_data['user_id'] = current_user.get('user_id')
        restaurant_data['analysis_timestamp'] = datetime.now().isoformat()
        
        # Perform menu analysis
        menu_analysis = await ai_menu_optimizer.analyze_menu_performance(restaurant_data)
        
        if not menu_analysis.get('success'):
            raise HTTPException(status_code=500, detail="Menu analysis failed")
        
        return {
            "success": True,
            "message": "Menu analysis completed successfully",
            "data": menu_analysis
        }
        
    except Exception as e:
        logger.error(f"Menu analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Menu analysis failed: {str(e)}")

@router.post("/menu/generate-promotions")
async def generate_menu_promotions(
    menu_items: List[Dict[str, Any]],
    restaurant_name: str,
    promotion_type: str = "cross_selling",
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate specific promotional campaigns based on menu items
    """
    try:
        logger.info(f"Generating {promotion_type} promotions for {restaurant_name}")
        
        # Create restaurant data for analysis
        restaurant_data = {
            "name": restaurant_name,
            "menu_items": menu_items,
            "user_id": current_user.get('user_id')
        }
        
        # Get menu analysis with promotional focus
        menu_analysis = await ai_menu_optimizer.analyze_menu_performance(restaurant_data)
        
        if menu_analysis.get('success'):
            promotional_strategies = menu_analysis.get('promotional_strategies', {})
            recommended_campaigns = promotional_strategies.get('recommended_campaigns', [])
            
            # Filter campaigns by type if specified
            if promotion_type != "all":
                recommended_campaigns = [
                    campaign for campaign in recommended_campaigns 
                    if campaign.get('type') == promotion_type
                ]
            
            return {
                "success": True,
                "message": f"Generated {len(recommended_campaigns)} promotional campaigns",
                "data": {
                    "campaigns": recommended_campaigns,
                    "implementation_priority": promotional_strategies.get('implementation_priority', []),
                    "expected_outcomes": promotional_strategies.get('expected_outcomes', {})
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate promotions")
        
    except Exception as e:
        logger.error(f"Promotion generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Promotion generation failed: {str(e)}")

# AI Marketing Assistant Endpoints
@router.post("/marketing/recommendations")
async def get_marketing_recommendations(
    restaurant_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Get comprehensive marketing recommendations and strategy
    """
    try:
        logger.info(f"Generating marketing recommendations for: {restaurant_data.get('name', 'Unknown')}")
        
        # Add user context
        restaurant_data['user_id'] = current_user.get('user_id')
        restaurant_data['analysis_timestamp'] = datetime.now().isoformat()
        
        # Get marketing recommendations
        marketing_recommendations = await ai_marketing_assistant.get_marketing_recommendations(restaurant_data)
        
        if not marketing_recommendations.get('success'):
            raise HTTPException(status_code=500, detail="Marketing recommendations failed")
        
        return {
            "success": True,
            "message": "Marketing recommendations generated successfully",
            "data": marketing_recommendations
        }
        
    except Exception as e:
        logger.error(f"Marketing recommendations error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Marketing recommendations failed: {str(e)}")

@router.post("/marketing/campaign-builder")
async def build_marketing_campaign(
    campaign_request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Build a specific marketing campaign based on goals and budget
    """
    try:
        restaurant_name = campaign_request.get('restaurant_name', 'Restaurant')
        business_goals = campaign_request.get('business_goals', [])
        budget = campaign_request.get('budget', 500)
        campaign_type = campaign_request.get('campaign_type', 'general')
        
        logger.info(f"Building {campaign_type} campaign for {restaurant_name} with ${budget} budget")
        
        # Create restaurant data for campaign building
        restaurant_data = {
            "name": restaurant_name,
            "business_goals": business_goals,
            "monthly_budget": budget,
            "campaign_focus": campaign_type,
            "user_id": current_user.get('user_id')
        }
        
        # Get marketing recommendations focused on campaign building
        marketing_analysis = await ai_marketing_assistant.get_marketing_recommendations(restaurant_data)
        
        if marketing_analysis.get('success'):
            campaign_recommendations = marketing_analysis.get('campaign_recommendations', {})
            
            return {
                "success": True,
                "message": "Marketing campaign built successfully",
                "data": {
                    "campaign_details": campaign_recommendations.get('recommended_campaigns', []),
                    "budget_allocation": campaign_recommendations.get('budget_allocation', {}),
                    "implementation_plan": marketing_analysis.get('comprehensive_plan', {}),
                    "roi_projections": marketing_analysis.get('roi_projections', {})
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to build campaign")
        
    except Exception as e:
        logger.error(f"Campaign building error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Campaign building failed: {str(e)}")

# Unified Content Generation Engine Endpoints
@router.post("/content/generate-suite")
async def generate_content_suite(
    content_request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate comprehensive content suite across multiple channels
    """
    try:
        restaurant_data = content_request.get('restaurant_data', {})
        content_types = content_request.get('content_types', ['social_media_campaign'])
        
        logger.info(f"Generating content suite for: {restaurant_data.get('name', 'Unknown')}")
        logger.info(f"Content types requested: {content_types}")
        
        # Add user context
        restaurant_data['user_id'] = current_user.get('user_id')
        restaurant_data['generation_timestamp'] = datetime.now().isoformat()
        
        # Generate comprehensive content suite
        content_suite = await ai_content_engine.generate_comprehensive_content_suite(
            restaurant_data, content_types
        )
        
        if not content_suite.get('success'):
            raise HTTPException(status_code=500, detail="Content generation failed")
        
        return {
            "success": True,
            "message": f"Generated content suite with {len(content_types)} content types",
            "data": content_suite
        }
        
    except Exception as e:
        logger.error(f"Content suite generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.post("/content/social-media")
async def generate_social_media_content(
    social_request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate specific social media content for multiple platforms
    """
    try:
        restaurant_name = social_request.get('restaurant_name', 'Restaurant')
        platforms = social_request.get('platforms', ['facebook', 'instagram'])
        content_theme = social_request.get('content_theme', 'general')
        post_count = social_request.get('post_count', 5)
        
        logger.info(f"Generating {post_count} social media posts for {restaurant_name}")
        
        # Create restaurant data for content generation
        restaurant_data = {
            "name": restaurant_name,
            "content_focus": content_theme,
            "user_id": current_user.get('user_id')
        }
        
        # Generate social media campaign
        content_suite = await ai_content_engine.generate_comprehensive_content_suite(
            restaurant_data, ['social_media_campaign']
        )
        
        if content_suite.get('success'):
            social_content = content_suite.get('generated_content', {}).get('social_media', {})
            
            return {
                "success": True,
                "message": f"Generated social media content for {len(platforms)} platforms",
                "data": {
                    "social_media_content": social_content,
                    "content_calendar": social_content.get('content_calendar', {}),
                    "posting_strategy": social_content.get('campaign_strategy', {})
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate social media content")
        
    except Exception as e:
        logger.error(f"Social media content generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Social media content generation failed: {str(e)}")

@router.post("/content/email-campaign")
async def generate_email_campaign(
    email_request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate email marketing campaign content
    """
    try:
        restaurant_name = email_request.get('restaurant_name', 'Restaurant')
        campaign_type = email_request.get('campaign_type', 'promotional')
        target_audience = email_request.get('target_audience', 'customers')
        
        logger.info(f"Generating {campaign_type} email campaign for {restaurant_name}")
        
        # Create restaurant data for email generation
        restaurant_data = {
            "name": restaurant_name,
            "email_focus": campaign_type,
            "target_audience": {"primary": target_audience},
            "user_id": current_user.get('user_id')
        }
        
        # Generate email marketing series
        content_suite = await ai_content_engine.generate_comprehensive_content_suite(
            restaurant_data, ['email_marketing_series']
        )
        
        if content_suite.get('success'):
            email_content = content_suite.get('generated_content', {}).get('email_series', {})
            
            return {
                "success": True,
                "message": f"Generated {campaign_type} email campaign",
                "data": {
                    "email_series": email_content.get('email_series', []),
                    "automation_triggers": email_content.get('automation_triggers', {}),
                    "performance_targets": email_content.get('performance_targets', {})
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate email campaign")
        
    except Exception as e:
        logger.error(f"Email campaign generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email campaign generation failed: {str(e)}")

# AI Insights and Analytics Endpoints
@router.post("/insights/comprehensive-analysis")
async def get_comprehensive_ai_insights(
    restaurant_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """
    Get comprehensive AI insights combining all AI services
    """
    try:
        restaurant_name = restaurant_data.get('name', 'Restaurant')
        logger.info(f"Generating comprehensive AI insights for: {restaurant_name}")
        
        # Add user context
        restaurant_data['user_id'] = current_user.get('user_id')
        restaurant_data['analysis_timestamp'] = datetime.now().isoformat()
        
        # Run all AI analyses in parallel
        digital_analysis_task = ai_grader_service.analyze_digital_presence(restaurant_data)
        menu_analysis_task = ai_menu_optimizer.analyze_menu_performance(restaurant_data)
        marketing_analysis_task = ai_marketing_assistant.get_marketing_recommendations(restaurant_data)
        
        # Wait for all analyses to complete
        digital_analysis = await digital_analysis_task
        menu_analysis = await menu_analysis_task
        marketing_analysis = await marketing_analysis_task
        
        # Combine insights
        comprehensive_insights = {
            "restaurant_name": restaurant_name,
            "analysis_date": datetime.now().isoformat(),
            "digital_presence": digital_analysis,
            "menu_optimization": menu_analysis,
            "marketing_strategy": marketing_analysis,
            "overall_recommendations": _generate_overall_recommendations(
                digital_analysis, menu_analysis, marketing_analysis
            ),
            "priority_actions": _generate_priority_actions(
                digital_analysis, menu_analysis, marketing_analysis
            ),
            "roi_projections": _calculate_combined_roi(
                digital_analysis, menu_analysis, marketing_analysis
            )
        }
        
        return {
            "success": True,
            "message": "Comprehensive AI analysis completed",
            "data": comprehensive_insights
        }
        
    except Exception as e:
        logger.error(f"Comprehensive analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

@router.get("/insights/dashboard-summary")
async def get_ai_dashboard_summary(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get AI insights dashboard summary for the current user
    """
    try:
        user_id = current_user.get('user_id')
        logger.info(f"Generating AI dashboard summary for user: {user_id}")
        
        # This would typically fetch from database, but for MVP we'll return mock data
        dashboard_summary = {
            "user_id": user_id,
            "last_analysis_date": datetime.now().isoformat(),
            "ai_features_available": [
                {
                    "feature": "Digital Presence Grader",
                    "status": "available",
                    "description": "Analyze and improve your online presence"
                },
                {
                    "feature": "Smart Menu Optimizer",
                    "status": "available", 
                    "description": "Optimize menu performance and pricing"
                },
                {
                    "feature": "AI Marketing Assistant",
                    "status": "available",
                    "description": "Get personalized marketing recommendations"
                },
                {
                    "feature": "Content Generation Engine",
                    "status": "available",
                    "description": "Generate marketing content across all channels"
                }
            ],
            "quick_stats": {
                "analyses_run": 0,
                "content_generated": 0,
                "campaigns_created": 0,
                "estimated_roi": "Calculate with first analysis"
            },
            "next_recommended_action": "Run Digital Presence Analysis to get started"
        }
        
        return {
            "success": True,
            "message": "AI dashboard summary retrieved",
            "data": dashboard_summary
        }
        
    except Exception as e:
        logger.error(f"Dashboard summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dashboard summary failed: {str(e)}")

# Helper functions for comprehensive analysis
def _generate_overall_recommendations(digital_analysis: Dict, menu_analysis: Dict, marketing_analysis: Dict) -> List[str]:
    """Generate overall recommendations from all analyses"""
    recommendations = []
    
    # Extract recommendations from each analysis
    if digital_analysis.get('success'):
        digital_actions = digital_analysis.get('action_plan', {}).get('immediate_actions', [])
        recommendations.extend([action.get('action', '') for action in digital_actions[:2]])
    
    if menu_analysis.get('success'):
        menu_actions = menu_analysis.get('optimization_plan', {}).get('immediate_actions', [])
        recommendations.extend(menu_actions[:2])
    
    if marketing_analysis.get('success'):
        marketing_plan = marketing_analysis.get('comprehensive_plan', {}).get('implementation_roadmap', {})
        phase_1_actions = marketing_plan.get('phase_1_30_days', {}).get('actions', [])
        recommendations.extend(phase_1_actions[:2])
    
    return recommendations[:5]  # Return top 5 recommendations

def _generate_priority_actions(digital_analysis: Dict, menu_analysis: Dict, marketing_analysis: Dict) -> List[Dict[str, Any]]:
    """Generate priority actions from all analyses"""
    priority_actions = []
    
    # High-impact actions from digital presence
    if digital_analysis.get('success'):
        digital_actions = digital_analysis.get('action_plan', {}).get('immediate_actions', [])
        for action in digital_actions[:2]:
            priority_actions.append({
                "action": action.get('action', ''),
                "source": "Digital Presence",
                "impact": action.get('estimated_impact', 'Medium'),
                "effort": action.get('effort_level', 'Medium')
            })
    
    # High-impact actions from menu optimization
    if menu_analysis.get('success'):
        promotional_campaigns = menu_analysis.get('promotional_strategies', {}).get('recommended_campaigns', [])
        for campaign in promotional_campaigns[:1]:
            priority_actions.append({
                "action": f"Launch {campaign.get('name', 'promotional campaign')}",
                "source": "Menu Optimization",
                "impact": "High",
                "effort": "Medium"
            })
    
    return priority_actions[:3]  # Return top 3 priority actions

def _calculate_combined_roi(digital_analysis: Dict, menu_analysis: Dict, marketing_analysis: Dict) -> Dict[str, Any]:
    """Calculate combined ROI projections from all analyses"""
    total_monthly_impact = 0
    total_annual_impact = 0
    
    # Extract revenue impacts
    if digital_analysis.get('success'):
        digital_impact = digital_analysis.get('revenue_impact', {})
        monthly_low = digital_impact.get('monthly_revenue_increase', {}).get('low_estimate', '$0')
        monthly_amount = int(monthly_low.replace('$', '').replace(',', '')) if monthly_low != '$0' else 0
        total_monthly_impact += monthly_amount
    
    if menu_analysis.get('success'):
        menu_impact = menu_analysis.get('revenue_impact', {})
        monthly_increase = menu_impact.get('potential_monthly_increase', '$0')
        monthly_amount = int(monthly_increase.replace('$', '').replace(',', '')) if monthly_increase != '$0' else 0
        total_monthly_impact += monthly_amount
    
    if marketing_analysis.get('success'):
        marketing_roi = marketing_analysis.get('roi_projections', {})
        monthly_revenue = marketing_roi.get('estimated_monthly_revenue_increase', '$0')
        monthly_amount = int(monthly_revenue.replace('$', '').replace(',', '')) if monthly_revenue != '$0' else 0
        total_monthly_impact += monthly_amount
    
    total_annual_impact = total_monthly_impact * 12
    
    return {
        "combined_monthly_impact": f"${total_monthly_impact:,}",
        "combined_annual_impact": f"${total_annual_impact:,}",
        "confidence_level": "Medium - Based on AI analysis of current state",
        "implementation_timeline": "2-6 months for full impact",
        "key_drivers": [
            "Digital presence improvements",
            "Menu optimization strategies", 
            "Marketing campaign effectiveness"
        ]
    }