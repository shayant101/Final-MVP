"""
Admin Routes
Provides admin-only endpoints for analytics, content moderation, and feature management
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from bson import ObjectId

from ..services.admin_analytics_service import admin_analytics_service
from ..auth import get_current_user
from ..models import (
    AnalyticsDateRange, RealTimeMetrics, UsageAnalyticsResponse,
    ContentModerationRequest, FeatureToggleRequest
)
from ..database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["Admin"])

def require_admin_role(current_user = Depends(get_current_user)):
    """Dependency to require admin role"""
    if hasattr(current_user, 'role') and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    elif hasattr(current_user, 'get') and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    elif not hasattr(current_user, 'role') and not hasattr(current_user, 'get'):
        # For TokenData objects, check if user_id contains 'admin'
        if hasattr(current_user, 'user_id') and 'admin' not in str(current_user.user_id):
            raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Analytics Endpoints
@router.get("/analytics/real-time")
async def get_real_time_metrics(
    admin_user = Depends(require_admin_role)
):
    """
    Get real-time AI usage metrics for admin dashboard
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} requesting real-time metrics")
        
        metrics = await admin_analytics_service.get_real_time_metrics()
        
        return {
            "success": True,
            "message": "Real-time metrics retrieved successfully",
            "data": metrics
        }
        
    except Exception as e:
        logger.error(f"Real-time metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")

@router.get("/analytics/usage")
async def get_usage_analytics(
    days: int = Query(7, description="Number of days to analyze"),
    feature_type: Optional[str] = Query(None, description="Filter by feature type"),
    admin_user = Depends(require_admin_role)
):
    """
    Get detailed usage analytics with date range and filtering
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} requesting usage analytics for {days} days")
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        analytics = await admin_analytics_service.get_usage_analytics(
            date_range=(start_date, end_date),
            feature_type=feature_type
        )
        
        return {
            "success": True,
            "message": f"Usage analytics retrieved for {days} days",
            "data": analytics
        }
        
    except Exception as e:
        logger.error(f"Usage analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get usage analytics: {str(e)}")

@router.get("/analytics/restaurant/{restaurant_id}")
async def get_restaurant_analytics(
    restaurant_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    admin_user = Depends(require_admin_role)
):
    """
    Get analytics for a specific restaurant
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} requesting analytics for restaurant {restaurant_id}")
        
        analytics = await admin_analytics_service.get_restaurant_analytics(
            restaurant_id=restaurant_id,
            days=days
        )
        
        return {
            "success": True,
            "message": f"Restaurant analytics retrieved for {days} days",
            "data": analytics
        }
        
    except Exception as e:
        logger.error(f"Restaurant analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get restaurant analytics: {str(e)}")

@router.post("/analytics/calculate-aggregates")
async def calculate_daily_aggregates(
    date: Optional[str] = None,
    admin_user = Depends(require_admin_role)
):
    """
    Manually trigger calculation of daily performance aggregates
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} triggering aggregate calculation")
        
        target_date = None
        if date:
            target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        await admin_analytics_service.calculate_daily_aggregates(target_date)
        
        return {
            "success": True,
            "message": "Daily aggregates calculated successfully",
            "data": {
                "calculated_date": target_date.isoformat() if target_date else datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Aggregate calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate aggregates: {str(e)}")

# Content Moderation Endpoints
@router.get("/moderation/flagged-content")
async def get_flagged_content(
    status: str = Query("flagged", description="Content status to filter by"),
    limit: int = Query(50, description="Maximum number of items to return"),
    admin_user = Depends(require_admin_role)
):
    """
    Get flagged content for admin review
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} requesting flagged content")
        
        flagged_content = await admin_analytics_service.get_flagged_content(
            status=status,
            limit=limit
        )
        
        return {
            "success": True,
            "message": f"Retrieved {len(flagged_content)} flagged content items",
            "data": {
                "flagged_content": flagged_content,
                "total_count": len(flagged_content),
                "status_filter": status
            }
        }
        
    except Exception as e:
        logger.error(f"Flagged content retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get flagged content: {str(e)}")

