"""
Simple Image Upload Test - Bypass authentication for debugging
"""
import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-image")
async def simple_upload_image(
    file: UploadFile = File(...),
    image_type: str = Form("hero")
):
    """Simple image upload without authentication"""
    try:
        print(f"🔍 SIMPLE UPLOAD: Received file: {file.filename}")
        print(f"🔍 SIMPLE UPLOAD: Upload directory: {UPLOAD_DIR}")
        
        # Generate filename
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{file_id}_{image_type}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        print(f"🔍 SIMPLE UPLOAD: Saving to: {file_path}")
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        print(f"🔍 SIMPLE UPLOAD: File saved successfully!")
        print(f"🔍 SIMPLE UPLOAD: File exists: {os.path.exists(file_path)}")
        
        return {
            "success": True,
            "filename": filename,
            "url": f"/images/{filename}",
            "message": "Upload successful"
        }
        
    except Exception as e:
        print(f"🔍 SIMPLE UPLOAD: Error: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/images/{filename}")
async def serve_image(filename: str):
    """Serve uploaded images"""
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        print(f"🔍 SIMPLE SERVE: Looking for: {file_path}")
        print(f"🔍 SIMPLE SERVE: File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            return {"error": "Image not found"}
        
        return FileResponse(file_path)
        
    except Exception as e:
        print(f"🔍 SIMPLE SERVE: Error: {str(e)}")
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"message": "Simple Image Upload Server", "upload": "/upload-image"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)