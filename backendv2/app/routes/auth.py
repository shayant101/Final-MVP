from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from ..models import UserRegister, UserLogin, AuthResponse, UserResponse, User, Restaurant, UserRole
from ..database import get_users_collection, get_restaurants_collection
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user, require_admin, TokenData
from ..services.email_service import send_verification_email, send_admin_notification
from ..utils.email_utils import create_verification_data, format_registration_time
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserRegister):
    """Register a new restaurant user"""
    users_collection = get_users_collection()
    restaurants_collection = get_restaurants_collection()
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists with this email"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Generate email verification data if email verification is enabled
    verification_token = None
    verification_token_hash = None
    verification_expires = None
    
    if settings.ENABLE_EMAIL_VERIFICATION:
        verification_token, verification_token_hash, verification_expires = create_verification_data()
    
    # Create user document
    user_doc = {
        "email": user_data.email,
        "password_hash": hashed_password,
        "role": UserRole.restaurant,
        "created_at": datetime.utcnow(),
        "email_verified": not settings.ENABLE_EMAIL_VERIFICATION,  # Auto-verify if verification disabled
        "email_verification_token": verification_token_hash,
        "email_verification_expires": verification_expires,
        "last_login": None
    }
    
    # Insert user
    user_result = await users_collection.insert_one(user_doc)
    user_id = str(user_result.inserted_id)
    
    # Create restaurant document
    restaurant_doc = {
        "user_id": user_id,
        "name": user_data.restaurantName,
        "address": user_data.address or "",
        "phone": user_data.phone or "",
        "created_at": datetime.utcnow()
    }
    
    # Insert restaurant
    restaurant_result = await restaurants_collection.insert_one(restaurant_doc)
    restaurant_id = str(restaurant_result.inserted_id)
    
    # Create default checklist items (simplified for now)
    # TODO: Implement checklist creation in a separate function
    
    # Create JWT token
    token_data = {
        "user_id": user_id,
        "email": user_data.email,
        "role": UserRole.restaurant
    }
    access_token = create_access_token(data=token_data)
    
    # Prepare response
    restaurant = Restaurant(
        restaurant_id=restaurant_id,
        user_id=user_id,
        name=user_data.restaurantName,
        address=user_data.address,
        phone=user_data.phone,
        created_at=restaurant_doc["created_at"]
    )
    
    user = User(
        user_id=user_id,
        email=user_data.email,
        role=UserRole.restaurant,
        created_at=user_doc["created_at"],
        restaurant=restaurant,
        email_verified=user_doc["email_verified"],
        last_login=user_doc["last_login"]
    )
    
    # Send verification email if email verification is enabled
    email_sent = False
    if settings.ENABLE_EMAIL_VERIFICATION and verification_token:
        try:
            result = await send_verification_email(
                to_email=user_data.email,
                user_name=user_data.email,
                restaurant_name=user_data.restaurantName,
                verification_token=verification_token,
                base_url=settings.FRONTEND_URL
            )
            email_sent = result["success"]
            if email_sent:
                logger.info(f"Verification email sent to {user_data.email}")
            else:
                logger.error(f"Failed to send verification email to {user_data.email}: {result['message']}")
        except Exception as e:
            logger.error(f"Error sending verification email to {user_data.email}: {str(e)}")
    
    # Send admin notification if enabled
    if settings.ENABLE_ADMIN_NOTIFICATIONS:
        try:
            await send_admin_notification(
                user_email=user_data.email,
                restaurant_name=user_data.restaurantName,
                phone=user_data.phone,
                address=user_data.address,
                registration_time=user_doc["created_at"]
            )
            logger.info(f"Admin notification sent for new registration: {user_data.restaurantName}")
        except Exception as e:
            logger.error(f"Failed to send admin notification for {user_data.restaurantName}: {str(e)}")
    
    # Prepare response message
    if settings.ENABLE_EMAIL_VERIFICATION:
        if email_sent:
            message = "User and restaurant created successfully. Please check your email to verify your account."
        else:
            message = "User and restaurant created successfully. Verification email could not be sent - please request a new one."
    else:
        message = "User and restaurant created successfully"
    
    return AuthResponse(
        message=message,
        token=access_token,
        user=user
    )

