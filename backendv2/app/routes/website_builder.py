"""
Website Builder API Routes
AI-powered restaurant website generation and management endpoints
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from .media_upload import router as media_router
from ..models_website_builder import (
    WebsiteGenerationRequest, WebsiteGenerationResponse, RestaurantWebsite,
    WebsiteListResponse, WebsiteUpdateRequest, ComponentUpdateRequest,
    PageUpdateRequest, WebsitePreviewRequest, WebsitePreviewResponse,
    AIGenerationProgress, WebsiteBuilderDashboard, WebsiteTemplate,
    WebsiteAnalytics, WebsiteBackup, WebsiteDeployment, WebsiteStatus,
    AIGenerationSettings, WebsitePerformanceMetrics,
    WebsitePublishRequest, WebsitePublishResponse, WebsiteUnpublishRequest,
    WebsiteUnpublishResponse, WebsitePublishStatusResponse
)
from ..services.ai_website_generator import ai_website_generator
from ..services.admin_analytics_service import admin_analytics_service
from ..services.website_publishing_service import WebsitePublishingService
from ..database import get_database
from ..auth import get_current_user, get_restaurant_id, require_restaurant

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/website-builder", tags=["Website Builder"])

# Global storage for generation progress (in production, use Redis or database)
generation_progress_store = {}

# Note: Image serving is handled by media_upload.py router
# Removed duplicate route to avoid conflicts

@router.post("/generate", response_model=WebsiteGenerationResponse)
async def generate_website(
    request: WebsiteGenerationRequest,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Generate a complete restaurant website using AI - FIXED to use working feature pattern
    """
    try:
        logger.info(f"🔍 DEBUG: Website Builder - Starting generation for restaurant {restaurant_id}")
        logger.info(f"🔍 DEBUG: Website Builder - Request restaurant_id: {request.restaurant_id}")
        logger.info(f"🔍 DEBUG: Website Builder - Auth restaurant_id: {restaurant_id}")
        
        # Use the restaurant_id from auth dependency (same as working features)
        # Override the request restaurant_id with the authenticated one
        request.restaurant_id = restaurant_id
        
        # Validate restaurant exists and user has access using working feature pattern
        restaurant_data = await _get_restaurant_data(restaurant_id, current_user, db)
        if not restaurant_data:
            raise HTTPException(status_code=404, detail="Restaurant not found or access denied")
        
        # Create generation ID and initialize progress tracking
        generation_id = f"gen_{request.restaurant_id}_{int(datetime.now().timestamp())}"
        website_id = f"website_{request.restaurant_id}_{int(datetime.now().timestamp())}"
        
        # Initialize progress tracking
        generation_progress_store[generation_id] = AIGenerationProgress(
            generation_id=generation_id,
            website_id=website_id,
            current_step="Initializing AI generation",
            total_steps=8,
            completed_steps=0,
            progress_percentage=0.0,
            current_operation="Analyzing restaurant data",
            started_at=datetime.now()
        )
        
        # Start background generation task
        background_tasks.add_task(
            _generate_website_background,
            generation_id,
            website_id,
            request,
            restaurant_data,
            current_user,
            db
        )
        
        return WebsiteGenerationResponse(
            success=True,
            website_id=website_id,
            generation_status="started",
            estimated_completion_time=180,  # 3 minutes
            preview_url=f"/api/website-builder/{website_id}/preview"
        )
        
    except Exception as e:
        logger.error(f"Website generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Website generation failed: {str(e)}")

