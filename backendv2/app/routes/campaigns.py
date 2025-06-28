"""
Campaign management routes for Facebook Ads and SMS campaigns
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from fastapi.responses import PlainTextResponse
from typing import List, Optional
import json

from ..auth import get_current_user, get_current_restaurant_user
from ..models import (
    User, Campaign, FacebookAdCampaignCreate, SMSCampaignCreate, 
    CampaignUpdate, CampaignResponse, CampaignListResponse,
    SMSPreviewRequest, FacebookAdPreviewRequest
)
from ..services.campaign_service import campaign_service
from ..services.mock_openai import generate_ad_copy, generate_sms_message, generate_promo_code
from ..utils.csv_parser import parse_customer_csv, filter_lapsed_customers, generate_sample_csv

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

# Facebook Ad Campaign Routes

@router.post("/facebook-ads", response_model=CampaignResponse)
async def create_facebook_ad_campaign(
    restaurantName: str = Form(...),
    itemToPromote: str = Form(...),
    offer: str = Form(...),
    budget: float = Form(...),
    dishPhoto: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_restaurant_user)
):
    """
    Create a new Facebook ad campaign
    """
    try:
        # Validate file type if photo is provided
        if dishPhoto:
            if not dishPhoto.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="Only image files are allowed")
            
            # Check file size (5MB limit)
            content = await dishPhoto.read()
            if len(content) > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File size must be less than 5MB")
            
            # Reset file pointer
            await dishPhoto.seek(0)
        
        campaign_data = FacebookAdCampaignCreate(
            restaurantName=restaurantName,
            itemToPromote=itemToPromote,
            offer=offer,
            budget=budget
        )
        
        restaurant_id = current_user.restaurant.restaurant_id
        result = await campaign_service.create_facebook_ad_campaign(
            restaurant_id, campaign_data, dishPhoto
        )
        
        return CampaignResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/facebook-ads/preview", response_model=dict)
async def generate_facebook_ad_preview(
    preview_data: FacebookAdPreviewRequest,
    current_user: User = Depends(get_current_restaurant_user)
):
    """
    Generate a preview of Facebook ad copy
    """
    try:
        # Generate ad copy preview
        ad_copy_result = await generate_ad_copy(
            preview_data.restaurantName,
            preview_data.itemToPromote,
            preview_data.offer
        )
        
        promo_code = generate_promo_code(preview_data.itemToPromote)
        
        return {
            "success": True,
            "preview": {
                "ad_copy": ad_copy_result["ad_copy"],
                "promo_code": promo_code,
                "character_count": ad_copy_result["metadata"]["character_count"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")

# SMS Campaign Routes

@router.post("/sms", response_model=CampaignResponse)
async def create_sms_campaign(
    restaurantName: str = Form(...),
    offer: str = Form(...),
    offerCode: str = Form(...),
    customerList: UploadFile = File(...),
    current_user: User = Depends(get_current_restaurant_user)
):
    """
    Create a new SMS campaign
    """
    try:
        # Validate CSV file
        if not customerList.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Check file size (2MB limit)
        content = await customerList.read()
        if len(content) > 2 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 2MB")
        
        # Reset file pointer
        await customerList.seek(0)
        
        campaign_data = SMSCampaignCreate(
            restaurantName=restaurantName,
            offer=offer,
            offerCode=offerCode
        )
        
        restaurant_id = current_user.restaurant.restaurant_id
        result = await campaign_service.create_sms_campaign(
            restaurant_id, campaign_data, customerList
        )
        
        return CampaignResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/sms/preview", response_model=dict)
async def generate_sms_preview(
    restaurantName: str = Form(...),
    offer: str = Form(...),
    offerCode: str = Form(...),
    customerList: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_restaurant_user)
):
    """
    Generate a preview of SMS campaign
    """
    try:
        customers = []
        csv_stats = None
        
        # If CSV file is provided, parse it for preview
        if customerList:
            if customerList.filename.endswith('.csv'):
                parse_result = await parse_customer_csv(customerList)
                if parse_result["success"]:
                    customers = filter_lapsed_customers(parse_result["customers"], 30)
                    csv_stats = {
                        "total_uploaded": parse_result["valid_rows"],
                        "lapsed_customers": len(customers),
                        "errors": len(parse_result["errors"])
                    }
        
        # Generate sample SMS message
        sample_customer_name = customers[0]["customer_name"] if customers else "Sarah"
        sms_result = await generate_sms_message(restaurantName, sample_customer_name, offer, offerCode)
        
        return {
            "success": True,
            "preview": {
                "sample_message": sms_result["sms_message"],
                "character_count": sms_result["metadata"]["character_count"],
                "offer_code": offerCode,
                "estimated_cost": f"{len(customers) * 0.0075:.4f}" if customers else "0.0000",
                "target_customers": len(customers),
                "csv_stats": csv_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")

@router.get("/sms/sample-csv")
async def download_sample_csv():
    """
    Download a sample CSV file for SMS campaigns
    """
    try:
        sample_csv = generate_sample_csv()
        
        return PlainTextResponse(
            content=sample_csv,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=sample-customer-list.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate sample CSV: {str(e)}")

# General Campaign Management Routes

@router.get("/{restaurant_id}", response_model=CampaignListResponse)
async def get_campaigns_by_restaurant(
    restaurant_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all campaigns for a restaurant
    """
    try:
        # Check access permissions
        if current_user.role == "restaurant":
            if current_user.restaurant.restaurant_id != restaurant_id:
                raise HTTPException(status_code=403, detail="Access denied")
        elif current_user.role == "admin":
            # Admins can access any restaurant's campaigns
            if current_user.impersonating_restaurant_id:
                restaurant_id = current_user.impersonating_restaurant_id
        
        campaigns = await campaign_service.get_campaigns_by_restaurant(restaurant_id)
        
        return CampaignListResponse(
            success=True,
            campaigns=campaigns,
            total=len(campaigns)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch campaigns: {str(e)}")

@router.get("/campaign/{campaign_id}", response_model=Campaign)
async def get_campaign_details(
    campaign_id: str,
    current_user: User = Depends(get_current_restaurant_user)
):
    """
    Get specific campaign details
    """
    try:
        restaurant_id = current_user.restaurant.restaurant_id
        campaign = await campaign_service.get_campaign_by_id(campaign_id, restaurant_id)
        
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch campaign: {str(e)}")

@router.put("/campaign/{campaign_id}", response_model=Campaign)
async def update_campaign(
    campaign_id: str,
    update_data: CampaignUpdate,
    current_user: User = Depends(get_current_restaurant_user)
):
    """
    Update a campaign
    """
    try:
        restaurant_id = current_user.restaurant.restaurant_id
        updated_campaign = await campaign_service.update_campaign(
            campaign_id, restaurant_id, update_data
        )
        
        return updated_campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update campaign: {str(e)}")

@router.delete("/campaign/{campaign_id}", response_model=dict)
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_restaurant_user)
):
    """
    Delete a campaign
    """
    try:
        restaurant_id = current_user.restaurant.restaurant_id
        result = await campaign_service.delete_campaign(campaign_id, restaurant_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete campaign: {str(e)}")

@router.post("/campaign/{campaign_id}/launch", response_model=dict)
async def launch_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_restaurant_user)
):
    """
    Launch a draft campaign
    """
    try:
        restaurant_id = current_user.restaurant.restaurant_id
        result = await campaign_service.launch_campaign(campaign_id, restaurant_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to launch campaign: {str(e)}")

@router.put("/campaign/{campaign_id}/pause", response_model=dict)
async def pause_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_restaurant_user)
):
    """
    Pause an active campaign
    """
    try:
        restaurant_id = current_user.restaurant.restaurant_id
        result = await campaign_service.pause_campaign(campaign_id, restaurant_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pause campaign: {str(e)}")

# Campaign Status and Analytics Routes

@router.get("/facebook-ads/status/{campaign_id}", response_model=dict)
async def get_facebook_campaign_status(
    campaign_id: str,
    current_user: User = Depends(get_current_restaurant_user)
):
    """
    Get Facebook campaign status and metrics
    """
    try:
        # Get campaign from database to verify ownership
        restaurant_id = current_user.restaurant.restaurant_id
        campaign = await campaign_service.get_campaign_by_id(campaign_id, restaurant_id)
        
        if campaign.campaign_type != "facebook_ad":
            raise HTTPException(status_code=400, detail="Campaign is not a Facebook ad campaign")
        
        # Get Facebook campaign ID from details
        facebook_campaign_id = campaign.details.get("facebook_campaign_id")
        if not facebook_campaign_id:
            raise HTTPException(status_code=404, detail="Facebook campaign ID not found")
        
        # Mock status response (in real implementation, would call Facebook API)
        from ..services.mock_facebook import get_campaign_status
        status = await get_campaign_status(facebook_campaign_id)
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch campaign status: {str(e)}")

@router.get("/sms/status/{campaign_id}", response_model=dict)
async def get_sms_campaign_status(
    campaign_id: str,
    current_user: User = Depends(get_current_restaurant_user)
):
    """
    Get SMS campaign status and metrics
    """
    try:
        # Get campaign from database to verify ownership
        restaurant_id = current_user.restaurant.restaurant_id
        campaign = await campaign_service.get_campaign_by_id(campaign_id, restaurant_id)
        
        if campaign.campaign_type != "sms":
            raise HTTPException(status_code=400, detail="Campaign is not an SMS campaign")
        
        # Get Twilio campaign ID from details
        twilio_campaign_id = campaign.details.get("twilio_campaign_id")
        if not twilio_campaign_id:
            raise HTTPException(status_code=404, detail="Twilio campaign ID not found")
        
        # Mock status response (in real implementation, would call Twilio API)
        from ..services.mock_twilio import get_sms_delivery_report
        status = await get_sms_delivery_report(twilio_campaign_id)
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch campaign status: {str(e)}")