import os
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

# Create router
router = APIRouter(prefix="/api/website-builder", tags=["Media Upload V2"])

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'uploads/images/'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename: str) -> str:
    """Simple filename sanitization"""
    # Remove path components and keep only the filename
    filename = os.path.basename(filename)
    # Replace any remaining problematic characters
    filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    return filename

@router.post("/upload-image-v2")
async def upload_image_v2(
    file: UploadFile = File(...),
    image_type: str = Form("general")
):
    logger.debug("Upload endpoint /api/website-builder/upload-image-v2 hit")
    
    if not file.filename:
        logger.error("No file provided")
        raise HTTPException(status_code=400, detail="No file provided")
        
    if not allowed_file(file.filename):
        logger.warning(f"File type not allowed: {file.filename}")
        raise HTTPException(status_code=400, detail="File type not allowed")
        
    try:
        # Read file content
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
            
        # Generate unique filename
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}_{image_type}.{file_ext}"
        
        # Ensure upload directory exists
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            logger.info(f"Created upload directory: {UPLOAD_FOLDER}")

        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        logger.debug(f"Attempting to save file to: {file_path}")
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(contents)
            
        logger.info(f"File saved successfully: {unique_filename}")
        
        # Construct the URL for the saved image
        image_url = f"/api/website-builder/images-v2/{unique_filename}"
        
        return {
            "message": "File uploaded successfully",
            "filename": unique_filename,
            "image_url": image_url
        }
        
    except Exception as e:
        logger.error(f"Error saving file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while saving the file")

@router.get("/images-v2/{filename}")
async def get_image_v2(filename: str):
    logger.debug(f"Serving image request for: {filename}")
    
    # Sanitize filename to prevent directory traversal attacks
    safe_filename = secure_filename(filename)
    if safe_filename != filename:
        logger.warning(f"Attempted access with unsafe filename: {filename}")
        raise HTTPException(status_code=404, detail="Not Found")
        
    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {safe_filename} in {UPLOAD_FOLDER}")
        # List what files are actually in the directory for debugging
        try:
            files_in_dir = os.listdir(UPLOAD_FOLDER)
            logger.info(f"Files in upload dir: {files_in_dir}")
        except Exception as e:
            logger.error(f"Could not list upload dir: {e}")
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
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
        
        logger.info(f"Serving with media type: {media_type}")
        
        return FileResponse(
            file_path,
            media_type=media_type,
            headers={"Cache-Control": "public, max-age=31536000"}  # 1 year cache
        )
        
    except Exception as e:
        logger.error(f"Error serving file {safe_filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")