"""
Website Publishing API Routes
Dedicated endpoints for website publishing operations
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..models_website_builder import (
    WebsitePublishRequest, WebsitePublishResponse, 
    WebsiteUnpublishRequest, WebsiteUnpublishResponse,
    WebsitePublishStatusResponse
)
from ..services.website_publishing_service import WebsitePublishingService
from ..services.admin_analytics_service import admin_analytics_service
from ..database import get_database
from ..auth import get_restaurant_id, require_restaurant

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/website-builder", tags=["Website Publishing"])


@router.post("/websites/{website_id}/publish", response_model=WebsitePublishResponse)
async def publish_website(
    website_id: str,
    request: Optional[WebsitePublishRequest] = None,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Publish a restaurant website to make it live on the internet
    
    This endpoint handles the complete publishing workflow:
    - Validates website is ready for publishing
    - Generates unique subdomain if needed
    - Creates content snapshot for published version
    - Updates website status and publishing metadata
    - Creates deployment record for tracking
    
    Args:
        website_id: ID of the website to publish
        request: Publishing configuration and options (optional)
        restaurant_id: Restaurant ID from authentication
        current_user: Authenticated user
        db: Database connection
        
    Returns:
        WebsitePublishResponse with success status and live URL
    """
    if request is None:
        request = WebsitePublishRequest(website_id=website_id)
    
    try:
        logger.info(f"🚀 Publishing website {website_id} for restaurant {restaurant_id}")
        
        # Initialize publishing service
        publishing_service = WebsitePublishingService(db)
        
        # Set the website_id in the request
        request.website_id = website_id
        
        # Publish the website
        response = await publishing_service.publish_website(request, restaurant_id)
        
        # Log analytics if successful
        if response.success:
            asyncio.create_task(admin_analytics_service.log_ai_usage(
                restaurant_id=restaurant_id,
                feature_type="website_publishing",
                operation_type="website_published",
                processing_time=0,
                tokens_used=0,
                status="success",
                metadata={
                    "website_id": website_id,
                    "live_url": response.live_url,
                    "deployment_id": response.deployment_id,
                    "force_republish": request.force_republish,
                    "custom_subdomain": request.custom_subdomain
                }
            ))
            logger.info(f"✅ Successfully published website {website_id} at {response.live_url}")
        else:
            logger.error(f"❌ Failed to publish website {website_id}: {response.message}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Publishing failed for website {website_id}: {str(e)}")
        return WebsitePublishResponse(
            success=False,
            message=f"Publishing failed: {str(e)}",
            error_details=str(e)
        )


