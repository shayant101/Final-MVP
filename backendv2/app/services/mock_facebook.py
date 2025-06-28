"""
Mock Facebook Marketing API service for creating ad campaigns
"""
import asyncio
import random
import time
from datetime import datetime
from typing import Dict, Any

async def create_ad_campaign(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a Facebook ad campaign (mock implementation)"""
    # Simulate API delay
    await asyncio.sleep(2.0)
    
    restaurant_name = campaign_data.get("restaurant_name")
    item_to_promote = campaign_data.get("item_to_promote")
    offer = campaign_data.get("offer")
    budget = campaign_data.get("budget")
    ad_copy = campaign_data.get("ad_copy")
    promo_code = campaign_data.get("promo_code")
    
    # Generate realistic campaign IDs
    timestamp = int(time.time())
    campaign_id = f"camp_{timestamp}_{random.randint(100000000, 999999999)}"
    ad_set_id = f"adset_{timestamp}_{random.randint(100000000, 999999999)}"
    ad_id = f"ad_{timestamp}_{random.randint(100000000, 999999999)}"
    
    # Simulate campaign creation response
    campaign_response = {
        "success": True,
        "campaign": {
            "id": campaign_id,
            "name": f"{restaurant_name} - {item_to_promote} Promotion",
            "objective": "STORE_TRAFFIC",
            "status": "ACTIVE",
            "created_time": datetime.now().isoformat(),
            "budget_remaining": budget * 100,  # Convert to cents
            "daily_budget": budget * 100
        },
        "ad_set": {
            "id": ad_set_id,
            "name": f"{restaurant_name} Local Audience",
            "targeting": {
                "geo_locations": {
                    "custom_locations": [
                        {
                            "radius": 2,
                            "distance_unit": "mile",
                            "address_string": "Restaurant Location"  # Hardcoded for MVP
                        }
                    ]
                },
                "age_min": 18,
                "age_max": 65
            },
            "optimization_goal": "REACH",
            "billing_event": "IMPRESSIONS"
        },
        "ad": {
            "id": ad_id,
            "name": f"{item_to_promote} Special Ad",
            "creative": {
                "title": f"{restaurant_name} Special Offer",
                "body": ad_copy,
                "call_to_action_type": "LEARN_MORE"
            },
            "status": "ACTIVE"
        },
        "tracking": {
            "promo_code": promo_code,
            "expected_reach": random.randint(1000, 6000),
            "estimated_impressions": random.randint(2000, 12000),
            "campaign_url": f"https://facebook.com/ads/manager/campaigns/{campaign_id}"
        },
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "platform": "Facebook Marketing API",
            "version": "v18.0"
        }
    }
    
    return campaign_response

async def get_campaign_status(campaign_id: str) -> Dict[str, Any]:
    """Get Facebook campaign status (mock implementation)"""
    # Simulate API delay
    await asyncio.sleep(0.8)
    
    statuses = ["ACTIVE", "PAUSED", "PENDING_REVIEW"]
    random_status = random.choice(statuses)
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "status": random_status,
        "metrics": {
            "impressions": random.randint(500, 5500),
            "clicks": random.randint(20, 220),
            "reach": random.randint(300, 3300),
            "spend": round(random.uniform(10, 60), 2)
        },
        "last_updated": datetime.now().isoformat()
    }

def validate_budget(budget: float) -> Dict[str, Any]:
    """Validate Facebook ad budget"""
    min_budget = 5.0
    max_budget = 1000.0
    
    if budget < min_budget:
        return {
            "valid": False,
            "error": f"Minimum daily budget is ${min_budget}"
        }
    
    if budget > max_budget:
        return {
            "valid": False,
            "error": f"Maximum daily budget is ${max_budget}"
        }
    
    return {"valid": True}

async def pause_campaign(campaign_id: str) -> Dict[str, Any]:
    """Pause a Facebook campaign (mock implementation)"""
    await asyncio.sleep(1.0)
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "status": "PAUSED",
        "message": "Campaign paused successfully",
        "paused_at": datetime.now().isoformat()
    }

async def resume_campaign(campaign_id: str) -> Dict[str, Any]:
    """Resume a Facebook campaign (mock implementation)"""
    await asyncio.sleep(1.0)
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "status": "ACTIVE",
        "message": "Campaign resumed successfully",
        "resumed_at": datetime.now().isoformat()
    }