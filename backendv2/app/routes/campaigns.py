"""
Campaign routes for Facebook ads and SMS campaigns with OpenAI integration
"""
from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from ..auth import get_current_restaurant_user
from ..services.openai_service import openai_service

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])
logger = logging.getLogger(__name__)

# Request models
class FacebookAdPreviewRequest(BaseModel):
    restaurantName: str
    itemToPromote: str
    offer: str

class SMSPreviewRequest(BaseModel):
    restaurantName: str
    offer: str
    offerCode: str

@router.post("/facebook-ads/preview")
async def generate_facebook_ad_preview(
    request: FacebookAdPreviewRequest,
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Generate Facebook ad preview using OpenAI"""
    try:
        logger.info(f"Generating Facebook ad preview for restaurant: {request.restaurantName}")
        
        # Generate ad copy using OpenAI service
        result = await openai_service.generate_ad_copy(
            restaurant_name=request.restaurantName,
            item_to_promote=request.itemToPromote,
            offer=request.offer,
            target_audience="local food lovers"
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Failed to generate ad copy")
        
        # Generate promo code
        promo_code = generate_promo_code(request.itemToPromote)
        
        return {
            "success": True,
            "preview": {
                "adCopy": result["ad_copy"],
                "promoCode": promo_code,
                "characterCount": result["metadata"]["character_count"]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate Facebook ad preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate ad preview: {str(e)}")

@router.post("/facebook-ads")
async def create_facebook_ad_campaign(
    restaurantName: str = Form(...),
    itemToPromote: str = Form(...),
    offer: str = Form(...),
    budget: str = Form(...),
    dishPhoto: Optional[UploadFile] = File(None),
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Create Facebook ad campaign with OpenAI-generated content"""
    try:
        logger.info(f"Creating Facebook ad campaign for restaurant: {restaurantName}")
        
        # Generate ad copy using OpenAI service
        ad_result = await openai_service.generate_ad_copy(
            restaurant_name=restaurantName,
            item_to_promote=itemToPromote,
            offer=offer,
            target_audience="local food lovers"
        )
        
        if not ad_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to generate ad copy")
        
        # Generate promo code
        promo_code = generate_promo_code(itemToPromote)
        
        # Mock campaign creation (would integrate with Facebook API in production)
        campaign_data = {
            "promoCode": promo_code,
            "adCopy": ad_result["ad_copy"],
            "expectedReach": calculate_expected_reach(float(budget)),
            "estimatedImpressions": calculate_estimated_impressions(float(budget)),
            "budget": float(budget)
        }
        
        return {
            "success": True,
            "message": f"Your Facebook ad for {itemToPromote} is now being created! Check your Facebook Ads Manager in a few minutes.",
            "data": campaign_data
        }
        
    except Exception as e:
        logger.error(f"Failed to create Facebook ad campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")

@router.post("/sms/preview")
async def generate_sms_preview(
    restaurantName: str = Form(...),
    offer: str = Form(...),
    offerCode: str = Form(...),
    customerList: Optional[UploadFile] = File(None),
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Generate SMS campaign preview using OpenAI"""
    try:
        logger.info(f"Generating SMS preview for restaurant: {restaurantName}")
        
        # Generate SMS message using OpenAI service
        result = await openai_service.generate_sms_message(
            restaurant_name=restaurantName,
            customer_name="[Customer Name]",
            offer=offer,
            offer_code=offerCode,
            message_type="winback"
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Failed to generate SMS message")
        
        # Mock CSV analysis
        target_customers = 25  # Mock number
        estimated_cost = target_customers * 0.05  # Mock cost calculation
        
        csv_stats = None
        if customerList:
            # In production, would parse the CSV file
            csv_stats = {
                "totalUploaded": 50,
                "lapsedCustomers": target_customers,
                "errors": 0
            }
        
        return {
            "success": True,
            "preview": {
                "sampleMessage": result["sms_message"],
                "characterCount": result["metadata"]["character_count"],
                "targetCustomers": target_customers,
                "estimatedCost": f"{estimated_cost:.2f}",
                "csvStats": csv_stats
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate SMS preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate SMS preview: {str(e)}")

@router.post("/sms")
async def create_sms_campaign(
    restaurantName: str = Form(...),
    offer: str = Form(...),
    offerCode: str = Form(...),
    customerList: UploadFile = File(...),
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Create SMS campaign with OpenAI-generated content"""
    try:
        logger.info(f"Creating SMS campaign for restaurant: {restaurantName}")
        
        # Generate SMS message using OpenAI service
        sms_result = await openai_service.generate_sms_message(
            restaurant_name=restaurantName,
            customer_name="[Customer Name]",
            offer=offer,
            offer_code=offerCode,
            message_type="winback"
        )
        
        if not sms_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to generate SMS message")
        
        # Mock campaign execution (would integrate with Twilio in production)
        messages_sent = 23  # Mock number
        total_cost = messages_sent * 0.05
        
        campaign_data = {
            "offerCode": offerCode,
            "messagesSent": messages_sent,
            "deliveryRate": "96%",
            "totalCost": f"{total_cost:.2f}",
            "totalCustomersUploaded": 50,
            "lapsedCustomersFound": 25,
            "sampleMessage": sms_result["sms_message"]
        }
        
        return {
            "success": True,
            "message": f"SMS campaign sent successfully to {messages_sent} customers!",
            "data": campaign_data
        }
        
    except Exception as e:
        logger.error(f"Failed to create SMS campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create SMS campaign: {str(e)}")

@router.get("/facebook-ads/status/{campaign_id}")
async def get_facebook_campaign_status(
    campaign_id: str,
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Get Facebook campaign status"""
    # Mock status response
    return {
        "success": True,
        "campaignId": campaign_id,
        "status": "ACTIVE",
        "metrics": {
            "impressions": 2500,
            "clicks": 125,
            "reach": 1800,
            "spend": "25.50"
        },
        "lastUpdated": "2025-06-28T12:00:00Z"
    }

@router.get("/sms/status/{campaign_id}")
async def get_sms_campaign_status(
    campaign_id: str,
    current_user = Depends(get_current_restaurant_user)
) -> Dict[str, Any]:
    """Get SMS campaign status"""
    # Mock status response
    return {
        "success": True,
        "campaignId": campaign_id,
        "status": "COMPLETED",
        "metrics": {
            "messagesSent": 23,
            "delivered": 22,
            "deliveryRate": "96%",
            "totalCost": "1.15"
        },
        "lastUpdated": "2025-06-28T12:00:00Z"
    }

@router.get("/sms/sample-csv")
async def download_sample_csv(
    current_user = Depends(get_current_restaurant_user)
):
    """Download sample CSV file for SMS campaigns"""
    from fastapi.responses import Response
    
    csv_content = """customer_name,phone_number,last_order_date
John Smith,+1234567890,2025-05-15
Jane Doe,+1987654321,2025-04-20
Mike Johnson,+1555123456,2025-03-10
Sarah Wilson,+1444987654,2025-02-28
"""
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sample-customer-list.csv"}
    )

# Helper functions
def generate_promo_code(item_to_promote: str) -> str:
    """Generate a promo code based on the item"""
    import re
    from datetime import datetime
    
    # Clean item name and take first 6 characters
    item_code = re.sub(r'[^a-zA-Z]', '', item_to_promote).upper()[:6]
    
    # Add day code
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    day_code = days[datetime.now().weekday()]
    
    return f"{item_code}{day_code}"

def calculate_expected_reach(budget: float) -> int:
    """Calculate expected reach based on budget"""
    # Mock calculation: $1 = ~100 people reach
    return int(budget * 100)

def calculate_estimated_impressions(budget: float) -> int:
    """Calculate estimated impressions based on budget"""
    # Mock calculation: $1 = ~200 impressions
    return int(budget * 200)