@router.post("/websites/{website_id}/unpublish", response_model=WebsiteUnpublishResponse)
async def unpublish_website(
    website_id: str,
    request: Optional[WebsiteUnpublishRequest] = None,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Unpublish a website (take it offline)
    
    This endpoint handles the unpublishing workflow:
    - Validates website is currently published
    - Updates website status to draft
    - Optionally cleans up static files and CDN resources
    - Preserves subdomain for quick republishing
    
    Args:
        website_id: ID of the website to unpublish
        request: Unpublishing configuration and options (optional)
        restaurant_id: Restaurant ID from authentication
        current_user: Authenticated user
        db: Database connection
        
    Returns:
        WebsiteUnpublishResponse with success status and cleanup details
    """
    if request is None:
        request = WebsiteUnpublishRequest(website_id=website_id)
    
    try:
        logger.info(f"📴 Unpublishing website {website_id} for restaurant {restaurant_id}")
        
        # Initialize publishing service
        publishing_service = WebsitePublishingService(db)
        
        # Set the website_id in the request
        request.website_id = website_id
        
        # Unpublish the website
        response = await publishing_service.unpublish_website(request, restaurant_id)
        
        # Log analytics if successful
        if response.success:
            asyncio.create_task(admin_analytics_service.log_ai_usage(
                restaurant_id=restaurant_id,
                feature_type="website_publishing",
                operation_type="website_unpublished",
                processing_time=0,
                tokens_used=0,
                status="success",
                metadata={
                    "website_id": website_id,
                    "keep_static_files": request.keep_static_files,
                    "cleanup_details": response.cleanup_details
                }
            ))
            logger.info(f"✅ Successfully unpublished website {website_id}")
        else:
            logger.error(f"❌ Failed to unpublish website {website_id}: {response.message}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unpublishing failed for website {website_id}: {str(e)}")
        return WebsiteUnpublishResponse(
            success=False,
            message=f"Unpublishing failed: {str(e)}"
        )


@router.get("/websites/{website_id}/publish-status", response_model=WebsitePublishStatusResponse)
async def get_website_publish_status(
    website_id: str,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Get the current publishing status of a website
    
    This endpoint provides comprehensive publishing status information:
    - Current website status (draft, published, etc.)
    - Live URL if published
    - Last published timestamp
    - Whether there are unpublished changes
    - Deployment status and performance metrics
    
    Args:
        website_id: ID of the website to check
        restaurant_id: Restaurant ID from authentication
        current_user: Authenticated user
        db: Database connection
        
    Returns:
        WebsitePublishStatusResponse with current publishing status
    """
    try:
        logger.info(f"📊 Getting publish status for website {website_id}")
        
        # Initialize publishing service
        publishing_service = WebsitePublishingService(db)
        
        # Get publish status
        response = await publishing_service.get_publish_status(website_id, restaurant_id)
        
        logger.info(f"📊 Website {website_id} status: {response.status}, live_url: {response.live_url}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get publish status for website {website_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get publish status: {str(e)}"
        )


@router.post("/websites/{website_id}/validate-for-publishing")
async def validate_website_for_publishing(
    website_id: str,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Validate that a website is ready for publishing
    
    This endpoint performs comprehensive validation checks:
    - Required fields are present (website name, pages, etc.)
    - At least one page exists with homepage designation
    - SEO settings are configured (title, description)
    - Content quality checks
    
    Args:
        website_id: ID of the website to validate
        restaurant_id: Restaurant ID from authentication
        current_user: Authenticated user
        db: Database connection
        
    Returns:
        Validation results with errors and warnings
    """
    try:
        logger.info(f"🔍 Validating website {website_id} for publishing")
        
        # Initialize publishing service
        publishing_service = WebsitePublishingService(db)
        
        # Get website
        website = await publishing_service._get_website(website_id, restaurant_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Validate website
        validation_result = await publishing_service._validate_website_for_publishing(website)
        
        logger.info(f"🔍 Website {website_id} validation: {'✅ Valid' if validation_result['is_valid'] else '❌ Invalid'}")
        
        return {
            "success": True,
            "website_id": website_id,
            "is_valid": validation_result["is_valid"],
            "errors": validation_result["errors"],
            "validation_timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Validation failed for website {website_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/websites/{website_id}/deployment-history")
async def get_deployment_history(
    website_id: str,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Get deployment history for a website
    
    Args:
        website_id: ID of the website
        restaurant_id: Restaurant ID from authentication
        current_user: Authenticated user
        db: Database connection
        
    Returns:
        List of deployment records with timestamps and status
    """
    try:
        logger.info(f"📜 Getting deployment history for website {website_id}")
        
        # Verify website access
        publishing_service = WebsitePublishingService(db)
        website = await publishing_service._get_website(website_id, restaurant_id)
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Get deployment history
        deployments_cursor = db.website_deployments.find(
            {"website_id": website_id}
        ).sort("deployed_at", -1).limit(20)
        
        deployments = await deployments_cursor.to_list(length=20)
        
        # Convert ObjectId to string for JSON serialization
        for deployment in deployments:
            if "_id" in deployment:
                deployment["_id"] = str(deployment["_id"])
        
        logger.info(f"📜 Found {len(deployments)} deployment records for website {website_id}")
        
        return {
            "success": True,
            "website_id": website_id,
            "deployments": deployments,
            "total_deployments": len(deployments)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get deployment history for website {website_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get deployment history: {str(e)}"
        )


@router.post("/websites/{website_id}/mark-changed")
async def mark_website_as_changed(
    website_id: str,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Manually mark a website as having unpublished changes
    
    This is useful for triggering change detection when content
    has been modified outside the normal editing workflow.
    
    Args:
        website_id: ID of the website to mark as changed
        restaurant_id: Restaurant ID from authentication
        current_user: Authenticated user
        db: Database connection
        
    Returns:
        Success status
    """
    try:
        logger.info(f"🔄 Marking website {website_id} as changed")
        
        # Initialize publishing service
        publishing_service = WebsitePublishingService(db)
        
        # Mark as changed
        success = await publishing_service.mark_website_as_changed(website_id, restaurant_id)
        
        if success:
            logger.info(f"✅ Successfully marked website {website_id} as changed")
            return {
                "success": True,
                "message": "Website marked as having unpublished changes",
                "website_id": website_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            logger.warning(f"⚠️ Failed to mark website {website_id} as changed")
            return {
                "success": False,
                "message": "Failed to mark website as changed",
                "website_id": website_id
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to mark website {website_id} as changed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark website as changed: {str(e)}"
        )