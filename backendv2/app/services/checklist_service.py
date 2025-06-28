from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from app.database import get_database
from app.models import TokenData, UserRole, ChecklistType, ChecklistStatus
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChecklistService:
    def __init__(self):
        self.db = get_database()
        self.categories_collection = self.db.checklist_categories
        self.items_collection = self.db.checklist_items
        self.status_collection = self.db.restaurant_checklist_status
        self.restaurants_collection = self.db.restaurants

    async def verify_restaurant_access(self, user: TokenData, restaurant_id: str) -> None:
        """Verify that the user has access to the specified restaurant"""
        if user.role == UserRole.admin:
            # Admins can access any restaurant
            return
        
        if user.role == UserRole.restaurant:
            # Restaurant users can only access their own restaurant
            # In our system, for restaurant users, user_id IS the restaurant_id
            if user.user_id == restaurant_id:
                return
            # Or if they're impersonating (admin feature)
            if user.impersonating_restaurant_id == restaurant_id:
                return
        
        raise HTTPException(
            status_code=403,
            detail="Access denied to this restaurant"
        )

    async def get_categories(self, type_filter: Optional[ChecklistType] = None) -> List[Dict[str, Any]]:
        """Get all checklist categories with optional type filter"""
        try:
            query = {}
            if type_filter:
                query["type"] = type_filter.value
            
            cursor = self.categories_collection.find(query).sort("order_in_list", 1)
            categories = []
            
            async for category in cursor:
                categories.append({
                    "category_id": str(category["_id"]),
                    "name": category["name"],
                    "description": category.get("description"),
                    "icon": category.get("icon"),
                    "type": category["type"],
                    "order_in_list": category["order_in_list"],
                    "created_at": category.get("created_at", datetime.utcnow())
                })
            
            return categories
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise

    async def get_category_items(self, category_id: str) -> List[Dict[str, Any]]:
        """Get all items for a specific category"""
        try:
            if not ObjectId.is_valid(category_id):
                raise HTTPException(status_code=400, detail="Invalid category ID")
            
            cursor = self.items_collection.find({
                "category_id": ObjectId(category_id)
            }).sort("order_in_category", 1)
            
            items = []
            async for item in cursor:
                items.append({
                    "item_id": str(item["_id"]),
                    "category_id": str(item["category_id"]),
                    "parent_item_id": str(item["parent_item_id"]) if item.get("parent_item_id") else None,
                    "title": item["title"],
                    "description": item.get("description"),
                    "guidance_link": item.get("guidance_link"),
                    "order_in_category": item["order_in_category"],
                    "is_critical": item.get("is_critical", False),
                    "created_at": item.get("created_at", datetime.utcnow())
                })
            
            return items
        except Exception as e:
            logger.error(f"Error fetching items for category {category_id}: {str(e)}")
            raise

    async def get_restaurant_status(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get checklist status for a specific restaurant"""
        try:
            if not ObjectId.is_valid(restaurant_id):
                raise HTTPException(status_code=400, detail="Invalid restaurant ID")
            
            # Use aggregation to join status with items and categories
            pipeline = [
                {
                    "$match": {
                        "restaurant_id": ObjectId(restaurant_id)
                    }
                },
                {
                    "$lookup": {
                        "from": "checklist_items",
                        "localField": "item_id",
                        "foreignField": "_id",
                        "as": "item"
                    }
                },
                {
                    "$unwind": "$item"
                },
                {
                    "$lookup": {
                        "from": "checklist_categories",
                        "localField": "item.category_id",
                        "foreignField": "_id",
                        "as": "category"
                    }
                },
                {
                    "$unwind": "$category"
                }
            ]
            
            cursor = self.status_collection.aggregate(pipeline)
            statuses = []
            
            async for status in cursor:
                statuses.append({
                    "status_id": str(status["_id"]),
                    "restaurant_id": str(status["restaurant_id"]),
                    "item_id": str(status["item_id"]),
                    "status": status["status"],
                    "notes": status.get("notes"),
                    "last_updated_at": status["last_updated_at"],
                    "title": status["item"]["title"],
                    "category_id": str(status["item"]["category_id"]),
                    "category_name": status["category"]["name"],
                    "category_type": status["category"]["type"]
                })
            
            return statuses
        except Exception as e:
            logger.error(f"Error fetching status for restaurant {restaurant_id}: {str(e)}")
            raise

    async def update_item_status(
        self, 
        restaurant_id: str, 
        item_id: str, 
        status: ChecklistStatus, 
        notes: Optional[str] = None
    ) -> str:
        """Update the status of a checklist item for a restaurant"""
        try:
            if not ObjectId.is_valid(restaurant_id):
                raise HTTPException(status_code=400, detail="Invalid restaurant ID")
            if not ObjectId.is_valid(item_id):
                raise HTTPException(status_code=400, detail="Invalid item ID")
            
            # Verify the item exists
            item = await self.items_collection.find_one({"_id": ObjectId(item_id)})
            if not item:
                raise HTTPException(status_code=404, detail="Checklist item not found")
            
            # Update or insert status
            update_data = {
                "restaurant_id": ObjectId(restaurant_id),
                "item_id": ObjectId(item_id),
                "status": status.value,
                "notes": notes,
                "last_updated_at": datetime.utcnow()
            }
            
            result = await self.status_collection.update_one(
                {
                    "restaurant_id": ObjectId(restaurant_id),
                    "item_id": ObjectId(item_id)
                },
                {"$set": update_data},
                upsert=True
            )
            
            if result.upserted_id:
                return str(result.upserted_id)
            else:
                # Find the existing document to return its ID
                existing = await self.status_collection.find_one({
                    "restaurant_id": ObjectId(restaurant_id),
                    "item_id": ObjectId(item_id)
                })
                return str(existing["_id"]) if existing else ""
                
        except Exception as e:
            logger.error(f"Error updating status for restaurant {restaurant_id}, item {item_id}: {str(e)}")
            raise

    async def get_restaurant_progress(
        self, 
        restaurant_id: str, 
        type_filter: Optional[ChecklistType] = None
    ) -> Dict[str, Any]:
        """Get progress statistics for a restaurant's checklist"""
        try:
            if not ObjectId.is_valid(restaurant_id):
                raise HTTPException(status_code=400, detail="Invalid restaurant ID")
            
            # Build aggregation pipeline
            match_stage = {}
            if type_filter:
                match_stage["type"] = type_filter.value
            
            pipeline = [
                {
                    "$match": match_stage
                },
                {
                    "$lookup": {
                        "from": "checklist_items",
                        "localField": "_id",
                        "foreignField": "category_id",
                        "as": "items"
                    }
                },
                {
                    "$unwind": "$items"
                },
                {
                    "$lookup": {
                        "from": "restaurant_checklist_status",
                        "let": {
                            "item_id": "$items._id",
                            "restaurant_id": ObjectId(restaurant_id)
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$item_id", "$$item_id"]},
                                            {"$eq": ["$restaurant_id", "$$restaurant_id"]}
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "status"
                    }
                },
                {
                    "$group": {
                        "_id": "$type",
                        "total_items": {"$sum": 1},
                        "completed_items": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$and": [
                                            {"$ne": ["$status", []]},
                                            {"$eq": [{"$arrayElemAt": ["$status.status", 0]}, "completed"]}
                                        ]
                                    },
                                    1,
                                    0
                                ]
                            }
                        },
                        "critical_items": {
                            "$sum": {
                                "$cond": ["$items.is_critical", 1, 0]
                            }
                        },
                        "completed_critical_items": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$and": [
                                            "$items.is_critical",
                                            {"$ne": ["$status", []]},
                                            {"$eq": [{"$arrayElemAt": ["$status.status", 0]}, "completed"]}
                                        ]
                                    },
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                }
            ]
            
            cursor = self.categories_collection.aggregate(pipeline)
            progress = {}
            
            async for result in cursor:
                completion_percentage = 0
                if result["total_items"] > 0:
                    completion_percentage = round((result["completed_items"] / result["total_items"]) * 100)
                
                critical_completion_percentage = 0
                if result["critical_items"] > 0:
                    critical_completion_percentage = round(
                        (result["completed_critical_items"] / result["critical_items"]) * 100
                    )
                
                progress[result["_id"]] = {
                    "totalItems": result["total_items"],
                    "completedItems": result["completed_items"],
                    "completionPercentage": completion_percentage,
                    "criticalItems": result["critical_items"],
                    "completedCriticalItems": result["completed_critical_items"],
                    "criticalCompletionPercentage": critical_completion_percentage
                }
            
            return progress
        except Exception as e:
            logger.error(f"Error calculating progress for restaurant {restaurant_id}: {str(e)}")
            raise

    async def get_categories_with_items(
        self, 
        type_filter: Optional[ChecklistType] = None,
        restaurant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all categories with their items, optionally including status for a specific restaurant"""
        try:
            # Get categories
            categories = await self.get_categories(type_filter)
            
            # For each category, get items with optional status
            for category in categories:
                category_id = category["category_id"]
                
                # Get items for this category
                items = await self.get_category_items(category_id)
                
                # If restaurant_id is provided, get status for each item
                if restaurant_id and ObjectId.is_valid(restaurant_id):
                    for item in items:
                        item_id = item["item_id"]
                        
                        # Get status for this item and restaurant
                        status_doc = await self.status_collection.find_one({
                            "restaurant_id": ObjectId(restaurant_id),
                            "item_id": ObjectId(item_id)
                        })
                        
                        if status_doc:
                            item["status"] = status_doc["status"]
                            item["notes"] = status_doc.get("notes")
                            item["status_updated_at"] = status_doc["last_updated_at"]
                        else:
                            item["status"] = None
                            item["notes"] = None
                            item["status_updated_at"] = None
                
                category["items"] = items
            
            return categories
        except Exception as e:
            logger.error(f"Error fetching categories with items: {str(e)}")
            raise