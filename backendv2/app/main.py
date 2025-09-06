from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .database import connect_to_mongo, close_mongo_connection, initialize_collections
from .routes.auth import router as auth_router
from .routes.email_verification import router as email_verification_router
from .routes.dashboard import router as dashboard_router
from .routes.checklist import router as checklist_router
from .routes.campaigns import router as campaigns_router
from .routes.content_generation import router as content_router
from .routes.ai_features import router as ai_router
from .routes.admin import router as admin_router
from .routes.website_builder import router as website_builder_router
from .routes.website_publishing import router as website_publishing_router
from .routes.media_upload import router as media_router
from .routes.media_upload_v2 import router as media_router_v2
from .routes.phase3_routes import get_phase3_routers
from .core.config import settings, validate_environment

# Create FastAPI application instance
app = FastAPI(
    title="Restaurant Marketing Platform API v2",
    description="FastAPI backend for restaurant marketing platform",
    version="2.0.0"
)

# Configure CORS middleware - Allow all origins for full accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Database event handlers
@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    # Validate environment configuration
    env_errors = validate_environment()
    if env_errors:
        print("⚠️  Environment Configuration Warnings:")
        for error in env_errors:
            print(f"   - {error}")
        print()
    
    await connect_to_mongo()
    await initialize_collections()
    print("🚀 FastAPI Backend v2 started successfully!")
    print("🔐 Authentication endpoints available at /api/auth")
    print("📧 Email verification endpoints available at /api/auth")
    print("� Dashboard endpoints available at /api/dashboard")
    print("✅ Checklist endpoints available at /api/checklist")
    print("📢 Campaign endpoints available at /api/campaigns")
    print("🤖 Content generation endpoints available at /api/content")
    print("🧠 AI Features endpoints available at /api/ai")
    print("👑 Admin endpoints available at /api/admin")
    print("🌐 Website Builder endpoints available at /api/website-builder")
    print("🚀 Website Publishing endpoints available at /api/website-builder")
    print("� Media Upload endpoints available at /api/website-builder/upload-image")
    print("📈 Phase 3 Business Intelligence endpoints available:")
    print("   📊 Billing & Subscriptions at /api/billing")
    print("   📈 Revenue Analytics at /api/revenue")
    print("   🤖 AI Assistant at /api/ai-assistant")
    print("   🧠 Business Intelligence at /api/business-intelligence")
    
    # Email service status
    if settings.email_enabled:
        print("📧 Email service: ✅ Configured")
        if settings.ENABLE_EMAIL_VERIFICATION:
            print("   - Email verification: ✅ Enabled")
        if settings.ENABLE_ADMIN_NOTIFICATIONS:
            print("   - Admin notifications: ✅ Enabled")
        if settings.ENABLE_WELCOME_EMAILS:
            print("   - Welcome emails: ✅ Enabled")
    else:
        print("📧 Email service: ⚠️  Not configured (RESEND_API_KEY missing)")

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_mongo_connection()

# Include routers
app.include_router(auth_router)
app.include_router(email_verification_router)
app.include_router(dashboard_router)
app.include_router(checklist_router)
app.include_router(campaigns_router)
app.include_router(content_router)
app.include_router(ai_router)
app.include_router(admin_router)
app.include_router(website_builder_router)
app.include_router(website_publishing_router)
app.include_router(media_router)
app.include_router(media_router_v2)

# Include Phase 3 routers
phase3_routers = get_phase3_routers()
for router in phase3_routers:
    app.include_router(router)

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
        "checklist": "/api/checklist",
        "campaigns": "/api/campaigns",
        "content": "/api/content",
        "ai_features": "/api/ai",
        "admin": "/api/admin",
        "website_builder": "/api/website-builder",
        "phase3_billing": "/api/billing",
        "phase3_revenue": "/api/revenue",
        "phase3_ai_assistant": "/api/ai-assistant",
        "phase3_business_intelligence": "/api/business-intelligence"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )