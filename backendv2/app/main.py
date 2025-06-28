from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .database import connect_to_mongo, close_mongo_connection, initialize_collections
from .routes.auth import router as auth_router
from .routes.dashboard import router as dashboard_router
from .routes.checklist import router as checklist_router

# Create FastAPI application instance
app = FastAPI(
    title="Restaurant Marketing Platform API v2",
    description="FastAPI backend for restaurant marketing platform",
    version="2.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database event handlers
@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    await connect_to_mongo()
    await initialize_collections()
    print("🚀 FastAPI Backend v2 started successfully!")
    print("🔐 Authentication endpoints available at /api/auth")
    print("📊 Dashboard endpoints available at /api/dashboard")
    print("✅ Checklist endpoints available at /api/checklist")

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_mongo_connection()

# Include routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(checklist_router)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return {
        "status": "healthy",
        "message": "FastAPI Backend v2 is running",
        "version": "2.0.0",
        "database": "MongoDB connected"
    }

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Welcome to Restaurant Marketing Platform API v2",
        "docs": "/docs",
        "health": "/api/health",
        "auth": "/api/auth",
        "dashboard": "/api/dashboard",
        "checklist": "/api/checklist"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )