from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
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
    email_verified: bool = False
    last_login: Optional[datetime] = None

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
    email_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_expires: Optional[datetime] = None
    last_login: Optional[datetime] = None

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

# Image Enhancement Models
class ImageEnhancementOptions(BaseModel):
    brightness: Optional[float] = Field(default=1.1, ge=0.5, le=2.0)
    contrast: Optional[float] = Field(default=1.2, ge=0.5, le=2.0)
    saturation: Optional[float] = Field(default=1.15, ge=0.5, le=2.0)
    sharpness: Optional[float] = Field(default=1.1, ge=0.5, le=2.0)
    food_styling_optimization: Optional[bool] = Field(default=True)

class ImageUploadRequest(BaseModel):
    filename: str = Field(..., min_length=1)
    enhancement_options: Optional[ImageEnhancementOptions] = None

class ImageAnalysis(BaseModel):
    food_identification: Dict[str, Any]
    visual_quality: Dict[str, Any]
    marketing_potential: Dict[str, Any]
    suggested_improvements: List[str]
    color_palette: List[str]
    dominant_colors: List[str]
    image_dimensions: str
    analysis_timestamp: str

class EnhancedImage(BaseModel):
    image_id: str
    restaurant_id: str
    original_filename: str
    file_size: int
    enhanced_file_size: int
    enhancement_options: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    created_at: str
    status: str

class ImageContentGenerationRequest(BaseModel):
    image_id: str
    content_types: Optional[List[str]] = Field(default=['social_media_caption', 'menu_description', 'promotional_content'])

class GeneratedImageContent(BaseModel):
    image_id: str
    generated_content: Dict[str, Any]
    content_types: List[str]
    generation_timestamp: str
    image_analysis_used: Dict[str, Any]

class ImageListResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]

class ImageEnhancementResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_type: Optional[str] = None

# Analytics Models for Enhanced Admin Dashboard
class AIUsageAnalytics(BaseModel):
    analytics_id: str
    restaurant_id: str
    feature_type: str  # image_enhancement, content_generation, marketing_assistant
    operation_type: str  # specific operation like enhance_image, generate_content
    timestamp: datetime
    processing_time_ms: int
    tokens_used: Optional[int] = 0
    estimated_cost: Optional[float] = 0.0
    status: str  # success, error, timeout
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class AIContentModeration(BaseModel):
    moderation_id: str
    restaurant_id: str
    content_type: str  # social_media_caption, menu_description, etc.
    content_id: Optional[str] = None
    status: str  # approved, flagged, pending_review
    content_data: Dict[str, Any]
    flags: Optional[List[str]] = []
    reviewed_by: Optional[str] = None
    flagged_at: datetime
    reviewed_at: Optional[datetime] = None

class AIPerformanceMetrics(BaseModel):
    metric_id: str
    feature_type: str
    metric_date: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_processing_time: float
    total_cost: float
    hourly_breakdown: Dict[str, Dict[str, Any]]
    created_at: datetime

class AIFeatureToggles(BaseModel):
    toggle_id: str
    restaurant_id: str
    feature_name: str  # image_enhancement, content_generation, etc.
    enabled: bool
    rate_limits: Optional[Dict[str, int]] = None
    updated_at: datetime
    updated_by: str

# Admin Analytics Request/Response Models
class AnalyticsDateRange(BaseModel):
    start_date: datetime
    end_date: datetime
    feature_type: Optional[str] = None

class RealTimeMetrics(BaseModel):
    today_requests: int
    success_rate: float
    avg_response_time: int
    daily_cost: float
    active_requests: int
    last_updated: str

class UsageAnalyticsResponse(BaseModel):
    usage_over_time: List[Dict[str, Any]]
    feature_breakdown: List[Dict[str, Any]]
    error_analysis: List[Dict[str, Any]]
    date_range: Dict[str, str]

class ContentModerationRequest(BaseModel):
    content_ids: List[str]
    action: str  # approve, flag, reject
    reason: Optional[str] = None

class FeatureToggleRequest(BaseModel):
    restaurant_id: str
    feature_name: str
    enabled: bool
    rate_limits: Optional[Dict[str, int]] = None

# Email Verification Models
class EmailVerificationRequest(BaseModel):
    token: str

class EmailVerificationResponse(BaseModel):
    success: bool
    message: str
    user: Optional[User] = None

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ResendVerificationResponse(BaseModel):
    success: bool
    message: str