@router.post("/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin):
    """Login user"""
    users_collection = get_users_collection()
    restaurants_collection = get_restaurants_collection()
    
    # Find user
    user_doc = await users_collection.find_one({"email": login_data.email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(login_data.password, user_doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user_id = str(user_doc["_id"])
    
    # Update last login time
    await users_collection.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create JWT token
    token_data = {
        "user_id": user_id,
        "email": user_doc["email"],
        "role": user_doc["role"]
    }
    access_token = create_access_token(data=token_data)
    
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
    
    user = User(
        user_id=user_id,
        email=user_doc["email"],
        role=user_doc["role"],
        created_at=user_doc["created_at"],
        restaurant=restaurant,
        email_verified=user_doc.get("email_verified", False),
        last_login=datetime.utcnow()
    )
    
    return AuthResponse(
        message="Login successful",
        token=access_token,
        user=user
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information"""
    users_collection = get_users_collection()
    restaurants_collection = get_restaurants_collection()
    
    # Get user from database
    user_doc = await users_collection.find_one({"_id": ObjectId(current_user.user_id)})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get restaurant info if user is restaurant owner
    restaurant = None
    if user_doc["role"] == UserRole.restaurant:
        restaurant_doc = await restaurants_collection.find_one({"user_id": current_user.user_id})
        if restaurant_doc:
            restaurant = Restaurant(
                restaurant_id=str(restaurant_doc["_id"]),
                user_id=current_user.user_id,
                name=restaurant_doc["name"],
                address=restaurant_doc.get("address"),
                phone=restaurant_doc.get("phone"),
                created_at=restaurant_doc["created_at"]
            )
    
    user = User(
        user_id=current_user.user_id,
        email=user_doc["email"],
        role=user_doc["role"],
        created_at=user_doc["created_at"],
        restaurant=restaurant,
        impersonating_restaurant_id=current_user.impersonating_restaurant_id,
        email_verified=user_doc.get("email_verified", False),
        last_login=user_doc.get("last_login")
    )
    
    return UserResponse(user=user)

@router.post("/impersonate/{restaurant_id}", response_model=AuthResponse)
async def impersonate_restaurant(
    restaurant_id: str,
    current_user: TokenData = Depends(require_admin)
):
    """Admin impersonation of restaurant"""
    restaurants_collection = get_restaurants_collection()
    
    # Verify restaurant exists
    try:
        restaurant_doc = await restaurants_collection.find_one({"_id": ObjectId(restaurant_id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid restaurant ID"
        )
    
    if not restaurant_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    # Create new token with impersonation
    token_data = {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role,
        "impersonating_restaurant_id": restaurant_id
    }
    access_token = create_access_token(data=token_data)
    
    restaurant = Restaurant(
        restaurant_id=restaurant_id,
        user_id=restaurant_doc["user_id"],
        name=restaurant_doc["name"],
        address=restaurant_doc.get("address"),
        phone=restaurant_doc.get("phone"),
        created_at=restaurant_doc["created_at"]
    )
    
    # Get admin user info
    users_collection = get_users_collection()
    user_doc = await users_collection.find_one({"_id": ObjectId(current_user.user_id)})
    
    user = User(
        user_id=current_user.user_id,
        email=current_user.email,
        role=current_user.role,
        created_at=user_doc["created_at"],
        impersonating_restaurant_id=restaurant_id
    )
    
    return AuthResponse(
        message="Impersonation started",
        token=access_token,
        user=user
    )

@router.post("/end-impersonation", response_model=AuthResponse)
async def end_impersonation(current_user: TokenData = Depends(require_admin)):
    """End admin impersonation"""
    users_collection = get_users_collection()
    
    # Create new token without impersonation
    token_data = {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role
    }
    access_token = create_access_token(data=token_data)
    
    # Get admin user info
    user_doc = await users_collection.find_one({"_id": ObjectId(current_user.user_id)})
    
    user = User(
        user_id=current_user.user_id,
        email=current_user.email,
        role=current_user.role,
        created_at=user_doc["created_at"]
    )
    
    return AuthResponse(
        message="Impersonation ended",
        token=access_token,
        user=user
    )