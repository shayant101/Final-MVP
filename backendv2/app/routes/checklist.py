from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from app.auth import get_current_user, get_restaurant_id
from app.models import TokenData, ChecklistCategory, ChecklistItem, RestaurantChecklistStatus, ChecklistStatus, ChecklistType
from app.services.checklist_service import ChecklistService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/checklist", tags=["checklist"])

def get_checklist_service():
    """Get checklist service instance"""
    return ChecklistService()

@router.get("/categories")
async def get_categories(
    type: Optional[ChecklistType] = Query(None, description="Filter by category type: foundational or ongoing"),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all checklist categories with optional type filter
    
    - **type**: Optional filter for 'foundational' or 'ongoing' categories
    """
    try:
        service = get_checklist_service()
        categories = await service.get_categories(type_filter=type)
        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch categories"
        )

@router.get("/items/{category_id}")
async def get_category_items(
    category_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all items for a specific category
    
    - **category_id**: The ID of the category to fetch items for
    """
    try:
        service = get_checklist_service()
        items = await service.get_category_items(category_id)
        return {
            "success": True,
            "items": items
        }
    except Exception as e:
        logger.error(f"Error fetching items for category {category_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch items"
        )

@router.get("/status/{restaurant_id}")
async def get_restaurant_checklist_status(
    restaurant_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get checklist status for a specific restaurant
    
    - **restaurant_id**: The ID of the restaurant to fetch status for
    """
    try:
        service = get_checklist_service()
        # Verify user has access to this restaurant
        await service.verify_restaurant_access(current_user, restaurant_id)
        
        statuses = await service.get_restaurant_status(restaurant_id)
        return {
            "success": True,
            "statuses": statuses
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching status for restaurant {restaurant_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch status"
        )

@router.put("/status/{restaurant_id}/{item_id}")
async def update_item_status(
    restaurant_id: str,
    item_id: str,
    status: ChecklistStatus = Query(..., description="New status for the item"),
    notes: Optional[str] = Query(None, description="Optional notes about the status update"),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Update the status of a checklist item for a restaurant
    
    - **restaurant_id**: The ID of the restaurant
    - **item_id**: The ID of the checklist item
    - **status**: New status (pending, in_progress, completed, not_applicable)
    - **notes**: Optional notes about the status update
    """
    try:
        service = get_checklist_service()
        # Verify user has access to this restaurant
        await service.verify_restaurant_access(current_user, restaurant_id)
        
        status_id = await service.update_item_status(
            restaurant_id, item_id, status, notes
        )
        
        return {
            "success": True,
            "message": "Status updated successfully",
            "statusId": status_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating status for restaurant {restaurant_id}, item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update status"
        )

@router.get("/progress/{restaurant_id}")
async def get_restaurant_progress(
    restaurant_id: str,
    type: Optional[ChecklistType] = Query(None, description="Filter by category type: foundational or ongoing"),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get progress statistics for a restaurant's checklist
    
    - **restaurant_id**: The ID of the restaurant
    - **type**: Optional filter for 'foundational' or 'ongoing' categories
    """
    try:
        service = get_checklist_service()
        # Verify user has access to this restaurant
        await service.verify_restaurant_access(current_user, restaurant_id)
        
        progress = await service.get_restaurant_progress(restaurant_id, type_filter=type)
        return {
            "success": True,
            "progress": progress
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating progress for restaurant {restaurant_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate progress"
        )

@router.get("/categories-with-items")
async def get_categories_with_items(
    type: Optional[ChecklistType] = Query(None, description="Filter by category type: foundational or ongoing"),
    restaurant_id: Optional[str] = Query(None, description="Include status for specific restaurant"),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all categories with their items, optionally including status for a specific restaurant
    
    - **type**: Optional filter for 'foundational' or 'ongoing' categories
    - **restaurant_id**: Optional restaurant ID to include status information
    """
    try:
        service = get_checklist_service()
        # If restaurant_id is provided, verify access
        if restaurant_id:
            await service.verify_restaurant_access(current_user, restaurant_id)
        
        categories = await service.get_categories_with_items(
            type_filter=type,
            restaurant_id=restaurant_id
        )
        
        return {
            "success": True,
            "categories": categories
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching categories with items: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch categories with items"
        )