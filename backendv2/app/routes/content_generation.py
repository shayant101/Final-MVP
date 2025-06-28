"""
Content generation routes using OpenAI API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ..auth import get_current_restaurant_user
from ..services.openai_service import openai_service

router = APIRouter(prefix="/api/content", tags=["content_generation"])

# Request models
class AdCopyRequest(BaseModel):
    restaurant_name: str
    item_to_promote: str
    offer: str
    target_audience: Optional[str] = "local food lovers"

class SMSMessageRequest(BaseModel):
    restaurant_name: str
    customer_name: str
    offer: str
    offer_code: str
    message_type: Optional[str] = "winback"

class EmailCampaignRequest(BaseModel):
    restaurant_name: str
    campaign_type: str
    offer: str
    target_audience: Optional[str] = "customers"

class SocialMediaPostRequest(BaseModel):
    restaurant_name: str
    platform: str
    content_type: str
    item_to_promote: Optional[str] = ""
    offer: Optional[str] = ""

class MenuDescriptionRequest(BaseModel):
    restaurant_name: str
    cuisine_type: str
    items: List[Dict[str, str]]

class CampaignSuggestionsRequest(BaseModel):
    restaurant_name: str
    campaign_type: str
    business_goals: Optional[List[str]] = None

@router.post("/generate/ad-copy")
async def generate_ad_copy(
    request: AdCopyRequest,
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Generate Facebook ad copy using OpenAI"""
    try:
        result = await openai_service.generate_ad_copy(
            restaurant_name=request.restaurant_name,
            item_to_promote=request.item_to_promote,
            offer=request.offer,
            target_audience=request.target_audience
        )
        
        return {
            "success": True,
            "data": result,
            "restaurant_id": current_user.restaurant.restaurant_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ad copy: {str(e)}")

@router.post("/generate/sms-message")
async def generate_sms_message(
    request: SMSMessageRequest,
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Generate SMS message using OpenAI"""
    try:
        result = await openai_service.generate_sms_message(
            restaurant_name=request.restaurant_name,
            customer_name=request.customer_name,
            offer=request.offer,
            offer_code=request.offer_code,
            message_type=request.message_type
        )
        
        return {
            "success": True,
            "data": result,
            "restaurant_id": current_user.restaurant.restaurant_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate SMS message: {str(e)}")

@router.post("/generate/email-campaign")
async def generate_email_campaign(
    request: EmailCampaignRequest,
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Generate email campaign content using OpenAI"""
    try:
        result = await openai_service.generate_email_campaign(
            restaurant_name=request.restaurant_name,
            campaign_type=request.campaign_type,
            offer=request.offer,
            target_audience=request.target_audience
        )
        
        return {
            "success": True,
            "data": result,
            "restaurant_id": current_user.restaurant.restaurant_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate email campaign: {str(e)}")

@router.post("/generate/social-media-post")
async def generate_social_media_post(
    request: SocialMediaPostRequest,
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Generate social media post using OpenAI"""
    try:
        result = await openai_service.generate_social_media_post(
            restaurant_name=request.restaurant_name,
            platform=request.platform,
            content_type=request.content_type,
            item_to_promote=request.item_to_promote,
            offer=request.offer
        )
        
        return {
            "success": True,
            "data": result,
            "restaurant_id": current_user.restaurant.restaurant_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate social media post: {str(e)}")

@router.post("/generate/menu-descriptions")
async def generate_menu_descriptions(
    request: MenuDescriptionRequest,
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Generate menu item descriptions using OpenAI"""
    try:
        result = await openai_service.generate_menu_descriptions(
            restaurant_name=request.restaurant_name,
            cuisine_type=request.cuisine_type,
            items=request.items
        )
        
        return {
            "success": True,
            "data": result,
            "restaurant_id": current_user.restaurant.restaurant_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate menu descriptions: {str(e)}")

@router.post("/generate/campaign-suggestions")
async def generate_campaign_suggestions(
    request: CampaignSuggestionsRequest,
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Generate campaign suggestions using OpenAI"""
    try:
        result = await openai_service.generate_campaign_suggestions(
            restaurant_name=request.restaurant_name,
            campaign_type=request.campaign_type,
            business_goals=request.business_goals
        )
        
        return {
            "success": True,
            "data": result,
            "restaurant_id": current_user.restaurant.restaurant_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate campaign suggestions: {str(e)}")

@router.get("/test-connection")
async def test_openai_connection(
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Test OpenAI API connection"""
    try:
        result = await openai_service.test_connection()
        
        return {
            "success": True,
            "data": result,
            "restaurant_id": current_user.restaurant.restaurant_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test OpenAI connection: {str(e)}")

# Bulk content generation endpoints
@router.post("/generate/bulk/social-media")
async def generate_bulk_social_media(
    platforms: List[str],
    request: SocialMediaPostRequest,
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Generate social media posts for multiple platforms"""
    try:
        results = {}
        
        for platform in platforms:
            try:
                result = await openai_service.generate_social_media_post(
                    restaurant_name=request.restaurant_name,
                    platform=platform,
                    content_type=request.content_type,
                    item_to_promote=request.item_to_promote,
                    offer=request.offer
                )
                results[platform] = result
            except Exception as e:
                results[platform] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": True,
            "data": results,
            "restaurant_id": current_user.restaurant.restaurant_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate bulk social media content: {str(e)}")

@router.post("/generate/marketing-package")
async def generate_marketing_package(
    request: AdCopyRequest,
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Generate a complete marketing package (ad copy, social posts, email)"""
    try:
        # Generate ad copy
        ad_copy_result = await openai_service.generate_ad_copy(
            restaurant_name=request.restaurant_name,
            item_to_promote=request.item_to_promote,
            offer=request.offer,
            target_audience=request.target_audience
        )
        
        # Generate social media posts for multiple platforms
        social_platforms = ["facebook", "instagram", "twitter"]
        social_results = {}
        
        for platform in social_platforms:
            try:
                result = await openai_service.generate_social_media_post(
                    restaurant_name=request.restaurant_name,
                    platform=platform,
                    content_type="promotional",
                    item_to_promote=request.item_to_promote,
                    offer=request.offer
                )
                social_results[platform] = result
            except Exception as e:
                social_results[platform] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Generate email campaign
        email_result = await openai_service.generate_email_campaign(
            restaurant_name=request.restaurant_name,
            campaign_type="promotional",
            offer=request.offer,
            target_audience=request.target_audience
        )
        
        return {
            "success": True,
            "data": {
                "ad_copy": ad_copy_result,
                "social_media": social_results,
                "email_campaign": email_result
            },
            "restaurant_id": current_user.restaurant.restaurant_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate marketing package: {str(e)}")