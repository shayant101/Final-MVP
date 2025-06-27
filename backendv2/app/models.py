from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    restaurant = "restaurant"
    admin = "admin"

class CampaignType(str, Enum):
    ad = "ad"
    sms = "sms"

class CampaignStatus(str, Enum):
    active = "active"
    draft = "draft"
    completed = "completed"
    paused = "paused"

class ChecklistStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    not_applicable = "not_applicable"

class ChecklistType(str, Enum):
    foundational = "foundational"
    ongoing = "ongoing"

# Request Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    restaurantName: str = Field(..., min_length=1)
    address: Optional[str] = None
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response Models
class Restaurant(BaseModel):
    restaurant_id: str
    user_id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime

class User(BaseModel):
    user_id: str
    email: str
    role: UserRole
    created_at: datetime
    restaurant: Optional[Restaurant] = None
    impersonating_restaurant_id: Optional[str] = None

class AuthResponse(BaseModel):
    message: str
    token: str
    user: User

class UserResponse(BaseModel):
    user: User

class Campaign(BaseModel):
    campaign_id: str
    restaurant_id: str
    campaign_type: CampaignType
    status: CampaignStatus
    name: str
    details: Optional[str] = None
    budget: Optional[float] = None
    created_at: datetime
    updated_at: datetime

class ChecklistCategory(BaseModel):
    category_id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    type: ChecklistType
    order_in_list: int
    created_at: datetime

class ChecklistItem(BaseModel):
    item_id: str
    category_id: str
    parent_item_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    guidance_link: Optional[str] = None
    order_in_category: int
    is_critical: bool = False
    created_at: datetime

class RestaurantChecklistStatus(BaseModel):
    status_id: str
    restaurant_id: str
    item_id: str
    status: ChecklistStatus
    notes: Optional[str] = None
    last_updated_at: datetime

# Database Models (for internal use)
class UserInDB(BaseModel):
    user_id: str
    email: str
    password_hash: str
    role: UserRole
    created_at: datetime

class RestaurantInDB(BaseModel):
    restaurant_id: str
    user_id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    impersonating_restaurant_id: Optional[str] = None