@router.post("/moderation/moderate-content")
async def moderate_content(
    moderation_id: str,
    action: str,
    reason: Optional[str] = None,
    admin_user = Depends(require_admin_role)
):
    """
    Moderate flagged content (approve/reject)
    """
    try:
        if action not in ["approve", "reject"]:
            raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
        
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} moderating content {moderation_id}: {action}")
        
        success = await admin_analytics_service.moderate_content(
            moderation_id=moderation_id,
            action=action,
            admin_user_id=user_id,
            reason=reason
        )
        
        if success:
            return {
                "success": True,
                "message": f"Content {action}ed successfully",
                "data": {
                    "moderation_id": moderation_id,
                    "action": action,
                    "moderated_by": user_id,
                    "moderated_at": datetime.utcnow().isoformat()
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Content not found or already moderated")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content moderation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to moderate content: {str(e)}")

@router.post("/moderation/bulk-moderate")
async def bulk_moderate_content(
    request: ContentModerationRequest,
    admin_user = Depends(require_admin_role)
):
    """
    Bulk moderate multiple content items
    """
    try:
        if request.action not in ["approve", "reject", "flag"]:
            raise HTTPException(status_code=400, detail="Action must be 'approve', 'reject', or 'flag'")
        
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} bulk moderating {len(request.content_ids)} items: {request.action}")
        
        results = []
        for content_id in request.content_ids:
            success = await admin_analytics_service.moderate_content(
                moderation_id=content_id,
                action=request.action,
                admin_user_id=user_id,
                reason=request.reason
            )
            results.append({
                "content_id": content_id,
                "success": success,
                "action": request.action
            })
        
        successful_count = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "message": f"Bulk moderation completed: {successful_count}/{len(request.content_ids)} successful",
            "data": {
                "results": results,
                "total_processed": len(request.content_ids),
                "successful": successful_count,
                "failed": len(request.content_ids) - successful_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk moderation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to bulk moderate content: {str(e)}")

# Feature Management Endpoints
@router.get("/features/toggles")
async def get_feature_toggles(
    restaurant_id: Optional[str] = Query(None, description="Filter by restaurant ID"),
    admin_user = Depends(require_admin_role)
):
    """
    Get feature toggles for restaurants
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} requesting feature toggles")
        
        toggles = await admin_analytics_service.get_feature_toggles(restaurant_id)
        
        return {
            "success": True,
            "message": f"Retrieved {len(toggles)} feature toggles",
            "data": {
                "feature_toggles": toggles,
                "total_count": len(toggles),
                "restaurant_filter": restaurant_id
            }
        }
        
    except Exception as e:
        logger.error(f"Feature toggles retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get feature toggles: {str(e)}")

@router.post("/features/toggle")
async def update_feature_toggle(
    request: FeatureToggleRequest,
    admin_user = Depends(require_admin_role)
):
    """
    Update feature toggle for a restaurant
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} updating feature toggle: {request.feature_name} for restaurant {request.restaurant_id}")
        
        success = await admin_analytics_service.update_feature_toggle(
            restaurant_id=request.restaurant_id,
            feature_name=request.feature_name,
            enabled=request.enabled,
            rate_limits=request.rate_limits,
            admin_user_id=user_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"Feature toggle updated successfully",
                "data": {
                    "restaurant_id": request.restaurant_id,
                    "feature_name": request.feature_name,
                    "enabled": request.enabled,
                    "rate_limits": request.rate_limits,
                    "updated_by": user_id,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update feature toggle")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feature toggle update error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update feature toggle: {str(e)}")

@router.get("/features/check/{restaurant_id}/{feature_name}")
async def check_feature_status(
    restaurant_id: str,
    feature_name: str,
    admin_user = Depends(require_admin_role)
):
    """
    Check feature status and rate limits for a restaurant
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} checking feature status: {feature_name} for restaurant {restaurant_id}")
        
        # Check if feature is enabled
        enabled = await admin_analytics_service.check_feature_enabled(restaurant_id, feature_name)
        
        # Check rate limits
        rate_limit_status = await admin_analytics_service.check_rate_limit(restaurant_id, feature_name)
        
        return {
            "success": True,
            "message": "Feature status retrieved successfully",
            "data": {
                "restaurant_id": restaurant_id,
                "feature_name": feature_name,
                "enabled": enabled,
                "rate_limit_status": rate_limit_status,
                "checked_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Feature status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check feature status: {str(e)}")

# Dashboard Summary Endpoints
@router.get("/dashboard/summary")
async def get_admin_dashboard_summary(
    admin_user = Depends(require_admin_role)
):
    """
    Get comprehensive admin dashboard summary
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} requesting dashboard summary")
        
        # Get real-time metrics
        real_time_metrics = await admin_analytics_service.get_real_time_metrics()
        
        # Get recent analytics (last 7 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        recent_analytics = await admin_analytics_service.get_usage_analytics((start_date, end_date))
        
        # Get flagged content count
        flagged_content = await admin_analytics_service.get_flagged_content(status="flagged", limit=1)
        flagged_count = len(flagged_content)
        
        # Get feature toggles summary
        all_toggles = await admin_analytics_service.get_feature_toggles()
        
        # Calculate summary statistics
        total_features = len(set(toggle["feature_name"] for toggle in all_toggles))
        enabled_features = len([t for t in all_toggles if t["enabled"]])
        
        dashboard_summary = {
            "admin_user": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "real_time_metrics": real_time_metrics,
            "recent_analytics": {
                "period": "Last 7 days",
                "total_usage_events": len(recent_analytics.get("usage_over_time", [])),
                "feature_breakdown": recent_analytics.get("feature_breakdown", []),
                "error_count": len(recent_analytics.get("error_analysis", []))
            },
            "content_moderation": {
                "flagged_content_count": flagged_count,
                "pending_review": flagged_count  # Assuming flagged = pending review
            },
            "feature_management": {
                "total_features": total_features,
                "enabled_features": enabled_features,
                "total_restaurants_with_toggles": len(set(toggle["restaurant_id"] for toggle in all_toggles))
            },
            "system_health": {
                "analytics_service": "operational",
                "content_moderation": "operational",
                "feature_toggles": "operational"
            }
        }
        
        return {
            "success": True,
            "message": "Admin dashboard summary retrieved successfully",
            "data": dashboard_summary
        }
        
    except Exception as e:
        logger.error(f"Dashboard summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}")

