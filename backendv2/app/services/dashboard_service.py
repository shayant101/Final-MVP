"""
Dashboard Service
Handles business logic for dashboard endpoints
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import db


class DashboardService:
    """Service class for dashboard-related operations"""
    
    @staticmethod
    async def get_restaurant_dashboard_data(restaurant_id: str) -> Dict[str, Any]:
        """Get dashboard data for a specific restaurant - OPTIMIZED for performance"""
        try:
            # Get collection references
            users_collection = db.database.users
            restaurants_collection = db.database.restaurants
            campaigns_collection = db.database.campaigns
            checklist_collection = db.database.checklist_status
            
            # Use parallel queries to fetch data simultaneously
            restaurant_task = None
            user_task = None
            
            # Optimize restaurant/user lookup
            if isinstance(restaurant_id, str) and len(restaurant_id) == 24:
                restaurant_task = restaurants_collection.find_one({"_id": ObjectId(restaurant_id)})
            
            # Execute restaurant lookup
            restaurant_doc = await restaurant_task if restaurant_task else None
            
            if restaurant_doc:
                # Found restaurant, get the corresponding user
                user_id = restaurant_doc.get("user_id")
                if user_id:
                    user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
                else:
                    user_doc = None
            else:
                # Fallback: try to find user directly
                try:
                    user_doc = await users_collection.find_one({"_id": ObjectId(restaurant_id)})
                    if user_doc and user_doc.get("role") == "restaurant":
                        restaurant_doc = await restaurants_collection.find_one({"user_id": str(user_doc["_id"])})
                except Exception:
                    user_doc = await users_collection.find_one({"user_id": restaurant_id})
                    if user_doc:
                        restaurant_doc = await restaurants_collection.find_one({"user_id": restaurant_id})
            
            if not restaurant_doc or not user_doc:
                raise ValueError("Restaurant not found")
            
            # Execute all remaining queries in parallel for better performance
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            # Create all query tasks
            active_campaigns_task = campaigns_collection.find(
                {"restaurant_id": restaurant_id, "status": "active"}
            ).sort("created_at", -1).limit(3).to_list(length=None)
            
            pending_tasks_task = checklist_collection.find(
                {"restaurant_id": restaurant_id, "is_complete": False}
            ).sort("created_at", 1).limit(3).to_list(length=None)
            
            recent_campaigns_count_task = campaigns_collection.count_documents({
                "restaurant_id": restaurant_id,
                "created_at": {"$gte": seven_days_ago}
            })
            
            # Execute momentum metrics calculation in parallel
            momentum_metrics_task = DashboardService._calculate_momentum_metrics_exact(restaurant_id)
            
            # Wait for all queries to complete
            try:
                active_campaigns, pending_tasks, recent_campaigns_count, momentum_metrics = await asyncio.gather(
                    active_campaigns_task,
                    pending_tasks_task,
                    recent_campaigns_count_task,
                    momentum_metrics_task,
                    return_exceptions=True
                )
                
                # Handle any exceptions from parallel execution
                if isinstance(active_campaigns, Exception):
                    active_campaigns = []
                if isinstance(pending_tasks, Exception):
                    pending_tasks = []
                if isinstance(recent_campaigns_count, Exception):
                    recent_campaigns_count = 0
                if isinstance(momentum_metrics, Exception):
                    momentum_metrics = {
                        "marketingScore": 0,
                        "weeklyRevenuePotential": 0,
                        "completedRevenue": 0,
                        "totalPotential": 0,
                        "foundationalProgress": {"completed": 0, "total": 0, "percentage": 0},
                        "ongoingProgress": {"completed": 0, "total": 0, "percentage": 0}
                    }
                    
            except Exception as e:
                print(f"🔍 DEBUG: Error in parallel queries: {str(e)}")
                active_campaigns = []
                pending_tasks = []
                recent_campaigns_count = 0
                momentum_metrics = {
                    "marketingScore": 0,
                    "weeklyRevenuePotential": 0,
                    "completedRevenue": 0,
                    "totalPotential": 0,
                    "foundationalProgress": {"completed": 0, "total": 0, "percentage": 0},
                    "ongoingProgress": {"completed": 0, "total": 0, "percentage": 0}
                }
            
            # Format response to match Node.js structure
            return {
                "restaurant": {
                    "restaurant_id": restaurant_id,
                    "user_id": str(user_doc["_id"]),
                    "name": restaurant_doc.get("name", ""),
                    "address": restaurant_doc.get("address", ""),
                    "phone": restaurant_doc.get("phone", ""),
                    "created_at": restaurant_doc.get("created_at", datetime.utcnow()).isoformat()
                },
                "performanceSnapshot": {
                    "newCustomersAcquired": restaurant_doc.get("new_customers_acquired", 0) or (10 + int(restaurant_id[-1:], 16) % 40),  # Mock data
                    "customersReengaged": restaurant_doc.get("customers_reengaged", 0) or (5 + int(restaurant_id[-1:], 16) % 25),  # Mock data
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
                },
                "momentumMetrics": await DashboardService._calculate_momentum_metrics_exact(restaurant_id)
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
            restaurants_collection = db.database.restaurants
            
            # Build aggregation pipeline to join users and restaurants
            pipeline = [
                # Match restaurant users
                {"$match": {"role": "restaurant"}},
                # Add string version of _id for join
                {
                    "$addFields": {
                        "user_id_string": {"$toString": "$_id"}
                    }
                },
                # Join with restaurants collection using string user_id
                {
                    "$lookup": {
                        "from": "restaurants",
                        "localField": "user_id_string",
                        "foreignField": "user_id",
                        "as": "restaurant_info"
                    }
                },
                # Unwind restaurant info (should be 1-to-1)
                {"$unwind": {"path": "$restaurant_info", "preserveNullAndEmptyArrays": True}},
                # Sort by creation date
                {"$sort": {"created_at": -1}}
            ]
            
            # Add search filter if provided
            if search:
                pipeline.insert(1, {
                    "$match": {
                        "$or": [
                            {"restaurant_info.name": {"$regex": search, "$options": "i"}},
                            {"email": {"$regex": search, "$options": "i"}}
                        ]
                    }
                })
            
            # Execute aggregation
            results = await users_collection.aggregate(pipeline).to_list(length=None)
            
            # Format response to match Node.js structure
            formatted_restaurants = []
            for result in results:
                restaurant_info = result.get("restaurant_info", {})
                formatted_restaurants.append({
                    "restaurant_id": str(restaurant_info.get("_id", result["_id"])),  # Use actual restaurant ID
                    "user_id": str(result["_id"]),  # User ID
                    "name": restaurant_info.get("name", ""),  # Restaurant name from restaurants collection
                    "address": restaurant_info.get("address", ""),
                    "phone": restaurant_info.get("phone", ""),
                    "email": result.get("email", ""),  # Email from users collection
                    "signup_date": result.get("created_at", datetime.utcnow()).isoformat(),
                    "created_at": result.get("created_at", datetime.utcnow()).isoformat()
                })
            
            return {"restaurants": formatted_restaurants}
            
        except Exception as e:
            print(f"🔍 DEBUG: Error in get_all_restaurants: {str(e)}")
            import traceback
            traceback.print_exc()
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
    
    @staticmethod
    async def _calculate_momentum_metrics_exact(restaurant_id: str) -> Dict[str, Any]:
        """Calculate marketing score and revenue potential exactly like MarketingFoundations.js - SIMPLIFIED"""
        try:
            # Get collection references
            checklist_status_collection = db.database.restaurant_checklist_status
            checklist_items_collection = db.database.checklist_items
            checklist_categories_collection = db.database.checklist_categories
            
            # Use simple, fast queries instead of complex aggregation
            # Get all categories
            categories_dict = {}
            async for category in checklist_categories_collection.find():
                categories_dict[category["_id"]] = {
                    "type": category.get("type", ""),
                    "items": []
                }
            
            # Get all items
            items_by_category = {}
            async for item in checklist_items_collection.find():
                category_id = item["category_id"]
                if category_id not in items_by_category:
                    items_by_category[category_id] = []
                items_by_category[category_id].append({
                    "id": item["_id"],
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "is_critical": item.get("is_critical", False)
                })
            
            # Get all status records for this restaurant
            status_dict = {}
            async for status in checklist_status_collection.find({"restaurant_id": ObjectId(restaurant_id)}):
                status_dict[status["item_id"]] = status.get("status") == "completed"
            
            # Combine data efficiently
            foundational_items = []
            ongoing_items = []
            
            for category_id, category_data in categories_dict.items():
                category_type = category_data["type"]
                items = items_by_category.get(category_id, [])
                
                for item in items:
                    item_data = {
                        "title": item["title"],
                        "description": item["description"],
                        "is_critical": item["is_critical"],
                        "status": "completed" if status_dict.get(item["id"], False) else "pending"
                    }
                    
                    if category_type == "foundational":
                        foundational_items.append(item_data)
                    elif category_type == "ongoing":
                        ongoing_items.append(item_data)
            
            # Calculate progress exactly like getOverallProgress() in MarketingFoundations.js
            foundational_total = len(foundational_items)
            foundational_completed = len([item for item in foundational_items if item["status"] == "completed"])
            foundational_critical = [item for item in foundational_items if item["is_critical"]]
            foundational_critical_total = len(foundational_critical)
            foundational_critical_completed = len([item for item in foundational_critical if item["status"] == "completed"])
            
            ongoing_total = len(ongoing_items)
            ongoing_completed = len([item for item in ongoing_items if item["status"] == "completed"])
            
            # Calculate marketing score using EXACT algorithm from calculateOverallScore() (lines 204-228)
            foundational_weight = 0.7
            ongoing_weight = 0.3
            critical_bonus = 0.1
            
            foundational_base_score = (foundational_completed / max(foundational_total, 1)) * 100
            critical_score = (foundational_critical_completed / max(foundational_critical_total, 1)) * 100
            foundational_score = (foundational_base_score * (1 - critical_bonus)) + (critical_score * critical_bonus)
            
            ongoing_score = (ongoing_completed / max(ongoing_total, 1)) * 100
            
            marketing_score = (foundational_score * foundational_weight) + (ongoing_score * ongoing_weight)
            marketing_score = round(min(marketing_score, 100))
            
            # Calculate revenue impact using EXACT algorithm from calculateRevenueImpact() (lines 241-304)
            revenue_impacts = {
                'google_business_optimization': 450,
                'google_reviews_management': 320,
                'social_media_posting': 280,
                'social_media_advertising': 680,
                'online_ordering_setup': 890,
                'menu_optimization': 340,
                'upselling_strategies': 520,
                'email_campaigns': 380,
                'promotional_campaigns': 450,
                'loyalty_program': 420,
                'rewards_system': 290,
                'facebook_advertising': 720,
                'google_ads': 650,
                'promotional_offers': 380,
                'customer_feedback': 180,
                'review_management': 220,
            }
            
            total_potential = 0
            completed_revenue = 0
            
            # Process all items (both foundational and ongoing) exactly like the frontend
            all_items = foundational_items + ongoing_items
            
            for item in all_items:
                # Map item to revenue category using EXACT logic from getRevenueCategory
                revenue_category = DashboardService._get_revenue_category_exact(
                    item["title"],
                    item["description"]
                )
                impact = revenue_impacts.get(revenue_category, 0)
                
                total_potential += impact
                if item["status"] == "completed":
                    completed_revenue += impact
            
            # Calculate remaining potential exactly like the frontend
            weekly_revenue_potential = max(0, total_potential - completed_revenue)
            
            return {
                "marketingScore": marketing_score,
                "weeklyRevenuePotential": round(weekly_revenue_potential),
                "completedRevenue": round(completed_revenue),
                "totalPotential": round(total_potential),
                "foundationalProgress": {
                    "completed": foundational_completed,
                    "total": foundational_total,
                    "percentage": round((foundational_completed / max(foundational_total, 1)) * 100)
                },
                "ongoingProgress": {
                    "completed": ongoing_completed,
                    "total": ongoing_total,
                    "percentage": round((ongoing_completed / max(ongoing_total, 1)) * 100)
                }
            }
            
        except Exception as e:
            print(f"🔍 DEBUG: Error calculating momentum metrics: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return default values if calculation fails
            return {
                "marketingScore": 0,
                "weeklyRevenuePotential": 0,
                "completedRevenue": 0,
                "totalPotential": 0,
                "foundationalProgress": {"completed": 0, "total": 0, "percentage": 0},
                "ongoingProgress": {"completed": 0, "total": 0, "percentage": 0}
            }

    @staticmethod
    async def _calculate_momentum_metrics(restaurant_id: str) -> Dict[str, Any]:
        """Calculate marketing score and revenue potential for a restaurant"""
        try:
            # Get collection references
            checklist_status_collection = db.database.restaurant_checklist_status
            checklist_items_collection = db.database.checklist_items
            checklist_categories_collection = db.database.checklist_categories
            
            # Get all checklist items with their completion status for this restaurant
            pipeline = [
                # Match items for this restaurant
                {"$match": {"restaurant_id": ObjectId(restaurant_id)}},
                # Join with checklist_items to get item details
                {
                    "$lookup": {
                        "from": "checklist_items",
                        "localField": "item_id",
                        "foreignField": "_id",
                        "as": "item_details"
                    }
                },
                # Unwind item details
                {"$unwind": {"path": "$item_details", "preserveNullAndEmptyArrays": True}},
                # Join with categories to get category type
                {
                    "$lookup": {
                        "from": "checklist_categories",
                        "localField": "item_details.category_id",
                        "foreignField": "_id",
                        "as": "category_details"
                    }
                },
                # Unwind category details
                {"$unwind": {"path": "$category_details", "preserveNullAndEmptyArrays": True}},
                # Project needed fields
                {
                    "$project": {
                        "is_completed": 1,
                        "item_type": "$category_details.type",
                        "is_critical": "$item_details.is_critical",
                        "title": "$item_details.title",
                        "description": "$item_details.description"
                    }
                }
            ]
            
            checklist_data = await checklist_status_collection.aggregate(pipeline).to_list(length=None)
            
            # Calculate marketing score using the same algorithm as MarketingFoundations.js
            foundational_items = [item for item in checklist_data if item.get("item_type") == "foundational"]
            ongoing_items = [item for item in checklist_data if item.get("item_type") == "ongoing"]
            
            # Calculate foundational progress
            foundational_total = len(foundational_items)
            foundational_completed = len([item for item in foundational_items if item.get("is_completed")])
            foundational_critical = [item for item in foundational_items if item.get("is_critical") == True]
            foundational_critical_total = len(foundational_critical)
            foundational_critical_completed = len([item for item in foundational_critical if item.get("is_completed")])
            
            # Calculate ongoing progress
            ongoing_total = len(ongoing_items)
            ongoing_completed = len([item for item in ongoing_items if item.get("is_completed")])
            
            # Calculate weighted marketing score (same algorithm as frontend)
            foundational_weight = 0.7
            ongoing_weight = 0.3
            critical_bonus = 0.1
            
            foundational_base_score = (foundational_completed / max(foundational_total, 1)) * 100
            critical_score = (foundational_critical_completed / max(foundational_critical_total, 1)) * 100
            foundational_score = (foundational_base_score * (1 - critical_bonus)) + (critical_score * critical_bonus)
            
            ongoing_score = (ongoing_completed / max(ongoing_total, 1)) * 100
            
            marketing_score = (foundational_score * foundational_weight) + (ongoing_score * ongoing_weight)
            marketing_score = min(round(marketing_score), 100)
            
            # Calculate revenue potential using similar logic as MarketingFoundations.js
            revenue_impacts = {
                'google_business_optimization': 450,
                'google_reviews_management': 320,
                'social_media_posting': 280,
                'social_media_advertising': 680,
                'online_ordering_setup': 890,
                'menu_optimization': 340,
                'upselling_strategies': 520,
                'email_campaigns': 380,
                'promotional_campaigns': 450,
                'loyalty_program': 420,
                'rewards_system': 290,
                'facebook_advertising': 720,
                'google_ads': 650,
                'promotional_offers': 380,
                'customer_feedback': 180,
                'review_management': 220,
            }
            
            total_potential = 0
            completed_revenue = 0
            
            for item in checklist_data:
                # Map item to revenue category
                revenue_category = DashboardService._get_revenue_category(
                    item.get("title", ""),
                    item.get("description", "")
                )
                impact = revenue_impacts.get(revenue_category, 0)
                
                total_potential += impact
                if item.get("is_completed"):
                    completed_revenue += impact
            
            weekly_revenue_potential = max(0, total_potential - completed_revenue)
            
            return {
                "marketingScore": marketing_score,
                "weeklyRevenuePotential": round(weekly_revenue_potential),
                "completedRevenue": round(completed_revenue),
                "totalPotential": round(total_potential),
                "foundationalProgress": {
                    "completed": foundational_completed,
                    "total": foundational_total,
                    "percentage": round((foundational_completed / max(foundational_total, 1)) * 100)
                },
                "ongoingProgress": {
                    "completed": ongoing_completed,
                    "total": ongoing_total,
                    "percentage": round((ongoing_completed / max(ongoing_total, 1)) * 100)
                }
            }
            
        except Exception as e:
            print(f"🔍 DEBUG: Error calculating momentum metrics: {str(e)}")
            # Return default values if calculation fails
            return {
                "marketingScore": 0,
                "weeklyRevenuePotential": 0,
                "completedRevenue": 0,
                "totalPotential": 0,
                "foundationalProgress": {"completed": 0, "total": 0, "percentage": 0},
                "ongoingProgress": {"completed": 0, "total": 0, "percentage": 0}
            }
    
    @staticmethod
    def _get_revenue_category_exact(title: str, description: str) -> str:
        """Map checklist items to revenue categories - EXACT match to MarketingFoundations.js getRevenueCategory"""
        text = (title + ' ' + description).lower()
        
        if 'google business' in text or 'gbp' in text:
            return 'google_business_optimization'
        if 'review' in text and 'google' in text:
            return 'google_reviews_management'
        if 'social media' in text and 'post' in text:
            return 'social_media_posting'
        if 'facebook' in text and 'ad' in text:
            return 'facebook_advertising'
        if 'google' in text and 'ad' in text:
            return 'google_ads'
        if 'online ordering' in text or 'delivery' in text:
            return 'online_ordering_setup'
        if 'menu' in text and ('optim' in text or 'updat' in text):
            return 'menu_optimization'
        if 'upsell' in text or 'cross-sell' in text:
            return 'upselling_strategies'
        if 'email' in text and 'campaign' in text:
            return 'email_campaigns'
        if 'promotion' in text or 'offer' in text:
            return 'promotional_campaigns'
        if 'loyalty' in text or 'reward' in text:
            return 'loyalty_program'
        if 'social media' in text and 'ad' in text:
            return 'social_media_advertising'
        if 'feedback' in text or 'survey' in text:
            return 'customer_feedback'
        if 'review' in text and not 'google' in text:
            return 'review_management'
        
        # Default for foundational items
        return 'google_business_optimization'

    @staticmethod
    def _get_revenue_category(title: str, description: str) -> str:
        """Map checklist items to revenue categories - matches MarketingFoundations.js logic"""
        return DashboardService._get_revenue_category_exact(title, description)