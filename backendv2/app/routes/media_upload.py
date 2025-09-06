"""
Media Upload API Routes
Handles image upload, optimization, and storage for website builder
"""
import os
import uuid
import logging
import io
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from PIL import Image, ImageOps
from ..auth import get_current_user, get_restaurant_id, require_restaurant
from ..database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/website-builder", tags=["Media Upload"])
logger.info("✅ Media Upload Router Loaded")

# Configuration - Use absolute path from current working directory
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "images")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
THUMBNAIL_SIZES = {
    'small': (150, 150),
    'medium': (300, 300),
    'large': (600, 600)
}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
logger.info(f"🔍 DEBUG: Media Upload - Upload directory set to: {UPLOAD_DIR}")

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    image_type: str = Form("general"),  # hero, about, menu_item, logo, general
    website_id: Optional[str] = Form(None)
    # Temporarily removed authentication for debugging
    # restaurant_id: str = Depends(get_restaurant_id),
    # current_user = Depends(require_restaurant),
    # db = Depends(get_database)
):
    """
    Upload and optimize image for website builder
    """
    try:
        # Use default restaurant_id for testing
        restaurant_id = "test_restaurant_id"
        
        logger.info(f"🔍 DEBUG: Media Upload - ===== UPLOAD STARTED =====")
        logger.info(f"🔍 DEBUG: Media Upload - Restaurant ID: {restaurant_id}")
        logger.info(f"🔍 DEBUG: Media Upload - File: {file.filename}, Type: {image_type}, Size: {file.size}")
        logger.info(f"🔍 DEBUG: Media Upload - Upload directory: {UPLOAD_DIR}")
        logger.info(f"🔍 DEBUG: Media Upload - Directory exists: {os.path.exists(UPLOAD_DIR)}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{image_type}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Read and validate image
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        try:
            # Open and validate image with PIL
            image = Image.open(io.BytesIO(contents))
            
            # Auto-rotate based on EXIF data
            image = ImageOps.exif_transpose(image)
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Optimize image based on type
            optimized_image = await optimize_image_for_type(image, image_type)
            
            # Save optimized image
            optimized_image.save(file_path, 'JPEG', quality=85, optimize=True)
            
            # Get image metadata
            width, height = optimized_image.size
            file_size = os.path.getsize(file_path)
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Generate URL
        image_url = f"/api/website-builder/images/{filename}"
        
        # Save to database
        image_record = {
            "image_id": file_id,
            "restaurant_id": restaurant_id,
            "website_id": website_id,
            "filename": filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "image_type": image_type,
            "url": image_url,
            "width": width,
            "height": height,
            "file_size": file_size,
            "mime_type": "image/jpeg",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Temporarily skip database save for debugging
        # await db.website_images.insert_one(image_record)
        
        logger.info(f"🔍 DEBUG: Media Upload - Image uploaded successfully: {filename}")
        logger.info(f"🔍 DEBUG: Media Upload - File saved to: {file_path}")
        logger.info(f"🔍 DEBUG: Media Upload - File exists after save: {os.path.exists(file_path)}")
        
        return {
            "success": True,
            "image_id": file_id,
            "filename": filename,
            "url": image_url,
            "width": width,
            "height": height,
            "file_size": file_size,
            "image_type": image_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Image upload failed")

@router.get("/images/{filename}")
async def get_image(filename: str):
    """
    Serve uploaded images
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        logger.info(f"🔍 DEBUG: Media Upload - Serving image: {filename}")
        logger.info(f"🔍 DEBUG: Media Upload - UPLOAD_DIR: {UPLOAD_DIR}")
        logger.info(f"🔍 DEBUG: Media Upload - Full file path: {file_path}")
        logger.info(f"🔍 DEBUG: Media Upload - File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            logger.error(f"🔍 DEBUG: Media Upload - Image not found at: {file_path}")
            # List what files are actually in the directory
            try:
                files_in_dir = os.listdir(UPLOAD_DIR)
                logger.info(f"🔍 DEBUG: Media Upload - Files in upload dir: {files_in_dir}")
            except Exception as e:
                logger.error(f"🔍 DEBUG: Media Upload - Could not list upload dir: {e}")
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Determine media type based on file extension
        file_ext = filename.lower().split('.')[-1]
        media_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'webp': 'image/webp',
            'gif': 'image/gif'
        }
        media_type = media_type_map.get(file_ext, 'image/jpeg')
        
        logger.info(f"🔍 DEBUG: Media Upload - Serving with media type: {media_type}")
        
        return FileResponse(
            file_path,
            media_type=media_type,
            headers={"Cache-Control": "public, max-age=31536000"}  # 1 year cache
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve image: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve image")

@router.get("/images/thumbnail/{filename}")
async def get_thumbnail(
    filename: str,
    size: str = "medium",
    format: str = "jpeg"
):
    """
    Generate and serve image thumbnails
    """
    try:
        # Validate size
        if size not in THUMBNAIL_SIZES:
            size = "medium"
        
        # Generate thumbnail filename
        thumb_filename = f"thumb_{size}_{filename}"
        thumb_path = os.path.join(UPLOAD_DIR, "thumbnails", thumb_filename)
        
        # Create thumbnails directory if it doesn't exist
        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
        
        # Check if thumbnail already exists
        if not os.path.exists(thumb_path):
            # Generate thumbnail
            original_path = os.path.join(UPLOAD_DIR, filename)
            
            if not os.path.exists(original_path):
                raise HTTPException(status_code=404, detail="Original image not found")
            
            # Create thumbnail
            with Image.open(original_path) as image:
                # Create thumbnail maintaining aspect ratio
                image.thumbnail(THUMBNAIL_SIZES[size], Image.Resampling.LANCZOS)
                
                # Save thumbnail
                if format.lower() == "webp":
                    image.save(thumb_path, "WEBP", quality=80, optimize=True)
                    media_type = "image/webp"
                else:
                    image.save(thumb_path, "JPEG", quality=80, optimize=True)
                    media_type = "image/jpeg"
        else:
            media_type = "image/webp" if format.lower() == "webp" else "image/jpeg"
        
        return FileResponse(
            thumb_path,
            media_type=media_type,
            headers={"Cache-Control": "public, max-age=31536000"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate thumbnail: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate thumbnail")

@router.delete("/images/{image_id}")
async def delete_image(
    image_id: str,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    Delete uploaded image
    """
    try:
        # Find image record
        image_record = await db.website_images.find_one({
            "image_id": image_id,
            "restaurant_id": restaurant_id
        })
        
        if not image_record:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Delete file from filesystem
        file_path = image_record.get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete thumbnails
        filename = image_record.get("filename")
        if filename:
            for size in THUMBNAIL_SIZES:
                thumb_filename = f"thumb_{size}_{filename}"
                thumb_path = os.path.join(UPLOAD_DIR, "thumbnails", thumb_filename)
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)
        
        # Delete from database
        await db.website_images.delete_one({"image_id": image_id})
        
        return {"success": True, "message": "Image deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete image: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete image")

@router.get("/images")
async def list_images(
    image_type: Optional[str] = None,
    website_id: Optional[str] = None,
    restaurant_id: str = Depends(get_restaurant_id),
    current_user = Depends(require_restaurant),
    db = Depends(get_database)
):
    """
    List uploaded images for restaurant
    """
    try:
        # Build query
        query = {"restaurant_id": restaurant_id}
        
        if image_type:
            query["image_type"] = image_type
        
        if website_id:
            query["website_id"] = website_id
        
        # Get images
        images_cursor = db.website_images.find(query).sort("created_at", -1)
        images = await images_cursor.to_list(length=None)
        
        # Format response
        formatted_images = []
        for image in images:
            formatted_images.append({
                "image_id": image["image_id"],
                "filename": image["filename"],
                "original_filename": image["original_filename"],
                "url": image["url"],
                "image_type": image["image_type"],
                "width": image["width"],
                "height": image["height"],
                "file_size": image["file_size"],
                "created_at": image["created_at"]
            })
        
        return {
            "success": True,
            "images": formatted_images,
            "total": len(formatted_images)
        }
        
    except Exception as e:
        logger.error(f"Failed to list images: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list images")

# Helper functions
async def optimize_image_for_type(image: Image.Image, image_type: str) -> Image.Image:
    """
    Optimize image based on its intended use
    """
    width, height = image.size
    
    # Define max dimensions for different image types
    max_dimensions = {
        'hero': (1920, 1080),
        'about': (800, 600),
        'menu_item': (600, 450),
        'logo': (400, 400),
        'general': (1200, 900)
    }
    
    max_width, max_height = max_dimensions.get(image_type, max_dimensions['general'])
    
    # Resize if necessary
    if width > max_width or height > max_height:
        # Calculate new dimensions maintaining aspect ratio
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return image
