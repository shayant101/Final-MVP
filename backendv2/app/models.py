from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    restaurant = "restaurant"
    admin = "admin"

class CampaignType(str, Enum):
    facebook_ad = "facebook_ad"
    sms = "sms"

class CampaignStatus(str, Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"
    pending_review = "pending_review"

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

# Campaign Request Models
class FacebookAdCampaignCreate(BaseModel):
    restaurantName: str = Field(..., min_length=1)
    itemToPromote: str = Field(..., min_length=1)
    offer: str = Field(..., min_length=1)
    budget: float = Field(..., gt=0)

class SMSCampaignCreate(BaseModel):
    restaurantName: str = Field(..., min_length=1)
    offer: str = Field(..., min_length=1)
    offerCode: str = Field(..., min_length=1)

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[CampaignStatus] = None
    budget: Optional[float] = None
    details: Optional[dict] = None

# Campaign Response Models
class FacebookAdDetails(BaseModel):
    restaurant_name: str
    item_to_promote: str
    offer: str
    budget: float
    ad_copy: Optional[str] = None
    promo_code: Optional[str] = None
    dish_photo: Optional[str] = None
    campaign_id: Optional[str] = None
    ad_set_id: Optional[str] = None
    ad_id: Optional[str] = None
    expected_reach: Optional[int] = None
    estimated_impressions: Optional[int] = None
    campaign_url: Optional[str] = None

class SMSCampaignDetails(BaseModel):
    restaurant_name: str
    offer: str
    offer_code: str
    total_customers_uploaded: Optional[int] = None
    lapsed_customers_found: Optional[int] = None
    messages_sent: Optional[int] = None
    messages_failed: Optional[int] = None
    messages_pending: Optional[int] = None
    total_cost: Optional[float] = None
    sample_message: Optional[str] = None
    delivery_rate: Optional[str] = None
    csv_errors: Optional[List[dict]] = None

class CampaignMetrics(BaseModel):
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    reach: Optional[int] = None
    spend: Optional[float] = None
    total_sent: Optional[int] = None
    delivered: Optional[int] = None
    failed: Optional[int] = None
    delivery_rate: Optional[str] = None
    total_cost: Optional[float] = None

class Campaign(BaseModel):
    campaign_id: str
    restaurant_id: str
    campaign_type: CampaignType
    status: CampaignStatus
    name: str
    details: Optional[dict] = None
    budget: Optional[float] = None
    metrics: Optional[CampaignMetrics] = None
    created_at: datetime
    updated_at: datetime
    launched_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None

class CampaignResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class CampaignListResponse(BaseModel):
    success: bool
    campaigns: List[Campaign]
    total: int

# Customer Models for SMS Campaigns
class Customer(BaseModel):
    customer_name: str
    phone_number: str
    last_order_date: str
    email: Optional[str] = None
    notes: Optional[str] = None

class CSVParseResult(BaseModel):
    success: bool
    customers: List[Customer]
    errors: List[dict]
    total_rows: int
    valid_rows: int
    error_rows: int

class SMSPreviewRequest(BaseModel):
    restaurantName: str
    offer: str
    offerCode: str

class FacebookAdPreviewRequest(BaseModel):
    restaurantName: str
    itemToPromote: str
    offer: str

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