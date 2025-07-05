"""
Admin Analytics Service
Provides analytics data collection and aggregation for the enhanced admin dashboard
"""
import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from ..database import get_database

logger = logging.getLogger(__name__)

class AdminAnalyticsService:
    def __init__(self):
        self.db = None
        
    async def get_db(self):
        """Get database connection"""
        if self.db is None:
            self.db = get_database()
        return self.db

    async def log_ai_usage(self, restaurant_id: str, feature_type: str, 
                          operation_type: str, processing_time: int, 
                          tokens_used: int = 0, status: str = "success", 
                          metadata: Dict[str, Any] = None) -> bool:
        """
        Log AI feature usage for analytics (non-blocking)
        """
        try:
            db = await self.get_db()
            
            analytics_doc = {
                "analytics_id": str(uuid.uuid4()),
                "restaurant_id": restaurant_id,
                "feature_type": feature_type,
                "operation_type": operation_type,
                "timestamp": datetime.utcnow(),
                "processing_time_ms": processing_time,
                "tokens_used": tokens_used,
                "estimated_cost": self._calculate_cost(tokens_used, feature_type),
                "status": status,
                "metadata": metadata or {},
                "created_at": datetime.utcnow()
            }
            
            # Insert analytics data (non-blocking)
            await db.ai_usage_analytics.insert_one(analytics_doc)
            
            logger.info(f"Logged AI usage: {feature_type}/{operation_type} for restaurant {restaurant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log AI usage: {str(e)}")
            return False

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics for admin dashboard"""
        try:
            db = await self.get_db()
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Get today's metrics
            pipeline = [
                {"$match": {"timestamp": {"$gte": today_start}}},
                {"$group": {
                    "_id": None,
                    "total_requests": {"$sum": 1},
                    "successful_requests": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                    "failed_requests": {"$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}},
                    "avg_processing_time": {"$avg": "$processing_time_ms"},
                    "total_cost": {"$sum": "$estimated_cost"}
                }}
            ]
            
            result = await db.ai_usage_analytics.aggregate(pipeline).to_list(1)
            metrics = result[0] if result else {}
            
            total_requests = metrics.get("total_requests", 0)
            successful_requests = metrics.get("successful_requests", 0)
            
            return {
                "today_requests": total_requests,
                "success_rate": round((successful_requests / max(total_requests, 1)) * 100, 2),
                "avg_response_time": round(metrics.get("avg_processing_time", 0)),
                "daily_cost": round(metrics.get("total_cost", 0), 4),
                "active_requests": await self._get_active_requests_count(),
                "last_updated": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {str(e)}")
            return {
                "today_requests": 0,
                "success_rate": 0,
                "avg_response_time": 0,
                "daily_cost": 0,
                "active_requests": 0,
                "last_updated": datetime.utcnow().isoformat()
            }

    async def get_usage_analytics(self, date_range: Tuple[datetime, datetime], 
                                 feature_type: str = None) -> Dict[str, Any]:
        """Get detailed usage analytics with filtering"""
        try:
            db = await self.get_db()
            start_date, end_date = date_range
            
            match_filter = {"timestamp": {"$gte": start_date, "$lte": end_date}}
            if feature_type:
                match_filter["feature_type"] = feature_type
            
            # Usage over time
            usage_pipeline = [
                {"$match": match_filter},
                {"$group": {
                    "_id": {
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                        "feature_type": "$feature_type"
                    },
                    "requests": {"$sum": 1},
                    "cost": {"$sum": "$estimated_cost"}
                }},
                {"$sort": {"_id.date": 1}}
            ]
            
            # Feature breakdown
            feature_pipeline = [
                {"$match": match_filter},
                {"$group": {
                    "_id": "$feature_type",
                    "requests": {"$sum": 1},
                    "cost": {"$sum": "$estimated_cost"},
                    "avg_processing_time": {"$avg": "$processing_time_ms"}
                }}
            ]
            
            # Error analysis
            error_pipeline = [
                {"$match": {**match_filter, "status": "error"}},
                {"$group": {
                    "_id": "$feature_type",
                    "error_count": {"$sum": 1},
                    "error_types": {"$push": "$metadata.error_details"}
                }}
            ]
            
            # Execute all pipelines concurrently
            usage_data, feature_data, error_data = await asyncio.gather(
                db.ai_usage_analytics.aggregate(usage_pipeline).to_list(None),
                db.ai_usage_analytics.aggregate(feature_pipeline).to_list(None),
                db.ai_usage_analytics.aggregate(error_pipeline).to_list(None)
            )
            
            return {
                "usage_over_time": usage_data,
                "feature_breakdown": feature_data,
                "error_analysis": error_data,
                "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()}
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage analytics: {str(e)}")
            return {
                "usage_over_time": [],
                "feature_breakdown": [],
                "error_analysis": [],
                "date_range": {"start": date_range[0].isoformat(), "end": date_range[1].isoformat()}
            }

    async def get_restaurant_analytics(self, restaurant_id: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a specific restaurant"""
        try:
            db = await self.get_db()
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            match_filter = {
                "restaurant_id": restaurant_id,
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }
            
            # Restaurant usage summary
            summary_pipeline = [
                {"$match": match_filter},
                {"$group": {
                    "_id": None,
                    "total_requests": {"$sum": 1},
                    "successful_requests": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                    "total_cost": {"$sum": "$estimated_cost"},
                    "avg_processing_time": {"$avg": "$processing_time_ms"}
                }}
            ]
            
            # Feature usage breakdown
            feature_pipeline = [
                {"$match": match_filter},
                {"$group": {
                    "_id": "$feature_type",
                    "requests": {"$sum": 1},
                    "cost": {"$sum": "$estimated_cost"}
                }}
            ]
            
            # Daily usage trend
            daily_pipeline = [
                {"$match": match_filter},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "requests": {"$sum": 1},
                    "cost": {"$sum": "$estimated_cost"}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            summary_data, feature_data, daily_data = await asyncio.gather(
                db.ai_usage_analytics.aggregate(summary_pipeline).to_list(1),
                db.ai_usage_analytics.aggregate(feature_pipeline).to_list(None),
                db.ai_usage_analytics.aggregate(daily_pipeline).to_list(None)
            )
            
            summary = summary_data[0] if summary_data else {}
            
            return {
                "restaurant_id": restaurant_id,
                "period_days": days,
                "summary": {
                    "total_requests": summary.get("total_requests", 0),
                    "success_rate": round((summary.get("successful_requests", 0) / max(summary.get("total_requests", 1), 1)) * 100, 2),
                    "total_cost": round(summary.get("total_cost", 0), 4),
                    "avg_processing_time": round(summary.get("avg_processing_time", 0))
                },
                "feature_breakdown": feature_data,
                "daily_usage": daily_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get restaurant analytics: {str(e)}")
            return {
                "restaurant_id": restaurant_id,
                "period_days": days,
                "summary": {"total_requests": 0, "success_rate": 0, "total_cost": 0, "avg_processing_time": 0},
                "feature_breakdown": [],
                "daily_usage": []
            }

    async def flag_content_for_moderation(self, restaurant_id: str, content_type: str, 
                                        content_data: Dict[str, Any], flags: List[str]) -> str:
        """Flag content for moderation review"""
        try:
            db = await self.get_db()
            
            moderation_doc = {
                "moderation_id": str(uuid.uuid4()),
                "restaurant_id": restaurant_id,
                "content_type": content_type,
                "content_id": content_data.get("content_id"),
                "status": "flagged",
                "content_data": content_data,
                "flags": flags,
                "reviewed_by": None,
                "flagged_at": datetime.utcnow(),
                "reviewed_at": None
            }
            
            await db.ai_content_moderation.insert_one(moderation_doc)
            
            logger.info(f"Flagged content for moderation: {moderation_doc['moderation_id']}")
            return moderation_doc["moderation_id"]
            
        except Exception as e:
            logger.error(f"Failed to flag content: {str(e)}")
            return None

    async def get_flagged_content(self, status: str = "flagged", limit: int = 50) -> List[Dict[str, Any]]:
        """Get flagged content for admin review"""
        try:
            db = await self.get_db()
            
            cursor = db.ai_content_moderation.find(
                {"status": status}
            ).sort("flagged_at", -1).limit(limit)
            
            flagged_content = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string for JSON serialization
            for item in flagged_content:
                item["_id"] = str(item["_id"])
            
            return flagged_content
            
        except Exception as e:
            logger.error(f"Failed to get flagged content: {str(e)}")
            return []

    async def moderate_content(self, moderation_id: str, action: str, admin_user_id: str, 
                             reason: str = None) -> bool:
        """Moderate flagged content (approve/reject)"""
        try:
            db = await self.get_db()
            
            update_doc = {
                "status": "approved" if action == "approve" else "rejected",
                "reviewed_by": admin_user_id,
                "reviewed_at": datetime.utcnow()
            }
            
            if reason:
                update_doc["review_reason"] = reason
            
            result = await db.ai_content_moderation.update_one(
                {"moderation_id": moderation_id},
                {"$set": update_doc}
            )
            
            if result.modified_count > 0:
                logger.info(f"Content {moderation_id} {action}ed by admin {admin_user_id}")
                return True
            else:
                logger.warning(f"No content found with moderation_id: {moderation_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to moderate content: {str(e)}")
            return False

    async def get_feature_toggles(self, restaurant_id: str = None) -> List[Dict[str, Any]]:
        """Get feature toggles for restaurants"""
        try:
            db = await self.get_db()
            
            match_filter = {}
            if restaurant_id:
                match_filter["restaurant_id"] = restaurant_id
            
            cursor = db.ai_feature_toggles.find(match_filter)
            toggles = await cursor.to_list(length=None)
            
            # Convert ObjectId to string
            for toggle in toggles:
                toggle["_id"] = str(toggle["_id"])
            
            return toggles
            
        except Exception as e:
            logger.error(f"Failed to get feature toggles: {str(e)}")
            return []

    async def update_feature_toggle(self, restaurant_id: str, feature_name: str, 
                                  enabled: bool, rate_limits: Dict[str, int] = None, 
                                  admin_user_id: str = None) -> bool:
        """Update feature toggle for a restaurant"""
        try:
            db = await self.get_db()
            
            toggle_doc = {
                "restaurant_id": restaurant_id,
                "feature_name": feature_name,
                "enabled": enabled,
                "rate_limits": rate_limits or {},
                "updated_at": datetime.utcnow(),
                "updated_by": admin_user_id or "system"
            }
            
            # Upsert the toggle
            result = await db.ai_feature_toggles.update_one(
                {"restaurant_id": restaurant_id, "feature_name": feature_name},
                {"$set": toggle_doc},
                upsert=True
            )
            
            logger.info(f"Updated feature toggle: {feature_name} for restaurant {restaurant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update feature toggle: {str(e)}")
            return False

    async def check_feature_enabled(self, restaurant_id: str, feature_name: str) -> bool:
        """Check if a feature is enabled for a restaurant"""
        try:
            db = await self.get_db()
            
            toggle = await db.ai_feature_toggles.find_one({
                "restaurant_id": restaurant_id,
                "feature_name": feature_name
            })
            
            # Default to enabled if no toggle exists
            return toggle.get("enabled", True) if toggle else True
            
        except Exception as e:
            logger.error(f"Failed to check feature toggle: {str(e)}")
            return True  # Default to enabled on error

    async def check_rate_limit(self, restaurant_id: str, feature_name: str) -> Dict[str, Any]:
        """Check rate limits for a restaurant feature"""
        try:
            db = await self.get_db()
            
            # Get feature toggle with rate limits
            toggle = await db.ai_feature_toggles.find_one({
                "restaurant_id": restaurant_id,
                "feature_name": feature_name
            })
            
            if not toggle or not toggle.get("rate_limits"):
                return {"allowed": True, "remaining": None}
            
            rate_limits = toggle["rate_limits"]
            now = datetime.utcnow()
            
            # Check daily limit
            if "daily_limit" in rate_limits:
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                today_usage = await db.ai_usage_analytics.count_documents({
                    "restaurant_id": restaurant_id,
                    "feature_type": feature_name,
                    "timestamp": {"$gte": today_start}
                })
                
                if today_usage >= rate_limits["daily_limit"]:
                    return {
                        "allowed": False,
                        "reason": "Daily limit exceeded",
                        "limit": rate_limits["daily_limit"],
                        "used": today_usage
                    }
            
            # Check hourly limit
            if "hourly_limit" in rate_limits:
                hour_start = now.replace(minute=0, second=0, microsecond=0)
                hour_usage = await db.ai_usage_analytics.count_documents({
                    "restaurant_id": restaurant_id,
                    "feature_type": feature_name,
                    "timestamp": {"$gte": hour_start}
                })
                
                if hour_usage >= rate_limits["hourly_limit"]:
                    return {
                        "allowed": False,
                        "reason": "Hourly limit exceeded",
                        "limit": rate_limits["hourly_limit"],
                        "used": hour_usage
                    }
            
            return {"allowed": True, "remaining": None}
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {str(e)}")
            return {"allowed": True, "remaining": None}  # Default to allowed on error

    async def calculate_daily_aggregates(self, date: datetime = None):
        """Calculate and store daily performance metrics"""
        try:
            db = await self.get_db()
            target_date = date or datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            day_start = target_date
            day_end = day_start + timedelta(days=1)
            
            # Get feature types for the day
            feature_types = await db.ai_usage_analytics.distinct("feature_type", {
                "timestamp": {"$gte": day_start, "$lt": day_end}
            })
            
            for feature_type in feature_types:
                # Calculate daily metrics for each feature
                pipeline = [
                    {"$match": {
                        "feature_type": feature_type,
                        "timestamp": {"$gte": day_start, "$lt": day_end}
                    }},
                    {"$group": {
                        "_id": {"$hour": "$timestamp"},
                        "requests": {"$sum": 1},
                        "successful": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                        "failed": {"$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}},
                        "avg_processing_time": {"$avg": "$processing_time_ms"},
                        "cost": {"$sum": "$estimated_cost"}
                    }}
                ]
                
                hourly_data = await db.ai_usage_analytics.aggregate(pipeline).to_list(None)
                
                # Create hourly breakdown
                hourly_breakdown = {}
                total_requests = 0
                total_successful = 0
                total_failed = 0
                total_cost = 0
                processing_times = []
                
                for hour_data in hourly_data:
                    hour = str(hour_data["_id"]).zfill(2)
                    hourly_breakdown[hour] = {
                        "requests": hour_data["requests"],
                        "cost": round(hour_data["cost"], 4)
                    }
                    total_requests += hour_data["requests"]
                    total_successful += hour_data["successful"]
                    total_failed += hour_data["failed"]
                    total_cost += hour_data["cost"]
                    if hour_data["avg_processing_time"]:
                        processing_times.append(hour_data["avg_processing_time"])
                
                # Store daily aggregate
                metric_doc = {
                    "metric_id": str(uuid.uuid4()),
                    "feature_type": feature_type,
                    "metric_date": day_start,
                    "total_requests": total_requests,
                    "successful_requests": total_successful,
                    "failed_requests": total_failed,
                    "avg_processing_time": round(sum(processing_times) / len(processing_times) if processing_times else 0),
                    "total_cost": round(total_cost, 4),
                    "hourly_breakdown": hourly_breakdown,
                    "created_at": datetime.utcnow()
                }
                
                # Upsert daily metric
                await db.ai_performance_metrics.replace_one(
                    {"feature_type": feature_type, "metric_date": day_start},
                    metric_doc,
                    upsert=True
                )
                
                logger.info(f"Calculated daily aggregates for {feature_type} on {day_start.date()}")
            
        except Exception as e:
            logger.error(f"Failed to calculate daily aggregates: {str(e)}")

    def _calculate_cost(self, tokens_used: int, feature_type: str) -> float:
        """Calculate estimated cost based on tokens and feature type"""
        # Simple cost calculation - adjust based on actual OpenAI pricing
        cost_per_token = {
            "image_enhancement": 0.0,  # No tokens for image enhancement
            "content_generation": 0.00002,  # ~$0.02 per 1K tokens
            "marketing_assistant": 0.00002,
            "menu_optimizer": 0.00002,
            "digital_grader": 0.00002
        }
        
        return tokens_used * cost_per_token.get(feature_type, 0.00002)

    async def _get_active_requests_count(self) -> int:
        """Get count of currently active AI requests"""
        # This would track in-progress requests in a separate collection or cache
        # For now, return 0 as placeholder
        return 0

# Create service instance
admin_analytics_service = AdminAnalyticsService()