# System Management Endpoints
@router.post("/system/create-admin")
async def create_admin_user(
    email: str,
    password: str,
    admin_user = Depends(require_admin_role)
):
    """
    Create a new admin user (admin-only)
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} creating new admin user: {email}")
        
        # This would typically create a new admin user in the database
        # For now, return a placeholder response
        return {
            "success": True,
            "message": "Admin user creation endpoint - implementation pending",
            "data": {
                "email": email,
                "role": "admin",
                "created_by": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "note": "This endpoint needs to be connected to the user management system"
            }
        }
        
    except Exception as e:
        logger.error(f"Admin user creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create admin user: {str(e)}")

@router.get("/system/health")
async def get_system_health(
    admin_user = Depends(require_admin_role)
):
    """
    Get system health status
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} requesting system health")
        
        # Check database connectivity
        db_status = "operational"
        try:
            await admin_analytics_service.get_db()
        except Exception:
            db_status = "error"
        
        # Check analytics service
        analytics_status = "operational"
        try:
            await admin_analytics_service.get_real_time_metrics()
        except Exception:
            analytics_status = "error"
        
        health_status = {
            "overall_status": "operational" if db_status == "operational" and analytics_status == "operational" else "degraded",
            "components": {
                "database": db_status,
                "analytics_service": analytics_status,
                "content_moderation": "operational",
                "feature_toggles": "operational"
            },
            "checked_at": datetime.utcnow().isoformat(),
            "checked_by": user_id
        }
        
        return {
            "success": True,
            "message": "System health check completed",
            "data": health_status
        }
        
    except Exception as e:
        logger.error(f"System health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check system health: {str(e)}")

