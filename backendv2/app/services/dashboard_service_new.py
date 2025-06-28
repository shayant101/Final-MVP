"""
New Dashboard Service with exact Momentum Orchestrator calculations
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import db


class DashboardServiceNew:
    """Service class for dashboard-related operations with exact Momentum Orchestrator calculations"""
    
    @staticmethod
    async def calculate_momentum_metrics_exact(restaurant_id: str) -> Dict[str, Any]:
        """Calculate marketing score and revenue potential exactly like MarketingFoundations.js"""
        try:
            # Get collection references
            checklist_status_collection = db.database.restaurant_checklist_status
            checklist_items_collection = db.database.checklist_items
            checklist_categories_collection = db.database.checklist_categories
            
            # Get all categories with their items
            categories = []
            async for category in checklist_categories_collection.find():
                # Get items for this category
                items = []
                async for item in checklist_items_collection.find({"category_id": category["_id"]}):
                    # Get status for this item and restaurant
                    status_doc = await checklist_status_collection.find_one({
                        "restaurant_id": ObjectId(restaurant_id),
                        "item_id": item["_id"]
                    })
                    
                    status = "completed" if status_doc and status_doc.get("is_completed") else "pending"
                    
                    items.append({
                        "title": item.get("title", ""),
                        "description": item.get("description", ""),
                        "is_critical": item.get("is_critical", False),
                        "status": status
                    })
                
                categories.append({
                    "type": category.get("type", ""),
                    "items": items
                })
            
            # Separate foundational and ongoing items exactly like MarketingFoundations.js
            foundational_items = []
            ongoing_items = []
            
            for category in categories:
                if category["type"] == "foundational":
                    foundational_items.extend(category["items"])
                elif category["type"] == "ongoing":
                    ongoing_items.extend(category["items"])
            
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
                revenue_category = DashboardServiceNew._get_revenue_category_exact(
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
    def _get_revenue_category_exact(title: str, description: str) -> str:
        """Map checklist items to revenue categories - EXACT match to MarketingFoundations.js getRevenueCategory (lines 307-327)"""
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