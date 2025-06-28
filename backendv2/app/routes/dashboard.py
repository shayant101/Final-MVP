"""
Dashboard Routes
Implements all dashboard endpoints with API compatibility
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ..auth import get_current_user, require_admin, get_restaurant_id, require_restaurant
from ..models import TokenData
from ..services.dashboard_service import DashboardService
from pydantic import BaseModel

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Request models
class ChecklistUpdateRequest(BaseModel):
    is_complete: bool

# Dashboard Routes

@router.get("/restaurant")
async def get_restaurant_dashboard(
    restaurant_id: str = Depends(get_restaurant_id),
    current_user: TokenData = Depends(require_restaurant)
):
    """
    Get restaurant dashboard data
    Matches Node.js: GET /api/dashboard/restaurant
    """
    try:
        data = await DashboardService.get_restaurant_dashboard_data(restaurant_id)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/admin")
async def get_admin_dashboard(
    current_user: TokenData = Depends(require_admin)
):
    """
    Get admin dashboard data
    Matches Node.js: GET /api/dashboard/admin
    """
    try:
        data = await DashboardService.get_admin_dashboard_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/restaurants")
async def get_all_restaurants(
    search: Optional[str] = Query(None, description="Search restaurants by name"),
    current_user: TokenData = Depends(require_admin)
):
    """
    Get all restaurants (admin only)
    Matches Node.js: GET /api/dashboard/restaurants
    """
    try:
        data = await DashboardService.get_all_restaurants(search)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/campaigns")
async def get_restaurant_campaigns(
    restaurant_id: str = Depends(get_restaurant_id),
    current_user: TokenData = Depends(require_restaurant)
):
    """
    Get restaurant campaigns
    Matches Node.js: GET /api/dashboard/campaigns
    """
    try:
        data = await DashboardService.get_restaurant_campaigns(restaurant_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@router.put("/checklist/{item_id}")
async def update_checklist_item(
    item_id: str,
    request: ChecklistUpdateRequest,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user: TokenData = Depends(require_restaurant)
):
    """
    Update checklist item
    Matches Node.js: PUT /api/dashboard/checklist/:itemId
    """
    try:
        result = await DashboardService.update_checklist_item(
            item_id, restaurant_id, request.is_complete
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update checklist item")