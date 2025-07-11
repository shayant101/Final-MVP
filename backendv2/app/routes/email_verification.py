from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from ..models import (
    EmailVerificationRequest, 
    EmailVerificationResponse, 
    ResendVerificationRequest, 
    ResendVerificationResponse,
    User, 
    Restaurant, 
    UserRole
)
from ..database import get_users_collection, get_restaurants_collection
from ..auth import get_current_user, TokenData
from ..services.email_service import send_verification_email, send_welcome_email, send_admin_notification
from ..utils.email_utils import (
    create_verification_data, 
    verify_token_hash, 
    is_token_expired,
    format_registration_time
)
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["email-verification"])

@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(request: EmailVerificationRequest):
    """
    Verify user email with verification token
    """
    users_collection = get_users_collection()
    restaurants_collection = get_restaurants_collection()
    
    if not request.token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token is required"
        )
    
    # Find user with this verification token
    user_doc = await users_collection.find_one({
        "email_verification_token": {"$exists": True, "$ne": None}
    })
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Check if token matches
    stored_token_hash = user_doc.get("email_verification_token")
    if not stored_token_hash or not verify_token_hash(request.token, stored_token_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Check if token has expired
    expires_at = user_doc.get("email_verification_expires")
    if not expires_at or is_token_expired(expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )
    
    # Check if already verified
    if user_doc.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Update user as verified
    await users_collection.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                "email_verified": True,
                "last_login": datetime.utcnow()
            },
            "$unset": {
                "email_verification_token": "",
                "email_verification_expires": ""
            }
        }
    )
    
    user_id = str(user_doc["_id"])
    
    # Get restaurant info if user is restaurant owner
    restaurant = None
    if user_doc["role"] == UserRole.restaurant:
        restaurant_doc = await restaurants_collection.find_one({"user_id": user_id})
        if restaurant_doc:
            restaurant = Restaurant(
                restaurant_id=str(restaurant_doc["_id"]),
                user_id=user_id,
                name=restaurant_doc["name"],
                address=restaurant_doc.get("address"),
                phone=restaurant_doc.get("phone"),
                created_at=restaurant_doc["created_at"]
            )
    
    # Create user response
    user = User(
        user_id=user_id,
        email=user_doc["email"],
        role=user_doc["role"],
        created_at=user_doc["created_at"],
        restaurant=restaurant,
        email_verified=True,
        last_login=datetime.utcnow()
    )
    
    # Send welcome email (async, don't wait for result)
    if settings.ENABLE_WELCOME_EMAILS and restaurant:
        try:
            await send_welcome_email(
                to_email=user_doc["email"],
                user_name=user_doc["email"],
                restaurant_name=restaurant.name,
                dashboard_url=settings.dashboard_url
            )
            logger.info(f"Welcome email sent to {user_doc['email']}")
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user_doc['email']}: {str(e)}")
    
    logger.info(f"Email verified successfully for user {user_doc['email']}")
    
    return EmailVerificationResponse(
        success=True,
        message="Email verified successfully! Welcome to our platform.",
        user=user
    )

@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification_email(request: ResendVerificationRequest):
    """
    Resend verification email to user
    """
    users_collection = get_users_collection()
    restaurants_collection = get_restaurants_collection()
    
    # Find user by email
    user_doc = await users_collection.find_one({"email": request.email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already verified
    if user_doc.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Generate new verification token
    token, token_hash, expiry = create_verification_data()
    
    # Update user with new verification token
    await users_collection.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                "email_verification_token": token_hash,
                "email_verification_expires": expiry
            }
        }
    )
    
    # Get restaurant info for email
    restaurant_name = "Your Restaurant"
    if user_doc["role"] == UserRole.restaurant:
        restaurant_doc = await restaurants_collection.find_one({"user_id": str(user_doc["_id"])})
        if restaurant_doc:
            restaurant_name = restaurant_doc["name"]
    
    # Send verification email
    try:
        result = await send_verification_email(
            to_email=request.email,
            user_name=request.email,
            restaurant_name=restaurant_name,
            verification_token=token,
            base_url=settings.FRONTEND_URL
        )
        
        if result["success"]:
            logger.info(f"Verification email resent to {request.email}")
            return ResendVerificationResponse(
                success=True,
                message="Verification email sent successfully. Please check your inbox."
            )
        else:
            logger.error(f"Failed to resend verification email to {request.email}: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again later."
            )
    
    except Exception as e:
        logger.error(f"Error resending verification email to {request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again later."
        )

@router.get("/verification-status")
async def get_verification_status(current_user: TokenData = Depends(get_current_user)):
    """
    Get current user's email verification status
    """
    users_collection = get_users_collection()
    
    # Get user from database
    user_doc = await users_collection.find_one({"_id": ObjectId(current_user.user_id)})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    email_verified = user_doc.get("email_verified", False)
    has_pending_verification = bool(user_doc.get("email_verification_token"))
    
    verification_expires = None
    if has_pending_verification and user_doc.get("email_verification_expires"):
        verification_expires = user_doc["email_verification_expires"].isoformat()
    
    return {
        "email": user_doc["email"],
        "email_verified": email_verified,
        "has_pending_verification": has_pending_verification,
        "verification_expires": verification_expires,
        "verification_required": settings.ENABLE_EMAIL_VERIFICATION
    }

@router.post("/send-admin-notification")
async def send_admin_notification_endpoint(current_user: TokenData = Depends(get_current_user)):
    """
    Send admin notification for new user (for testing purposes)
    """
    if not settings.ENABLE_ADMIN_NOTIFICATIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin notifications are disabled"
        )
    
    users_collection = get_users_collection()
    restaurants_collection = get_restaurants_collection()
    
    # Get user info
    user_doc = await users_collection.find_one({"_id": ObjectId(current_user.user_id)})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get restaurant info
    restaurant_name = "Unknown Restaurant"
    phone = None
    address = None
    
    if user_doc["role"] == UserRole.restaurant:
        restaurant_doc = await restaurants_collection.find_one({"user_id": current_user.user_id})
        if restaurant_doc:
            restaurant_name = restaurant_doc["name"]
            phone = restaurant_doc.get("phone")
            address = restaurant_doc.get("address")
    
    # Send admin notification
    try:
        result = await send_admin_notification(
            user_email=user_doc["email"],
            restaurant_name=restaurant_name,
            phone=phone,
            address=address,
            registration_time=user_doc["created_at"]
        )
        
        if result["success"]:
            return {"success": True, "message": "Admin notification sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send admin notification: {result['message']}"
            )
    
    except Exception as e:
        logger.error(f"Error sending admin notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send admin notification"
        )