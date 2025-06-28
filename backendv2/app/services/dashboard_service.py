"""
Dashboard Service
Handles business logic for dashboard endpoints
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import db


class DashboardService:
    """Service class for dashboard-related operations"""
    
    @staticmethod
    async def get_restaurant_dashboard_data(restaurant_id: str) -> Dict[str, Any]:
        """Get dashboard data for a specific restaurant - matches Node.js /api/dashboard/restaurant"""
        try:
            # Get collection references
            users_collection = db.database.users
            campaigns_collection = db.database.campaigns
            checklist_collection = db.database.checklist_status
            
            # Get restaurant data - handle both ObjectId and string formats
            try:
                if isinstance(restaurant_id, str) and len(restaurant_id) == 24:
                    restaurant = await users_collection.find_one({"_id": ObjectId(restaurant_id)})
                else:
                    restaurant = await users_collection.find_one({"_id": restaurant_id})
            except Exception:
                # Fallback: try to find by user_id field or email
                restaurant = await users_collection.find_one({"user_id": restaurant_id})
                if not restaurant:
                    restaurant = await users_collection.find_one({"email": restaurant_id})
            
            if not restaurant:
                raise ValueError("Restaurant not found")
            
            # Get active campaigns (last 3) - handle empty collection
            try:
                active_campaigns = await campaigns_collection.find(
                    {"restaurant_id": restaurant_id, "status": "active"}
                ).sort("created_at", -1).limit(3).to_list(length=None)
            except Exception:
                active_campaigns = []
            
            # Get pending checklist items (top 3) - handle empty collection
            try:
                pending_tasks = await checklist_collection.find(
                    {"restaurant_id": restaurant_id, "is_complete": False}
                ).sort("created_at", 1).limit(3).to_list(length=None)
            except Exception:
                pending_tasks = []
            
            # Get campaign count for last 7 days - handle empty collection
            try:
                seven_days_ago = datetime.utcnow() - timedelta(days=7)
                recent_campaigns_count = await campaigns_collection.count_documents({
                    "restaurant_id": restaurant_id,
                    "created_at": {"$gte": seven_days_ago}
                })
            except Exception:
                recent_campaigns_count = 0
            
            # Format response to match Node.js structure
            return {
                "restaurant": {
                    "restaurant_id": restaurant_id,
                    "user_id": str(restaurant["_id"]),
                    "name": restaurant.get("restaurant_name", ""),
                    "address": restaurant.get("address", ""),
                    "phone": restaurant.get("phone", ""),
                    "created_at": restaurant.get("created_at", datetime.utcnow()).isoformat()
                },
                "performanceSnapshot": {
                    "newCustomersAcquired": restaurant.get("new_customers_acquired", 0) or (10 + int(restaurant_id[-1:], 16) % 40),  # Mock data
                    "customersReengaged": restaurant.get("customers_reengaged", 0) or (5 + int(restaurant_id[-1:], 16) % 25),  # Mock data
                    "period": "Last 7 Days"
                },
                "activeCampaigns": [
                    {
                        "campaign_id": str(campaign["_id"]),
                        "restaurant_id": campaign["restaurant_id"],
                        "campaign_type": campaign.get("campaign_type", "ad"),
                        "status": campaign.get("status", "active"),
                        "name": campaign.get("name", ""),
                        "details": campaign.get("details", ""),
                        "budget": campaign.get("budget", 0),
                        "created_at": campaign.get("created_at", datetime.utcnow()).isoformat(),
                        "updated_at": campaign.get("updated_at", datetime.utcnow()).isoformat()
                    }
                    for campaign in active_campaigns
                ],
                "pendingTasks": [
                    {
                        "status_id": str(task["_id"]),
                        "restaurant_id": task["restaurant_id"],
                        "checklist_item_name": task.get("checklist_item_name", ""),
                        "is_complete": task.get("is_complete", False),
                        "created_at": task.get("created_at", datetime.utcnow()).isoformat(),
                        "updated_at": task.get("updated_at", datetime.utcnow()).isoformat()
                    }
                    for task in pending_tasks
                ],
                "campaignStats": {
                    "recentCampaigns": recent_campaigns_count
                }
            }
            
        except Exception as e:
            import traceback
            print(f"🔍 DEBUG: Dashboard service error: {str(e)}")
            print(f"🔍 DEBUG: Restaurant ID: {restaurant_id}")
            print(f"🔍 DEBUG: Full traceback:")
            traceback.print_exc()
            raise Exception(f"Error fetching restaurant dashboard data: {str(e)}")
    
    @staticmethod
    async def get_admin_dashboard_data() -> Dict[str, Any]:
        """Get dashboard data for admin users - matches Node.js /api/dashboard/admin"""
        try:
            # Get collection references
            users_collection = db.database.users
            campaigns_collection = db.database.campaigns
            checklist_collection = db.database.checklist_status
            
            # Get total restaurants count
            total_restaurants = await users_collection.count_documents({"role": "restaurant"})
            
            # Get campaigns launched in last 7 days
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_campaigns = await campaigns_collection.count_documents({
                "created_at": {"$gte": seven_days_ago}
            })
            
            # Get restaurants with incomplete setup (those with pending checklist items)
            incomplete_setups_pipeline = [
                {"$match": {"is_complete": False}},
                {"$group": {"_id": "$restaurant_id"}},
                {"$count": "incomplete_setups"}
            ]
            incomplete_result = await checklist_collection.aggregate(incomplete_setups_pipeline).to_list(length=None)
            incomplete_setups = incomplete_result[0]["incomplete_setups"] if incomplete_result else 0
            
            return {
                "platformStats": {
                    "totalRestaurants": total_restaurants,
                    "recentCampaigns": recent_campaigns,
                    "period": "Last 7 Days"
                },
                "needsAttention": {
                    "incompleteSetups": incomplete_setups
                }
            }
            
        except Exception as e:
            raise Exception(f"Error fetching admin dashboard data: {str(e)}")
    
    @staticmethod
    async def get_all_restaurants(search: Optional[str] = None) -> Dict[str, Any]:
        """Get all restaurants for admin - matches Node.js /api/dashboard/restaurants"""
        try:
            # Get collection references
            users_collection = db.database.users
            
            # Build query
            query = {"role": "restaurant"}
            if search:
                query["restaurant_name"] = {"$regex": search, "$options": "i"}
            
            # Get restaurants
            restaurants = await users_collection.find(query).sort("created_at", -1).to_list(length=None)
            
            # Format response to match Node.js structure
            formatted_restaurants = [
                {
                    "restaurant_id": str(restaurant["_id"]),
                    "user_id": str(restaurant["_id"]),
                    "name": restaurant.get("restaurant_name", ""),
                    "address": restaurant.get("address", ""),
                    "phone": restaurant.get("phone", ""),
                    "email": restaurant.get("email", ""),
                    "signup_date": restaurant.get("created_at", datetime.utcnow()).isoformat(),
                    "created_at": restaurant.get("created_at", datetime.utcnow()).isoformat()
                }
                for restaurant in restaurants
            ]
            
            return {"restaurants": formatted_restaurants}
            
        except Exception as e:
            raise Exception(f"Error fetching restaurants: {str(e)}")
    
    @staticmethod
    async def get_restaurant_campaigns(restaurant_id: str) -> Dict[str, Any]:
        """Get campaigns for a restaurant - matches Node.js /api/dashboard/campaigns"""
        try:
            # Get collection references
            campaigns_collection = db.database.campaigns
            
            # Get all campaigns for this restaurant
            campaigns = await campaigns_collection.find(
                {"restaurant_id": restaurant_id}
            ).sort("created_at", -1).to_list(length=None)
            
            # Format response to match Node.js structure
            formatted_campaigns = [
                {
                    "campaign_id": str(campaign["_id"]),
                    "restaurant_id": campaign["restaurant_id"],
                    "campaign_type": campaign.get("campaign_type", "ad"),
                    "status": campaign.get("status", "draft"),
                    "name": campaign.get("name", ""),
                    "details": campaign.get("details", ""),
                    "budget": campaign.get("budget", 0),
                    "created_at": campaign.get("created_at", datetime.utcnow()).isoformat(),
                    "updated_at": campaign.get("updated_at", datetime.utcnow()).isoformat()
                }
                for campaign in campaigns
            ]
            
            return {"campaigns": formatted_campaigns}
            
        except Exception as e:
            raise Exception(f"Error fetching restaurant campaigns: {str(e)}")
    
    @staticmethod
    async def update_checklist_item(item_id: str, restaurant_id: str, is_complete: bool) -> Dict[str, Any]:
        """Update checklist item - matches Node.js PUT /api/dashboard/checklist/:itemId"""
        try:
            # Get collection references
            checklist_collection = db.database.checklist_status
            
            # Verify the checklist item belongs to this restaurant
            item = await checklist_collection.find_one({
                "_id": ObjectId(item_id),
                "restaurant_id": restaurant_id
            })
            
            if not item:
                raise ValueError("Checklist item not found")
            
            # Update the item
            result = await checklist_collection.update_one(
                {"_id": ObjectId(item_id)},
                {
                    "$set": {
                        "is_complete": is_complete,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise ValueError("Failed to update checklist item")
            
            return {"message": "Checklist item updated successfully"}
            
        except Exception as e:
            raise Exception(f"Error updating checklist item: {str(e)}")