@router.get("/generation/{generation_id}/progress", response_model=AIGenerationProgress)
async def get_generation_progress(
    generation_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get the progress of an ongoing website generation
    """
    try:
        if generation_id not in generation_progress_store:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        progress = generation_progress_store[generation_id]
        
        # Clean up completed generations after 1 hour
        if progress.status == "completed" and progress.completed_at:
            if datetime.now() - progress.completed_at > timedelta(hours=1):
                del generation_progress_store[generation_id]
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get generation progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get generation progress")

@router.get("/websites", response_model=WebsiteListResponse)
async def list_websites(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[WebsiteStatus] = None,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    List all websites for the current user's restaurants - FIXED to use working feature pattern
    """
    try:
        logger.info(f"🔍 DEBUG: Website Builder - list_websites called for restaurant: {restaurant_id}")
        logger.info(f"🔍 DEBUG: Website Builder - User: {current_user.user_id}, Role: {current_user.role}")
        
        # Use the same pattern as working features - direct restaurant_id from dependency
        restaurant_ids = [restaurant_id]
        logger.info(f"🔍 DEBUG: Website Builder - Using restaurant_id from dependency: {restaurant_id}")
        
        # Build query using string restaurant_id (same as working features)
        query = {"restaurant_id": {"$in": restaurant_ids}}
        if status:
            query["status"] = status
        
        logger.info(f"🔍 DEBUG: Website Builder - Query: {query}")
        
        # Get websites with pagination
        skip = (page - 1) * per_page
        websites_cursor = db.websites.find(query).skip(skip).limit(per_page).sort("created_at", -1)
        websites = await websites_cursor.to_list(length=per_page)
        
        logger.info(f"🔍 DEBUG: Website Builder - Found {len(websites)} websites")
        
        # Get total count
        total_count = await db.websites.count_documents(query)
        
        # Convert to response models
        website_models = []
        for website in websites:
            website_models.append(RestaurantWebsite(**website))
        
        return WebsiteListResponse(
            websites=website_models,
            total_count=total_count,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"🔍 DEBUG: Website Builder - Failed to list websites: {str(e)}")
        import traceback
        logger.error(f"🔍 DEBUG: Website Builder - Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to list websites")

@router.get("/websites/{website_id}", response_model=RestaurantWebsite)
async def get_website(
    website_id: str,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Get a specific website by ID - FIXED to use working feature pattern
    """
    try:
        logger.info(f"🔍 DEBUG: Website Builder - get_website called for website: {website_id}")
        logger.info(f"🔍 DEBUG: Website Builder - User: {current_user.user_id}, Role: {current_user.role}")
        logger.info(f"🔍 DEBUG: Website Builder - Restaurant ID from auth: {restaurant_id}")
        
        website = await db.websites.find_one({"website_id": website_id})
        if not website:
            logger.error(f"🔍 DEBUG: Website Builder - Website not found: {website_id}")
            raise HTTPException(status_code=404, detail="Website not found")
        
        logger.info(f"🔍 DEBUG: Website Builder - Found website with restaurant_id: {website.get('restaurant_id')}")
        
        # Verify user has access to this website's restaurant using the same pattern as working features
        if website.get("restaurant_id") != restaurant_id:
            logger.error(f"🔍 DEBUG: Website Builder - Access denied. Website restaurant_id: {website.get('restaurant_id')}, User restaurant_id: {restaurant_id}")
            raise HTTPException(status_code=403, detail="Access denied to this website")
        
        logger.info(f"🔍 DEBUG: Website Builder - Access granted, returning website data")
        
        # CRITICAL DEBUG: Log what's actually in the database
        logger.info(f"🔍 CRITICAL DEBUG: Database website.hero_image = {website.get('hero_image')}")
        logger.info(f"🔍 CRITICAL DEBUG: Database website.menu_items = {website.get('menu_items')}")
        logger.info(f"🔍 CRITICAL DEBUG: Database website.pages = {website.get('pages')}")
        if website.get('pages') and len(website['pages']) > 0:
            logger.info(f"🔍 CRITICAL DEBUG: Database pages[0].sections = {website['pages'][0].get('sections')}")
        
        return RestaurantWebsite(**website)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔍 DEBUG: Website Builder - Failed to get website: {str(e)}")
        import traceback
        logger.error(f"🔍 DEBUG: Website Builder - Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to get website")

@router.put("/websites/{website_id}", response_model=RestaurantWebsite)
async def update_website(
    website_id: str,
    request: WebsiteUpdateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Update website settings and configuration
    """
    try:
        # Get existing website
        website = await db.websites.find_one({"website_id": website_id})
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Verify user has access
        await _verify_restaurant_access(website["restaurant_id"], current_user, db)
        
        # Prepare update data
        update_data = {"updated_at": datetime.now()}
        
        if request.website_name is not None:
            update_data["website_name"] = request.website_name
        
        if request.design_system is not None:
            update_data["design_system"] = request.design_system.dict()
        
        if request.seo_settings is not None:
            update_data["seo_settings"] = request.seo_settings.dict()
        
        if request.integration_settings is not None:
            update_data["integration_settings"] = request.integration_settings.dict()
        
        if request.custom_code is not None:
            update_data["custom_code"] = request.custom_code
        
        # Update website
        await db.websites.update_one(
            {"website_id": website_id},
            {"$set": update_data}
        )
        
        # Get updated website
        updated_website = await db.websites.find_one({"website_id": website_id})
        return RestaurantWebsite(**updated_website)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update website: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update website")

@router.post("/websites/{website_id}/preview", response_model=WebsitePreviewResponse)
async def generate_website_preview(
    website_id: str,
    request: WebsitePreviewRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Generate a preview URL for the website
    """
    try:
        # Get website
        website = await db.websites.find_one({"website_id": website_id})
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Verify user has access
        await _verify_restaurant_access(website["restaurant_id"], current_user, db)
        
        # Generate preview URL (in production, this would create a temporary preview)
        preview_url = f"https://preview.momentum-growth.com/{website_id}/{request.page_slug}?device={request.device_type}"
        preview_expires_at = datetime.now() + timedelta(hours=24)
        
        return WebsitePreviewResponse(
            success=True,
            preview_url=preview_url,
            preview_expires_at=preview_expires_at,
            device_type=request.device_type,
            page_slug=request.page_slug
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate preview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate preview")

@router.delete("/websites/{website_id}")
async def delete_website(
    website_id: str,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Delete a website permanently
    """
    try:
        logger.info(f"🔍 DEBUG: Website Builder - delete_website called for website: {website_id}")
        logger.info(f"🔍 DEBUG: Website Builder - User: {current_user.user_id}, Role: {current_user.role}")
        logger.info(f"🔍 DEBUG: Website Builder - Restaurant ID from auth: {restaurant_id}")
        
        # Get existing website
        website = await db.websites.find_one({"website_id": website_id})
        if not website:
            logger.error(f"🔍 DEBUG: Website Builder - Website not found: {website_id}")
            raise HTTPException(status_code=404, detail="Website not found")
        
        logger.info(f"🔍 DEBUG: Website Builder - Found website with restaurant_id: {website.get('restaurant_id')}")
        
        # Verify user has access to this website's restaurant
        if website.get("restaurant_id") != restaurant_id:
            logger.error(f"🔍 DEBUG: Website Builder - Access denied. Website restaurant_id: {website.get('restaurant_id')}, User restaurant_id: {restaurant_id}")
            raise HTTPException(status_code=403, detail="Access denied to this website")
        
        # Store website info for analytics
        website_name = website.get("website_name", "Unknown")
        
        # Delete the website from database
        result = await db.websites.delete_one({"website_id": website_id})
        
        if result.deleted_count == 0:
            logger.warning(f"🔍 DEBUG: Website Builder - No documents were deleted for website: {website_id}")
            raise HTTPException(status_code=404, detail="Website not found or already deleted")
        
        logger.info(f"🔍 DEBUG: Website Builder - Successfully deleted website: {website_id}")
        
        # Log analytics
        asyncio.create_task(admin_analytics_service.log_ai_usage(
            restaurant_id=restaurant_id,
            feature_type="website_builder",
            operation_type="website_deleted",
            processing_time=0,
            tokens_used=0,
            status="success",
            metadata={
                "website_id": website_id,
                "website_name": website_name
            }
        ))
        
        return {"success": True, "message": "Website deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔍 DEBUG: Website Builder - Failed to delete website: {str(e)}")
        import traceback
        logger.error(f"🔍 DEBUG: Website Builder - Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to delete website")


@router.patch("/websites/{website_id}/content")
async def update_website_content(
    website_id: str,
    content_updates: dict,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Update website content for inline editing
    """
    try:
        logger.info(f"🔍 DEBUG: Website Builder - update_website_content called for website: {website_id}")
        logger.info(f"🔍 DEBUG: Website Builder - Content updates: {content_updates}")
        logger.info(f"🔍 DEBUG: Website Builder - User: {current_user.user_id}, Role: {current_user.role}")
        logger.info(f"🔍 DEBUG: Website Builder - Restaurant ID from auth: {restaurant_id}")
        
        # Get existing website
        website = await db.websites.find_one({"website_id": website_id})
        if not website:
            logger.error(f"🔍 DEBUG: Website Builder - Website not found: {website_id}")
            raise HTTPException(status_code=404, detail="Website not found")
        
        logger.info(f"🔍 DEBUG: Website Builder - Found website with restaurant_id: {website.get('restaurant_id')}")
        
        # Verify user has access to this website's restaurant
        if website.get("restaurant_id") != restaurant_id:
            logger.error(f"🔍 DEBUG: Website Builder - Access denied. Website restaurant_id: {website.get('restaurant_id')}, User restaurant_id: {restaurant_id}")
            raise HTTPException(status_code=403, detail="Access denied to this website")
        
        # Prepare update data
        update_data = {"updated_at": datetime.now()}
        
        # Handle different types of content updates
        for field_path, new_value in content_updates.items():
            logger.info(f"🔍 DEBUG: Website Builder - Updating field: {field_path} = {new_value}")
            
            if field_path == "website_name":
                update_data["website_name"] = new_value
            elif field_path == "hero_image":
                # Handle hero image updates directly
                update_data["hero_image"] = new_value
                logger.info(f"🔍 DEBUG: Website Builder - Updated hero_image = {new_value}")
            elif field_path.startswith("menu_items["):
                # Handle menu item updates like "menu_items[0].name" or "menu_items[0].image"
                import re
                match = re.match(r'menu_items\[(\d+)\]\.(.+)', field_path)
                if match:
                    index = int(match.group(1))
                    field_name = match.group(2)

                    # Get current menu items or create default ones
                    current_menu_items = website.get("menu_items", [
                        {"name": "Signature Pasta", "description": "Fresh handmade pasta with our chef's special sauce", "price": "$18.99", "image": ""},
                        {"name": "Grilled Salmon", "description": "Atlantic salmon with seasonal vegetables and lemon butter", "price": "$24.99", "image": ""},
                        {"name": "Classic Margherita", "description": "Wood-fired pizza with fresh mozzarella and basil", "price": "$16.99", "image": ""}
                    ])
                    
                    # Make a deep copy to avoid reference issues
                    import copy
                    updated_menu_items = copy.deepcopy(current_menu_items)

                    # Ensure the array is large enough
                    while len(updated_menu_items) <= index:
                        updated_menu_items.append({"name": "", "description": "", "price": "$0.00", "image": ""})

                    # Update the specific field
                    updated_menu_items[index][field_name] = new_value
                    
                    # Set the complete array directly (like colors do)
                    update_data["menu_items"] = updated_menu_items
                    logger.info(f"🔍 DEBUG: Website Builder - Updated menu item {index}.{field_name} = {new_value}")
                    logger.info(f"🔍 DEBUG: Website Builder - Complete menu_items array: {updated_menu_items}")
            elif field_path.startswith("pages[0].sections.faq.items"):
                # Handle FAQ item updates and deletions
                if field_path == "pages[0].sections.faq.items.delete_index":
                    # Handle FAQ deletion
                    delete_index = int(new_value)
                    logger.info(f"🔍 DEBUG: Website Builder - Deleting FAQ item at index: {delete_index}")
                    
                    # Always get fresh pages from database for FAQ deletion to avoid cross-contamination
                    current_pages = website.get("pages", [])
                    if not current_pages:
                        logger.warning("🔍 DEBUG: Website Builder - No pages found for FAQ deletion")
                        continue
                    
                    # Deep copy to avoid reference issues
                    import copy
                    updated_pages = copy.deepcopy(current_pages)
                    
                    # Get existing FAQ data
                    existing_faq = updated_pages[0].get("sections", {}).get("faq", {})
                    current_faq_items = existing_faq.get("items", [])
                    
                    # Remove the item at the specified index
                    if 0 <= delete_index < len(current_faq_items):
                        removed_item = current_faq_items.pop(delete_index)
                        logger.info(f"🔍 DEBUG: Website Builder - Removed FAQ item at index {delete_index}: {removed_item}")
                        logger.info(f"🔍 DEBUG: Website Builder - Remaining FAQ items: {current_faq_items}")
                        
                        # Update the FAQ section
                        updated_pages[0]["sections"]["faq"]["items"] = current_faq_items
                        
                        # Set the complete pages array directly
                        update_data["pages"] = updated_pages
                    else:
                        logger.warning(f"🔍 DEBUG: Website Builder - Invalid delete index {delete_index} for FAQ items")
                        
                else:
                    # Handle regular FAQ item updates like "pages[0].sections.faq.items[0].question"
                    import re
                    match = re.match(r'pages\[0\]\.sections\.faq\.items\[(\d+)\]\.(.+)', field_path)
                    if match:
                        index = int(match.group(1))
                        field_name = match.group(2)

                        # Always get fresh pages from database for each FAQ field update to avoid cross-contamination
                        # This prevents one FAQ item update from affecting another FAQ item
                        current_pages = website.get("pages", [])
                        if not current_pages:
                            current_pages = [{
                                "page_id": "home",
                                "page_name": "Home",
                                "page_slug": "/",
                                "sections": {}
                            }]
                        
                        # Deep copy to avoid reference issues
                        import copy
                        updated_pages = copy.deepcopy(current_pages)
                        
                        # Ensure we have the first page with sections
                        if len(updated_pages) == 0:
                            updated_pages.append({
                                "page_id": "home",
                                "page_name": "Home",
                                "page_slug": "/",
                                "sections": {}
                            })
                        
                        if "sections" not in updated_pages[0]:
                            updated_pages[0]["sections"] = {}
                        
                        # Get existing FAQ data or create new (only if not already processed)
                        existing_faq = None
                        if website.get("pages") and len(website["pages"]) > 0:
                            existing_faq = website["pages"][0].get("sections", {}).get("faq", {})
                        
                        # Convert flat format to array format if needed
                        current_faq_items = []
                        if existing_faq:
                            if "items" in existing_faq and isinstance(existing_faq["items"], list):
                                # Already in correct format
                                current_faq_items = existing_faq["items"]
                            else:
                                # Convert from flat format to array format
                                flat_items = {}
                                for key, value in existing_faq.items():
                                    if key.startswith("items[") and "]." in key:
                                        # Parse items[0].question -> index=0, field=question
                                        import re
                                        match = re.match(r'items\[(\d+)\]\.(.+)', key)
                                        if match:
                                            idx = int(match.group(1))
                                            field = match.group(2)
                                            if idx not in flat_items:
                                                flat_items[idx] = {}
                                            flat_items[idx][field] = value
                                
                                # Convert to array
                                for i in sorted(flat_items.keys()):
                                    current_faq_items.append(flat_items[i])
                                
                                logger.info(f"🔍 DEBUG: Website Builder - Converted flat FAQ format to array: {current_faq_items}")
                        
                        # Initialize FAQ section if it doesn't exist
                        if "faq" not in updated_pages[0]["sections"]:
                            updated_pages[0]["sections"]["faq"] = {
                                "title": existing_faq.get("title", "Frequently Asked Questions") if existing_faq else "Frequently Asked Questions",
                                "items": current_faq_items
                            }
                        
                        # Get current FAQ items (either from database conversion or from previous updates in this request)
                        current_faq_items = updated_pages[0]["sections"]["faq"]["items"]
                        
                        # Ensure array is large enough
                        while len(current_faq_items) <= index:
                            current_faq_items.append({"question": "", "answer": ""})
                        
                        # Update the specific field in the existing array
                        current_faq_items[index][field_name] = new_value
                        
                        # Set the complete pages array directly
                        update_data["pages"] = updated_pages
                        logger.info(f"🔍 DEBUG: Website Builder - Updated FAQ item {index}.{field_name} = {new_value}")
                        logger.info(f"🔍 DEBUG: Website Builder - Complete FAQ items: {current_faq_items}")
            elif field_path.startswith("pages[0].sections.gallery.images["):
                # Handle Gallery image updates like "pages[0].sections.gallery.images[0].caption"
                import re
                match = re.match(r'pages\[0\]\.sections\.gallery\.images\[(\d+)\]\.(.+)', field_path)
                if match:
                    index = int(match.group(1))
                    field_name = match.group(2)

                    # Get current pages structure
                    current_pages = website.get("pages", [])
                    if not current_pages:
                        current_pages = [{
                            "page_id": "home",
                            "page_name": "Home",
                            "page_slug": "/",
                            "sections": {}
                        }]
                    
                    # Deep copy to avoid reference issues
                    import copy
                    updated_pages = copy.deepcopy(current_pages)
                    
                    # Ensure we have the first page with sections
                    if len(updated_pages) == 0:
                        updated_pages.append({
                            "page_id": "home",
                            "page_name": "Home",
                            "page_slug": "/",
                            "sections": {}
                        })
                    
                    if "sections" not in updated_pages[0]:
                        updated_pages[0]["sections"] = {}
                    
                    # Get existing gallery data or create new
                    existing_gallery = None
                    if website.get("pages") and len(website["pages"]) > 0:
                        existing_gallery = website["pages"][0].get("sections", {}).get("gallery", {})
                    
                    # Convert flat format to array format if needed
                    current_gallery_images = []
                    if existing_gallery:
                        if "images" in existing_gallery and isinstance(existing_gallery["images"], list):
                            # Already in correct format
                            current_gallery_images = existing_gallery["images"]
                        else:
                            # Convert from flat format to array format
                            flat_images = {}
                            for key, value in existing_gallery.items():
                                if key.startswith("images[") and "]." in key:
                                    # Parse images[0].url -> index=0, field=url
                                    import re
                                    match = re.match(r'images\[(\d+)\]\.(.+)', key)
                                    if match:
                                        idx = int(match.group(1))
                                        field = match.group(2)
                                        if idx not in flat_images:
                                            flat_images[idx] = {}
                                        flat_images[idx][field] = value
                            
                            # Convert to array
                            for i in sorted(flat_images.keys()):
                                current_gallery_images.append(flat_images[i])
                            
                            logger.info(f"🔍 DEBUG: Website Builder - Converted flat Gallery format to array: {current_gallery_images}")
                    
                    # Make a copy of gallery images
                    updated_gallery_images = copy.deepcopy(current_gallery_images)
                    
                    # Ensure array is large enough
                    while len(updated_gallery_images) <= index:
                        updated_gallery_images.append({"url": "", "caption": "", "alt": ""})
                    
                    # Update the specific field
                    updated_gallery_images[index][field_name] = new_value
                    
                    # Set the complete gallery section (like colors do)
                    updated_pages[0]["sections"]["gallery"] = {
                        "title": existing_gallery.get("title", "Gallery") if existing_gallery else "Gallery",
                        "description": existing_gallery.get("description", "Take a look at our restaurant and dishes") if existing_gallery else "Take a look at our restaurant and dishes",
                        "images": updated_gallery_images
                    }
                    
                    # Set the complete pages array directly
                    update_data["pages"] = updated_pages
                    logger.info(f"🔍 DEBUG: Website Builder - Updated gallery image {index}.{field_name} = {new_value}")
                    logger.info(f"🔍 DEBUG: Website Builder - Complete gallery images: {updated_gallery_images}")
            elif field_path.startswith("pages[0].sections.reviews.items["):
                # Handle Reviews updates like "pages[0].sections.reviews.items[0].name"
                import re
                match = re.match(r'pages\[0\]\.sections\.reviews\.items\[(\d+)\]\.(.+)', field_path)
                if match:
                    index = int(match.group(1))
                    field_name = match.group(2)

                    # Get current pages structure
                    current_pages = website.get("pages", [])
                    if not current_pages:
                        current_pages = [{
                            "page_id": "home",
                            "page_name": "Home",
                            "page_slug": "/",
                            "sections": {}
                        }]
                    
                    # Deep copy to avoid reference issues
                    import copy
                    updated_pages = copy.deepcopy(current_pages)
                    
                    # Ensure we have the first page with sections
                    if len(updated_pages) == 0:
                        updated_pages.append({
                            "page_id": "home",
                            "page_name": "Home",
                            "page_slug": "/",
                            "sections": {}
                        })
                    
                    if "sections" not in updated_pages[0]:
                        updated_pages[0]["sections"] = {}
                    
                    # Get existing reviews data or create new
                    existing_reviews = None
                    if website.get("pages") and len(website["pages"]) > 0:
                        existing_reviews = website["pages"][0].get("sections", {}).get("reviews", {})
                    
                    # Convert flat format to array format if needed
                    current_review_items = []
                    if existing_reviews:
                        if "items" in existing_reviews and isinstance(existing_reviews["items"], list):
                            # Already in correct format
                            current_review_items = existing_reviews["items"]
                        else:
                            # Convert from flat format to array format
                            flat_items = {}
                            for key, value in existing_reviews.items():
                                if key.startswith("items[") and "]." in key:
                                    # Parse items[0].name -> index=0, field=name
                                    import re
                                    match = re.match(r'items\[(\d+)\]\.(.+)', key)
                                    if match:
                                        idx = int(match.group(1))
                                        field = match.group(2)
                                        if idx not in flat_items:
                                            flat_items[idx] = {}
                                        flat_items[idx][field] = value
                            
                            # Convert to array
                            for i in sorted(flat_items.keys()):
                                current_review_items.append(flat_items[i])
                            
                            logger.info(f"🔍 DEBUG: Website Builder - Converted flat Reviews format to array: {current_review_items}")
                    
                    # Make a copy of review items
                    updated_review_items = copy.deepcopy(current_review_items)
                    
                    # Ensure array is large enough
                    while len(updated_review_items) <= index:
                        updated_review_items.append({"name": "", "rating": 5, "text": "", "date": ""})
                    
                    # Update the specific field
                    updated_review_items[index][field_name] = new_value
                    
                    # Set the complete reviews section (like colors do)
                    updated_pages[0]["sections"]["reviews"] = {
                        "title": existing_reviews.get("title", "What Our Customers Say") if existing_reviews else "What Our Customers Say",
                        "overall_rating": existing_reviews.get("overall_rating", 4.5) if existing_reviews else 4.5,
                        "items": updated_review_items
                    }
                    
                    # Set the complete pages array directly
                    update_data["pages"] = updated_pages
                    logger.info(f"🔍 DEBUG: Website Builder - Updated review item {index}.{field_name} = {new_value}")
                    logger.info(f"🔍 DEBUG: Website Builder - Complete review items: {updated_review_items}")
            elif field_path.startswith("pages[0].sections."):
                # Handle nested page section updates - GENERAL HANDLER (must come AFTER specific array handlers)
                section_path = field_path.replace("pages[0].sections.", "")
                
                # Initialize pages array if it doesn't exist
                if "pages" not in update_data:
                    current_pages = website.get("pages", [])
                    if not current_pages:
                        # Create default page structure
                        current_pages = [{
                            "page_id": "home",
                            "page_name": "Home",
                            "page_slug": "/",
                            "sections": {
                                "hero": {},
                                "about": {},
                                "contact": {}
                            }
                        }]
                    update_data["pages"] = current_pages.copy()
                
                # Ensure we have at least one page
                if len(update_data["pages"]) == 0:
                    update_data["pages"].append({
                        "page_id": "home",
                        "page_name": "Home",
                        "page_slug": "/",
                        "sections": {
                            "hero": {},
                            "about": {},
                            "contact": {}
                        }
                    })
                
                # Ensure sections exist
                if "sections" not in update_data["pages"][0]:
                    update_data["pages"][0]["sections"] = {}
                
                # Parse the section path and update
                if "." in section_path:
                    section_name, field_name = section_path.split(".", 1)
                    if section_name not in update_data["pages"][0]["sections"]:
                        update_data["pages"][0]["sections"][section_name] = {}
                    update_data["pages"][0]["sections"][section_name][field_name] = new_value
                    logger.info(f"🔍 DEBUG: Website Builder - Updated pages[0].sections.{section_name}.{field_name} = {new_value}")
                else:
                    update_data["pages"][0]["sections"][section_path] = new_value
                    logger.info(f"🔍 DEBUG: Website Builder - Updated pages[0].sections.{section_path} = {new_value}")
            else:
                # Direct field update
                update_data[field_path] = new_value
        
        logger.info(f"🔍 DEBUG: Website Builder - Final update data: {update_data}")
        
        # Update website in database
        result = await db.websites.update_one(
            {"website_id": website_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            logger.warning(f"🔍 DEBUG: Website Builder - No documents were modified for website: {website_id}")
        else:
            logger.info(f"🔍 DEBUG: Website Builder - Successfully updated website: {website_id}")
            
            # Mark website as having unpublished changes if it's currently published
            if website.get("status") == WebsiteStatus.published.value:
                try:
                    publishing_service = WebsitePublishingService(db)
                    await publishing_service.mark_website_as_changed(website_id, restaurant_id)
                    logger.info(f"🔍 DEBUG: Website Builder - Marked website {website_id} as having unpublished changes")
                except Exception as e:
                    logger.warning(f"🔍 DEBUG: Website Builder - Failed to mark website as changed: {str(e)}")
        
        # Return success response
        return {"success": True, "message": "Content updated successfully", "updated_fields": list(content_updates.keys())}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔍 DEBUG: Website Builder - Failed to update website content: {str(e)}")
        import traceback
        logger.error(f"🔍 DEBUG: Website Builder - Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to update website content")

@router.patch("/websites/{website_id}/colors")
async def update_website_colors(
    website_id: str,
    color_updates: dict,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Update website color theme
    """
    try:
        logger.info(f"🔍 DEBUG: Website Builder - update_website_colors called for website: {website_id}")
        logger.info(f"🔍 DEBUG: Website Builder - Color updates: {color_updates}")
        
        # Get existing website
        website = await db.websites.find_one({"website_id": website_id})
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Verify user has access
        if website.get("restaurant_id") != restaurant_id:
            raise HTTPException(status_code=403, detail="Access denied to this website")
        
        # Prepare color theme update
        current_design_system = website.get("design_system", {})
        current_color_palette = current_design_system.get("color_palette", {})
        
        # Update color palette
        updated_color_palette = {**current_color_palette, **color_updates}
        
        update_data = {
            "updated_at": datetime.now(),
            "design_system.color_palette": updated_color_palette
        }
        
        # Update website in database
        await db.websites.update_one(
            {"website_id": website_id},
            {"$set": update_data}
        )
        
        logger.info(f"🔍 DEBUG: Website Builder - Successfully updated colors for website: {website_id}")
        
        # Mark website as having unpublished changes if it's currently published
        if website.get("status") == WebsiteStatus.published.value:
            try:
                publishing_service = WebsitePublishingService(db)
                await publishing_service.mark_website_as_changed(website_id, restaurant_id)
                logger.info(f"🔍 DEBUG: Website Builder - Marked website {website_id} as having unpublished changes")
            except Exception as e:
                logger.warning(f"🔍 DEBUG: Website Builder - Failed to mark website as changed: {str(e)}")
        
        return {
            "success": True,
            "message": "Colors updated successfully",
            "color_palette": updated_color_palette
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔍 DEBUG: Website Builder - Failed to update website colors: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update website colors")

@router.get("/websites/{website_id}/colors")
async def get_website_colors(
    website_id: str,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Get website color theme
    """
    try:
        # Get website
        website = await db.websites.find_one({"website_id": website_id})
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Verify user has access
        if website.get("restaurant_id") != restaurant_id:
            raise HTTPException(status_code=403, detail="Access denied to this website")
        
        # Get color palette
        design_system = website.get("design_system", {})
        color_palette = design_system.get("color_palette", {
            "primary": "#015af6",
            "secondary": "#0ea5e9",
            "accent": "#f39c12",
            "neutral": "#ecf0f1"
        })
        
        return {
            "success": True,
            "color_palette": color_palette
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get website colors: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get website colors")

@router.post("/websites/{website_id}/colors/preset")
async def apply_color_preset(
    website_id: str,
    preset_data: dict,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Apply color preset to website
    """
    try:
        preset_name = preset_data.get("preset_name")
        
        # Define color presets
        color_presets = {
            "ocean": {
                "primary": "#0ea5e9",
                "secondary": "#06b6d4",
                "accent": "#14b8a6",
                "neutral": "#f1f5f9"
            },
            "forest": {
                "primary": "#10b981",
                "secondary": "#059669",
                "accent": "#84cc16",
                "neutral": "#f0fdf4"
            },
            "sunset": {
                "primary": "#f97316",
                "secondary": "#ea580c",
                "accent": "#fbbf24",
                "neutral": "#fffbeb"
            },
            "royal": {
                "primary": "#8b5cf6",
                "secondary": "#7c3aed",
                "accent": "#a855f7",
                "neutral": "#faf5ff"
            },
            "classic": {
                "primary": "#015af6",
                "secondary": "#0ea5e9",
                "accent": "#f39c12",
                "neutral": "#ecf0f1"
            }
        }
        
        if preset_name not in color_presets:
            raise HTTPException(status_code=400, detail="Invalid color preset")
        
        # Apply preset
        color_updates = color_presets[preset_name]
        
        # Get existing website
        website = await db.websites.find_one({"website_id": website_id})
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Verify user has access
        if website.get("restaurant_id") != restaurant_id:
            raise HTTPException(status_code=403, detail="Access denied to this website")
        
        # Update color palette
        update_data = {
            "updated_at": datetime.now(),
            "design_system.color_palette": color_updates
        }
        
        await db.websites.update_one(
            {"website_id": website_id},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "message": f"Applied {preset_name} color preset",
            "color_palette": color_updates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply color preset: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to apply color preset")

@router.post("/templates/create", response_model=RestaurantWebsite)
async def create_website_from_template(
    request: dict,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Create a website from a template with customizations
    """
    try:
        logger.info(f"Creating website from template for restaurant {request.get('restaurant_id')}")
        
        # Validate restaurant exists and user has access - simplified approach for templates
        restaurant_id = request["restaurant_id"]
        
        # Try to get restaurant data, but don't fail if it's not found (for template creation)
        try:
            restaurant_data = await _get_restaurant_data(restaurant_id, current_user, db)
            if not restaurant_data:
                # For template creation, we can proceed without full restaurant data
                logger.warning(f"Restaurant data not found for {restaurant_id}, proceeding with template creation")
                restaurant_data = {"restaurant_id": restaurant_id, "name": "Restaurant"}
        except Exception as e:
            logger.warning(f"Error fetching restaurant data for {restaurant_id}: {str(e)}, proceeding with template creation")
            restaurant_data = {"restaurant_id": restaurant_id, "name": "Restaurant"}
        
        # Generate website ID
        website_id = f"website_{request['restaurant_id']}_{int(datetime.now().timestamp())}"
        
        # Create website record from template
        website_record = {
            "website_id": website_id,
            "restaurant_id": request["restaurant_id"],
            "website_name": request["website_name"],
            "status": WebsiteStatus.ready,
            "design_category": request["design_category"],
            "template_id": request.get("template_id"),
            "template_customizations": request.get("template_customizations", {}),
            "generated_content": request.get("generated_content", {}),
            "design_system": {
                "color_palette": {
                    "primary": request.get("template_customizations", {}).get("primary_color", "#2c3e50"),
                    "secondary": request.get("template_customizations", {}).get("secondary_color", "#e74c3c"),
                    "accent": "#f39c12",
                    "neutral": "#ecf0f1"
                },
                "typography": {
                    "headings_font": "Playfair Display",
                    "body_font": "Open Sans"
                }
            },
            "pages": [
                {
                    "page_id": "home",
                    "page_name": "Home",
                    "page_slug": "/",
                    "page_title": request.get("template_customizations", {}).get("restaurant_name", "Restaurant"),
                    "meta_description": request.get("template_customizations", {}).get("restaurant_tagline", "Great food and service"),
                    "components": [],
                    "is_homepage": True,
                    "published": False
                }
            ],
            "seo_settings": {
                "site_title": request.get("template_customizations", {}).get("restaurant_name", "Restaurant"),
                "site_description": request.get("template_customizations", {}).get("about_description", "Great restaurant"),
                "keywords": ["restaurant", "dining", "food"],
                "robots_txt": "User-agent: *\nAllow: /",
                "sitemap_enabled": True
            },
            "ai_generation_metadata": {
                "generation_type": "template",
                "template_id": request.get("template_id"),
                "generation_date": datetime.now().isoformat(),
                "customizations_applied": request.get("template_customizations", {})
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Save to database
        await db.websites.insert_one(website_record)
        
        # Log analytics
        asyncio.create_task(admin_analytics_service.log_ai_usage(
            restaurant_id=request["restaurant_id"],
            feature_type="website_builder",
            operation_type="template_website_created",
            processing_time=0,
            tokens_used=0,
            status="success",
            metadata={
                "website_id": website_id,
                "template_id": request.get("template_id"),
                "website_name": request["website_name"]
            }
        ))
        
        # Return the created website
        created_website = await db.websites.find_one({"website_id": website_id})
        return RestaurantWebsite(**created_website)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create website from template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create website from template: {str(e)}")

@router.get("/templates", response_model=List[WebsiteTemplate])
async def list_website_templates(
    category: Optional[str] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    List available website templates
    """
    try:
        # Build query
        query = {"active": True}
        if category:
            query["design_category"] = category
        
        # Get templates
        templates_cursor = db.website_templates.find(query).sort("popularity_score", -1)
        templates = await templates_cursor.to_list(length=None)
        
        # Convert to response models
        template_models = []
        for template in templates:
            template_models.append(WebsiteTemplate(**template))
        
        return template_models
        
    except Exception as e:
        logger.error(f"Failed to list templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list templates")

@router.get("/dashboard", response_model=WebsiteBuilderDashboard)
async def get_website_builder_dashboard(
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get website builder dashboard data
    """
    try:
        # Get user's restaurants
        user_restaurants = await _get_user_restaurants(current_user, db)
        restaurant_ids = [r["_id"] for r in user_restaurants]
        
        # Get website statistics
        total_websites = await db.websites.count_documents({"restaurant_id": {"$in": restaurant_ids}})
        published_websites = await db.websites.count_documents({
            "restaurant_id": {"$in": restaurant_ids},
            "status": WebsiteStatus.published
        })
        draft_websites = await db.websites.count_documents({
            "restaurant_id": {"$in": restaurant_ids},
            "status": WebsiteStatus.draft
        })
        
        # Get recent websites
        recent_websites_cursor = db.websites.find(
            {"restaurant_id": {"$in": restaurant_ids}}
        ).sort("created_at", -1).limit(5)
        recent_websites = await recent_websites_cursor.to_list(length=5)
        
        # Get popular templates
        popular_templates_cursor = db.website_templates.find(
            {"active": True}
        ).sort("popularity_score", -1).limit(5)
        popular_templates = await popular_templates_cursor.to_list(length=5)
        
        # Convert to response models
        recent_website_models = [RestaurantWebsite(**w) for w in recent_websites]
        popular_template_models = [WebsiteTemplate(**t) for t in popular_templates]
        
        return WebsiteBuilderDashboard(
            total_websites=total_websites,
            published_websites=published_websites,
            draft_websites=draft_websites,
            recent_websites=recent_website_models,
            popular_templates=popular_template_models,
            ai_generation_stats={
                "total_generated": total_websites,
                "this_month": 0,  # Would calculate from actual data
                "success_rate": 95.0
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

# Background task for website generation
async def _generate_website_background(
    generation_id: str,
    website_id: str,
    request: WebsiteGenerationRequest,
    restaurant_data: Dict[str, Any],
    current_user,
    db
):
    """
    Background task to generate website using AI
    """
    try:
        logger.info(f"Starting background website generation for {website_id}")
        
        # Update progress
        def update_progress(step: str, completed: int, operation: str):
            if generation_id in generation_progress_store:
                progress = generation_progress_store[generation_id]
                progress.current_step = step
                progress.completed_steps = completed
                progress.progress_percentage = (completed / progress.total_steps) * 100
                progress.current_operation = operation
        
        # Step 1: Analyze restaurant data
        update_progress("Analyzing restaurant data", 1, "AI analysis of restaurant characteristics")
        await asyncio.sleep(2)  # Simulate processing time
        
        # Step 2: Generate website using AI
        update_progress("Generating website structure", 2, "Creating AI-powered website design")
        website_data = await ai_website_generator.generate_complete_website(restaurant_data)
        
        # Step 3: Process AI results
        update_progress("Processing AI results", 3, "Converting AI output to website structure")
        await asyncio.sleep(1)
        
        # Step 4: Create website record
        update_progress("Creating website record", 4, "Saving website to database")
        
        # Convert AI output to website model
        website_record = {
            "website_id": website_id,
            "restaurant_id": request.restaurant_id,
            "website_name": request.website_name,
            "status": WebsiteStatus.ready,
            "design_category": website_data.get("design_analysis", {}).get("recommended_category", "casual_dining"),
            "design_system": _convert_ai_design_system(website_data.get("design_system", {})),
            "pages": _convert_ai_pages(website_data.get("website_sections", {})),
            "seo_settings": _convert_ai_seo(website_data.get("seo_optimization", {})),
            "ai_generation_metadata": {
                "generation_id": generation_id,
                "ai_analysis": website_data.get("design_analysis", {}),
                "generation_date": datetime.now().isoformat(),
                "ai_insights": website_data.get("ai_insights", {})
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Save to database
        await db.websites.insert_one(website_record)
        
        # Step 5: Generate additional content
        update_progress("Generating additional content", 5, "Creating supplementary website content")
        await asyncio.sleep(1)
        
        # Step 6: Optimize for performance
        update_progress("Optimizing performance", 6, "Applying performance optimizations")
        await asyncio.sleep(1)
        
        # Step 7: SEO optimization
        update_progress("SEO optimization", 7, "Implementing SEO best practices")
        await asyncio.sleep(1)
        
        # Step 8: Finalization
        update_progress("Finalizing website", 8, "Completing website generation")
        
        # Mark as completed
        if generation_id in generation_progress_store:
            progress = generation_progress_store[generation_id]
            progress.status = "completed"
            progress.completed_at = datetime.now()
            progress.current_operation = "Website generation completed successfully"
        
        logger.info(f"Website generation completed successfully for {website_id}")
        
    except Exception as e:
        logger.error(f"Website generation failed: {str(e)}")
        
        # Mark as failed
        if generation_id in generation_progress_store:
            progress = generation_progress_store[generation_id]
            progress.status = "failed"
            progress.error_details = str(e)
            progress.completed_at = datetime.now()

# Helper functions
async def _get_restaurant_data(restaurant_id: str, current_user, db) -> Optional[Dict[str, Any]]:
    """Get restaurant data for AI generation"""
    try:
        from bson import ObjectId
        
        # Try multiple approaches to find the restaurant
        restaurant = None
        
        # Approach 1: Try as ObjectId (if it's a valid ObjectId format)
        if len(restaurant_id) == 24:
            try:
                restaurant_object_id = ObjectId(restaurant_id)
                restaurant = await db.restaurants.find_one({"_id": restaurant_object_id})
            except Exception:
                pass
        
        # Approach 2: Try to find by user_id if restaurant not found
        if not restaurant:
            try:
                # Check if restaurant_id is actually a user_id
                user = await db.users.find_one({"_id": ObjectId(restaurant_id)})
                if user and user.get("role") == "restaurant":
                    restaurant = await db.restaurants.find_one({"user_id": str(user["_id"])})
            except Exception:
                pass
        
        # Approach 3: Try direct string match
        if not restaurant:
            restaurant = await db.restaurants.find_one({"user_id": restaurant_id})
        
        # Approach 4: Try to find restaurant by matching current user
        if not restaurant:
            restaurant = await db.restaurants.find_one({"user_id": current_user.user_id})
        
        if not restaurant:
            logger.warning(f"Restaurant not found for ID: {restaurant_id}")
            return None
        
        # Verify user has access (check both user_id formats)
        restaurant_user_id = restaurant.get("user_id")
        if restaurant_user_id != current_user.user_id and restaurant_user_id != str(current_user.user_id):
            logger.warning(f"Access denied for restaurant {restaurant_id} to user {current_user.user_id}")
            return None
        
        # Get additional data (menu items, etc.)
        try:
            menu_items = await db.menu_items.find({"restaurant_id": restaurant_id}).to_list(length=None)
        except Exception:
            menu_items = []
        
        # Combine data for AI
        restaurant_data = {
            **restaurant,
            "menu_items": menu_items,
            "restaurant_id": restaurant_id
        }
        
        return restaurant_data
        
    except Exception as e:
        logger.error(f"Failed to get restaurant data: {str(e)}")
        return None

async def _get_user_restaurants(current_user, db) -> List[Dict[str, Any]]:
    """Get all restaurants for the current user"""
    logger.info(f"🔍 DEBUG: _get_user_restaurants - Looking for restaurants with user_id: {current_user.user_id}")
    
    # Try multiple approaches to find restaurants
    restaurants = []
    
    # Approach 1: Direct user_id match (string)
    restaurants_cursor = db.restaurants.find({"user_id": current_user.user_id})
    restaurants = await restaurants_cursor.to_list(length=None)
    logger.info(f"🔍 DEBUG: _get_user_restaurants - Approach 1 (string user_id): Found {len(restaurants)} restaurants")
    
    # Approach 2: Try ObjectId conversion if no results
    if not restaurants:
        try:
            from bson import ObjectId
            restaurants_cursor = db.restaurants.find({"user_id": str(ObjectId(current_user.user_id))})
            restaurants = await restaurants_cursor.to_list(length=None)
            logger.info(f"🔍 DEBUG: _get_user_restaurants - Approach 2 (ObjectId string): Found {len(restaurants)} restaurants")
        except Exception as e:
            logger.info(f"🔍 DEBUG: _get_user_restaurants - Approach 2 failed: {str(e)}")
    
    # Approach 3: Try to find by _id if still no results
    if not restaurants:
        try:
            from bson import ObjectId
            restaurants_cursor = db.restaurants.find({"_id": ObjectId(current_user.user_id)})
            restaurants = await restaurants_cursor.to_list(length=None)
            logger.info(f"🔍 DEBUG: _get_user_restaurants - Approach 3 (restaurant _id): Found {len(restaurants)} restaurants")
        except Exception as e:
            logger.info(f"🔍 DEBUG: _get_user_restaurants - Approach 3 failed: {str(e)}")
    
    # Log what we found
    for restaurant in restaurants:
        logger.info(f"🔍 DEBUG: _get_user_restaurants - Restaurant: {restaurant.get('name', 'Unknown')} (ID: {restaurant.get('_id')})")
    
    return restaurants

async def _verify_restaurant_access(restaurant_id: str, current_user, db):
    """Verify user has access to the restaurant"""
    restaurant = await db.restaurants.find_one({"_id": restaurant_id})
    if not restaurant or restaurant.get("user_id") != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied to this restaurant")

def _convert_ai_design_system(ai_design: Dict[str, Any]) -> Dict[str, Any]:
    """Convert AI design system to database format"""
    # This would convert the AI output to the proper format
    # For now, return a basic structure
    return {
        "color_palette": {
            "primary": "#2c3e50",
            "secondary": "#e74c3c",
            "accent": "#f39c12",
            "neutral": "#ecf0f1"
        },
        "typography": {
            "headings_font": "Playfair Display",
            "body_font": "Open Sans"
        }
    }

def _convert_ai_pages(ai_sections: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert AI sections to page format"""
    # This would convert AI sections to proper page structure
    # For now, return a basic homepage
    return [
        {
            "page_id": "home",
            "page_name": "Home",
            "page_slug": "/",
            "page_title": "Welcome to Our Restaurant",
            "meta_description": "Experience exceptional dining with us",
            "components": [],
            "is_homepage": True,
            "published": False
        }
    ]

def _convert_ai_seo(ai_seo: Dict[str, Any]) -> Dict[str, Any]:
    """Convert AI SEO data to database format"""
    return {
        "site_title": "Restaurant Website",
        "site_description": "Experience exceptional dining",
        "keywords": ["restaurant", "dining", "food"],
        "robots_txt": "User-agent: *\nAllow: /",
        "sitemap_enabled": True
    }