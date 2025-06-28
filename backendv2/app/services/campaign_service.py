"""
Campaign service for managing Facebook Ads and SMS campaigns
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import UploadFile, HTTPException

from ..database import get_database
from ..models import (
    Campaign, CampaignType, CampaignStatus, FacebookAdCampaignCreate, 
    SMSCampaignCreate, CampaignUpdate, CampaignMetrics
)
from .mock_facebook import create_ad_campaign, get_campaign_status, validate_budget
from .mock_twilio import send_sms_campaign, get_sms_delivery_report
from .mock_openai import generate_ad_copy, generate_sms_message, generate_promo_code
from ..utils.csv_parser import parse_customer_csv, filter_lapsed_customers

class CampaignService:
    def __init__(self):
        self.db = None
    
    async def get_db(self):
        if not self.db:
            self.db = get_database()
        return self.db

    async def create_facebook_ad_campaign(self, restaurant_id: str, campaign_data: FacebookAdCampaignCreate, dish_photo: Optional[UploadFile] = None) -> Dict[str, Any]:
        """Create a new Facebook ad campaign"""
        try:
            # Validate budget
            budget_validation = validate_budget(campaign_data.budget)
            if not budget_validation["valid"]:
                raise HTTPException(status_code=400, detail=budget_validation["error"])
            
            # Generate promo code
            promo_code = generate_promo_code(campaign_data.itemToPromote)
            
            # Generate ad copy
            ad_copy_result = await generate_ad_copy(
                campaign_data.restaurantName,
                campaign_data.itemToPromote,
                campaign_data.offer
            )
            
            if not ad_copy_result["success"]:
                raise HTTPException(status_code=500, detail="Failed to generate ad copy")
            
            # Handle photo upload
            dish_photo_filename = None
            if dish_photo:
                # In a real implementation, you'd save the file to storage
                dish_photo_filename = f"dish_{uuid.uuid4().hex[:8]}_{dish_photo.filename}"
            
            # Create Facebook ad campaign
            fb_campaign_data = {
                "restaurant_name": campaign_data.restaurantName,
                "item_to_promote": campaign_data.itemToPromote,
                "offer": campaign_data.offer,
                "budget": campaign_data.budget,
                "ad_copy": ad_copy_result["ad_copy"],
                "promo_code": promo_code,
                "dish_photo": dish_photo_filename
            }
            
            campaign_result = await create_ad_campaign(fb_campaign_data)
            
            if not campaign_result["success"]:
                raise HTTPException(status_code=500, detail="Failed to create Facebook ad campaign")
            
            # Save campaign to database
            campaign_id = str(uuid.uuid4())
            db = await self.get_db()
            
            campaign_doc = {
                "campaign_id": campaign_id,
                "restaurant_id": restaurant_id,
                "campaign_type": CampaignType.facebook_ad,
                "status": CampaignStatus.active,
                "name": f"{campaign_data.restaurantName} - {campaign_data.itemToPromote} Promotion",
                "details": {
                    "restaurant_name": campaign_data.restaurantName,
                    "item_to_promote": campaign_data.itemToPromote,
                    "offer": campaign_data.offer,
                    "budget": campaign_data.budget,
                    "ad_copy": ad_copy_result["ad_copy"],
                    "promo_code": promo_code,
                    "dish_photo": dish_photo_filename,
                    "facebook_campaign_id": campaign_result["campaign"]["id"],
                    "ad_set_id": campaign_result["ad_set"]["id"],
                    "ad_id": campaign_result["ad"]["id"],
                    "expected_reach": campaign_result["tracking"]["expected_reach"],
                    "estimated_impressions": campaign_result["tracking"]["estimated_impressions"],
                    "campaign_url": campaign_result["tracking"]["campaign_url"]
                },
                "budget": campaign_data.budget,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "launched_at": datetime.now()
            }
            
            await db.campaigns.insert_one(campaign_doc)
            
            return {
                "success": True,
                "message": f"Your Facebook ad for {campaign_data.itemToPromote} is now being created! Check your Facebook Ads Manager in a few minutes.",
                "data": {
                    "campaign_id": campaign_id,
                    "promo_code": promo_code,
                    "facebook_campaign_id": campaign_result["campaign"]["id"],
                    "ad_copy": ad_copy_result["ad_copy"],
                    "expected_reach": campaign_result["tracking"]["expected_reach"],
                    "estimated_impressions": campaign_result["tracking"]["estimated_impressions"],
                    "campaign_url": campaign_result["tracking"]["campaign_url"],
                    "budget": campaign_data.budget,
                    "created_at": campaign_result["metadata"]["created_at"]
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    async def create_sms_campaign(self, restaurant_id: str, campaign_data: SMSCampaignCreate, customer_list: UploadFile) -> Dict[str, Any]:
        """Create a new SMS campaign"""
        try:
            # Validate CSV file
            if not customer_list.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail="Only CSV files are allowed")
            
            # Parse CSV file
            parse_result = await parse_customer_csv(customer_list)
            
            if not parse_result["success"]:
                raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {parse_result.get('details', 'Unknown error')}")
            
            if parse_result["valid_rows"] == 0:
                raise HTTPException(status_code=400, detail="No valid customers found in CSV file")
            
            # Filter for lapsed customers (last order > 30 days ago)
            lapsed_customers = filter_lapsed_customers(parse_result["customers"], 30)
            
            if len(lapsed_customers) == 0:
                return {
                    "success": True,
                    "message": "No lapsed customers found (all customers have ordered within the last 30 days)",
                    "data": {
                        "total_customers": parse_result["valid_rows"],
                        "lapsed_customers": 0,
                        "offer_code": campaign_data.offerCode
                    }
                }
            
            # Generate personalized SMS messages for each customer
            sms_results = []
            for customer in lapsed_customers:
                try:
                    sms_result = await generate_sms_message(
                        campaign_data.restaurantName,
                        customer["customer_name"],
                        campaign_data.offer,
                        campaign_data.offerCode
                    )
                    
                    sms_results.append({
                        "customer": customer,
                        "sms_message": sms_result["sms_message"],
                        "character_count": sms_result["metadata"]["character_count"]
                    })
                except Exception as e:
                    sms_results.append({
                        "customer": customer,
                        "error": f"Failed to generate SMS message: {str(e)}"
                    })
            
            # Send SMS campaign
            sample_message = sms_results[0]["sms_message"] if sms_results else f"Hi! We miss you at {campaign_data.restaurantName}! {campaign_data.offer} Use code {campaign_data.offerCode}"
            
            campaign_result = await send_sms_campaign(
                lapsed_customers,
                sample_message,
                campaign_data.offerCode
            )
            
            # Save campaign to database
            campaign_id = str(uuid.uuid4())
            db = await self.get_db()
            
            campaign_doc = {
                "campaign_id": campaign_id,
                "restaurant_id": restaurant_id,
                "campaign_type": CampaignType.sms,
                "status": CampaignStatus.completed,
                "name": f"{campaign_data.restaurantName} - SMS Campaign",
                "details": {
                    "restaurant_name": campaign_data.restaurantName,
                    "offer": campaign_data.offer,
                    "offer_code": campaign_data.offerCode,
                    "total_customers_uploaded": parse_result["valid_rows"],
                    "lapsed_customers_found": len(lapsed_customers),
                    "messages_sent": campaign_result["delivery"]["sent"],
                    "messages_failed": campaign_result["delivery"]["failed"],
                    "messages_pending": campaign_result["delivery"]["pending"],
                    "total_cost": campaign_result["costs"]["total_cost"],
                    "sample_message": sample_message,
                    "delivery_rate": f"{round((campaign_result['delivery']['sent'] / len(lapsed_customers)) * 100)}%",
                    "csv_errors": parse_result["errors"],
                    "twilio_campaign_id": campaign_result["campaign"]["id"]
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "launched_at": datetime.now()
            }
            
            await db.campaigns.insert_one(campaign_doc)
            
            return {
                "success": True,
                "message": f"SMS campaign sent to {campaign_result['delivery']['sent']} lapsed customers! Track redemptions using code {campaign_data.offerCode}.",
                "data": {
                    "campaign_id": campaign_id,
                    "twilio_campaign_id": campaign_result["campaign"]["id"],
                    "offer_code": campaign_data.offerCode,
                    "total_customers_uploaded": parse_result["valid_rows"],
                    "lapsed_customers_found": len(lapsed_customers),
                    "messages_sent": campaign_result["delivery"]["sent"],
                    "messages_failed": campaign_result["delivery"]["failed"],
                    "messages_pending": campaign_result["delivery"]["pending"],
                    "total_cost": campaign_result["costs"]["total_cost"],
                    "sample_message": sample_message,
                    "delivery_rate": f"{round((campaign_result['delivery']['sent'] / len(lapsed_customers)) * 100)}%",
                    "created_at": campaign_result["campaign"]["created_at"],
                    "csv_errors": parse_result["errors"]
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    async def get_campaigns_by_restaurant(self, restaurant_id: str) -> List[Campaign]:
        """Get all campaigns for a restaurant"""
        try:
            db = await self.get_db()
            campaigns_cursor = db.campaigns.find({"restaurant_id": restaurant_id})
            campaigns = []
            
            async for campaign_doc in campaigns_cursor:
                campaign = Campaign(
                    campaign_id=campaign_doc["campaign_id"],
                    restaurant_id=campaign_doc["restaurant_id"],
                    campaign_type=campaign_doc["campaign_type"],
                    status=campaign_doc["status"],
                    name=campaign_doc["name"],
                    details=campaign_doc.get("details"),
                    budget=campaign_doc.get("budget"),
                    created_at=campaign_doc["created_at"],
                    updated_at=campaign_doc["updated_at"],
                    launched_at=campaign_doc.get("launched_at"),
                    paused_at=campaign_doc.get("paused_at")
                )
                campaigns.append(campaign)
            
            return campaigns
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch campaigns: {str(e)}")

    async def get_campaign_by_id(self, campaign_id: str, restaurant_id: Optional[str] = None) -> Campaign:
        """Get a specific campaign by ID"""
        try:
            db = await self.get_db()
            query = {"campaign_id": campaign_id}
            if restaurant_id:
                query["restaurant_id"] = restaurant_id
            
            campaign_doc = await db.campaigns.find_one(query)
            
            if not campaign_doc:
                raise HTTPException(status_code=404, detail="Campaign not found")
            
            return Campaign(
                campaign_id=campaign_doc["campaign_id"],
                restaurant_id=campaign_doc["restaurant_id"],
                campaign_type=campaign_doc["campaign_type"],
                status=campaign_doc["status"],
                name=campaign_doc["name"],
                details=campaign_doc.get("details"),
                budget=campaign_doc.get("budget"),
                created_at=campaign_doc["created_at"],
                updated_at=campaign_doc["updated_at"],
                launched_at=campaign_doc.get("launched_at"),
                paused_at=campaign_doc.get("paused_at")
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch campaign: {str(e)}")

    async def update_campaign(self, campaign_id: str, restaurant_id: str, update_data: CampaignUpdate) -> Campaign:
        """Update a campaign"""
        try:
            db = await self.get_db()
            
            # Check if campaign exists and belongs to restaurant
            existing_campaign = await db.campaigns.find_one({
                "campaign_id": campaign_id,
                "restaurant_id": restaurant_id
            })
            
            if not existing_campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")
            
            # Prepare update data
            update_fields = {"updated_at": datetime.now()}
            
            if update_data.name is not None:
                update_fields["name"] = update_data.name
            
            if update_data.status is not None:
                update_fields["status"] = update_data.status
                if update_data.status == CampaignStatus.paused:
                    update_fields["paused_at"] = datetime.now()
            
            if update_data.budget is not None:
                update_fields["budget"] = update_data.budget
            
            if update_data.details is not None:
                # Merge with existing details
                existing_details = existing_campaign.get("details", {})
                existing_details.update(update_data.details)
                update_fields["details"] = existing_details
            
            # Update in database
            await db.campaigns.update_one(
                {"campaign_id": campaign_id},
                {"$set": update_fields}
            )
            
            # Return updated campaign
            return await self.get_campaign_by_id(campaign_id, restaurant_id)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update campaign: {str(e)}")

    async def delete_campaign(self, campaign_id: str, restaurant_id: str) -> Dict[str, Any]:
        """Delete a campaign"""
        try:
            db = await self.get_db()
            
            # Check if campaign exists and belongs to restaurant
            existing_campaign = await db.campaigns.find_one({
                "campaign_id": campaign_id,
                "restaurant_id": restaurant_id
            })
            
            if not existing_campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")
            
            # Delete campaign
            result = await db.campaigns.delete_one({"campaign_id": campaign_id})
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=500, detail="Failed to delete campaign")
            
            return {
                "success": True,
                "message": "Campaign deleted successfully",
                "campaign_id": campaign_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete campaign: {str(e)}")

    async def launch_campaign(self, campaign_id: str, restaurant_id: str) -> Dict[str, Any]:
        """Launch a draft campaign"""
        try:
            campaign = await self.get_campaign_by_id(campaign_id, restaurant_id)
            
            if campaign.status != CampaignStatus.draft:
                raise HTTPException(status_code=400, detail="Only draft campaigns can be launched")
            
            # Update campaign status
            update_data = CampaignUpdate(status=CampaignStatus.active)
            updated_campaign = await self.update_campaign(campaign_id, restaurant_id, update_data)
            
            # Update launched_at timestamp
            db = await self.get_db()
            await db.campaigns.update_one(
                {"campaign_id": campaign_id},
                {"$set": {"launched_at": datetime.now()}}
            )
            
            return {
                "success": True,
                "message": "Campaign launched successfully",
                "campaign": updated_campaign
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to launch campaign: {str(e)}")

    async def pause_campaign(self, campaign_id: str, restaurant_id: str) -> Dict[str, Any]:
        """Pause an active campaign"""
        try:
            campaign = await self.get_campaign_by_id(campaign_id, restaurant_id)
            
            if campaign.status != CampaignStatus.active:
                raise HTTPException(status_code=400, detail="Only active campaigns can be paused")
            
            # Update campaign status
            update_data = CampaignUpdate(status=CampaignStatus.paused)
            updated_campaign = await self.update_campaign(campaign_id, restaurant_id, update_data)
            
            return {
                "success": True,
                "message": "Campaign paused successfully",
                "campaign": updated_campaign
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to pause campaign: {str(e)}")

# Create service instance
campaign_service = CampaignService()