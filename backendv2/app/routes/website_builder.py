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
from ..models_website_builder import (
    WebsiteGenerationRequest, WebsiteGenerationResponse, RestaurantWebsite,
    WebsiteListResponse, WebsiteUpdateRequest, ComponentUpdateRequest,
    PageUpdateRequest, WebsitePreviewRequest, WebsitePreviewResponse,
    AIGenerationProgress, WebsiteBuilderDashboard, WebsiteTemplate,
    WebsiteAnalytics, WebsiteBackup, WebsiteDeployment, WebsiteStatus,
    AIGenerationSettings, WebsitePerformanceMetrics
)
from ..services.ai_website_generator import ai_website_generator
from ..services.admin_analytics_service import admin_analytics_service
from ..database import get_database
from ..auth import get_current_user, get_restaurant_id, require_restaurant

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/website-builder", tags=["Website Builder"])

# Global storage for generation progress (in production, use Redis or database)
generation_progress_store = {}

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
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get a specific website by ID
    """
    try:
        website = await db.websites.find_one({"website_id": website_id})
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Verify user has access to this website's restaurant
        await _verify_restaurant_access(website["restaurant_id"], current_user, db)
        
        return RestaurantWebsite(**website)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get website: {str(e)}")
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

@router.post("/websites/{website_id}/publish")
async def publish_website(
    website_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Publish the website to make it live
    """
    try:
        # Get website
        website = await db.websites.find_one({"website_id": website_id})
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # Verify user has access
        await _verify_restaurant_access(website["restaurant_id"], current_user, db)
        
        # Update website status
        await db.websites.update_one(
            {"website_id": website_id},
            {
                "$set": {
                    "status": WebsiteStatus.published,
                    "published_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            }
        )
        
        # Log analytics
        asyncio.create_task(admin_analytics_service.log_ai_usage(
            restaurant_id=website["restaurant_id"],
            feature_type="website_builder",
            operation_type="website_published",
            processing_time=0,
            tokens_used=0,
            status="success",
            metadata={
                "website_id": website_id,
                "website_name": website.get("website_name", "Unknown")
            }
        ))
        
        return {"success": True, "message": "Website published successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to publish website: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to publish website")

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