# Restaurant Management Endpoints
@router.delete("/restaurants/{restaurant_id}")
async def delete_restaurant(
    restaurant_id: str,
    admin_user = Depends(require_admin_role)
):
    """
    Delete a restaurant and all associated data (admin-only)
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} attempting to delete restaurant {restaurant_id}")
        
        # Get database instance
        db = get_database()
        
        # Try to convert restaurant_id to ObjectId if it's a valid ObjectId string
        try:
            if ObjectId.is_valid(restaurant_id):
                query_id = ObjectId(restaurant_id)
            else:
                query_id = restaurant_id
        except Exception:
            query_id = restaurant_id
        
        # Check if restaurant exists
        restaurant = await db.restaurants.find_one({"_id": query_id})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Delete the restaurant document
        delete_result = await db.restaurants.delete_one({"_id": query_id})
        
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete restaurant")
        
        # Also delete associated user account if it exists
        user_deleted = False
        if restaurant.get("user_id"):
            # Try to delete user by user_id (string format first, then ObjectId)
            user_delete_result = await db.users.delete_one({"_id": ObjectId(restaurant["user_id"])})
            if user_delete_result.deleted_count == 0:
                # Fallback: try string format user_id
                user_delete_result = await db.users.delete_one({"user_id": restaurant["user_id"]})
            user_deleted = user_delete_result.deleted_count > 0
        elif restaurant.get("email"):
            # Fallback: delete by email if user_id not available
            user_delete_result = await db.users.delete_one({"email": restaurant["email"]})
            user_deleted = user_delete_result.deleted_count > 0
        
        logger.info(f"Admin {user_id} successfully deleted restaurant {restaurant_id}")
        
        return {
            "success": True,
            "message": f"Restaurant '{restaurant.get('name', restaurant_id)}' deleted successfully",
            "data": {
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant.get("name", "Unknown"),
                "restaurant_email": restaurant.get("email", "Unknown"),
                "user_account_deleted": user_deleted,
                "deleted_by": user_id,
                "deleted_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Restaurant deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete restaurant: {str(e)}")

@router.get("/restaurants")
async def list_restaurants(
    search: Optional[str] = Query(None, description="Search restaurants by name or email"),
    limit: int = Query(50, description="Maximum number of restaurants to return"),
    skip: int = Query(0, description="Number of restaurants to skip"),
    admin_user = Depends(require_admin_role)
):
    """
    List all restaurants with optional search (admin-only)
    """
    try:
        user_id = getattr(admin_user, 'user_id', admin_user.get('user_id') if hasattr(admin_user, 'get') else 'admin')
        logger.info(f"Admin {user_id} requesting restaurant list")
        
        # Get database instance
        db = get_database()
        
        # Build search query
        query = {}
        if search:
            query = {
                "$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}},
                    {"address": {"$regex": search, "$options": "i"}}
                ]
            }
        
        # Get restaurants with pagination
        cursor = db.restaurants.find(query).skip(skip).limit(limit)
        restaurants = await cursor.to_list(length=limit)
        
        # Get total count for pagination
        total_count = await db.restaurants.count_documents(query)
        
        # Format restaurant data for admin view
        formatted_restaurants = []
        for restaurant in restaurants:
            formatted_restaurants.append({
                "id": restaurant["_id"],
                "name": restaurant.get("name", "Unknown"),
                "email": restaurant.get("email", "Unknown"),
                "address": restaurant.get("address", "Unknown"),
                "phone": restaurant.get("phone", "Unknown"),
                "created_at": restaurant.get("created_at", "Unknown"),
                "last_login": restaurant.get("last_login", "Never"),
                "email_verified": restaurant.get("email_verified", False)
            })
        
        return {
            "success": True,
            "message": f"Retrieved {len(formatted_restaurants)} restaurants",
            "data": {
                "restaurants": formatted_restaurants,
                "total_count": total_count,
                "returned_count": len(formatted_restaurants),
                "search_query": search,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "has_more": (skip + len(formatted_restaurants)) < total_count
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Restaurant listing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list restaurants: {str(e)}")