import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import TokenData, UserRole
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        impersonating_restaurant_id: str = payload.get("impersonating_restaurant_id")
        
        if user_id is None or email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(
            user_id=user_id,
            email=email,
            role=role,
            impersonating_restaurant_id=impersonating_restaurant_id
        )
        return token_data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Get current user from JWT token"""
    token = credentials.credentials
    return verify_token(token)

async def require_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require admin role"""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_restaurant_id(current_user: TokenData = Depends(get_current_user)) -> str:
    """Get restaurant ID for current user (handles impersonation)"""
    from .database import users_collection
    from bson import ObjectId
    
    if current_user.impersonating_restaurant_id:
        return current_user.impersonating_restaurant_id
    
    if current_user.role == UserRole.restaurant:
        # For restaurant users, their user_id IS their restaurant_id in our MongoDB setup
        return current_user.user_id
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Restaurant access required"
    )

async def require_restaurant(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require restaurant role or admin impersonation"""
    if current_user.role != UserRole.restaurant and not current_user.impersonating_restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Restaurant access required"
        )
    return current_user

async def get_current_restaurant_user(current_user: TokenData = Depends(get_current_user)):
    """Get current restaurant user with full User object"""
    from .database import get_users_collection, get_restaurants_collection
    from .models import User, Restaurant
    from bson import ObjectId
    
    users_collection = get_users_collection()
    restaurants_collection = get_restaurants_collection()
    
    # Get user from database
    user_doc = await users_collection.find_one({"_id": ObjectId(current_user.user_id)})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user has restaurant access (either restaurant user or admin with impersonation)
    if current_user.role != UserRole.restaurant and not current_user.impersonating_restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Restaurant access required"
        )
    
    # Get restaurant info
    restaurant = None
    if current_user.role == UserRole.restaurant:
        # For restaurant users, get their restaurant
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
    elif current_user.impersonating_restaurant_id:
        # For admin users impersonating, get the impersonated restaurant
        restaurant_doc = await restaurants_collection.find_one({"_id": ObjectId(current_user.impersonating_restaurant_id)})
        if restaurant_doc:
            restaurant = Restaurant(
                restaurant_id=current_user.impersonating_restaurant_id,
                user_id=restaurant_doc["user_id"],
                name=restaurant_doc["name"],
                address=restaurant_doc.get("address"),
                phone=restaurant_doc.get("phone"),
                created_at=restaurant_doc["created_at"]
            )
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    user = User(
        user_id=current_user.user_id,
        email=user_doc["email"],
        role=user_doc["role"],
        created_at=user_doc["created_at"],
        restaurant=restaurant,
        impersonating_restaurant_id=current_user.impersonating_restaurant_id
    )
    
    return user