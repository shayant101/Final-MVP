"""
Website Builder Data Models
Models for AI-powered restaurant website generation and management
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums for Website Builder
class WebsiteStatus(str, Enum):
    draft = "draft"
    generating = "generating"
    ready = "ready"
    published = "published"
    archived = "archived"

class DesignCategory(str, Enum):
    fine_dining = "fine_dining"
    casual_dining = "casual_dining"
    fast_casual = "fast_casual"
    cafe_bakery = "cafe_bakery"
    ethnic_cuisine = "ethnic_cuisine"

class ComponentType(str, Enum):
    hero_section = "hero_section"
    about_section = "about_section"
    menu_showcase = "menu_showcase"
    location_contact = "location_contact"
    reservation_system = "reservation_system"
    gallery = "gallery"
    testimonials = "testimonials"
    footer = "footer"

class PublishingPlatform(str, Enum):
    momentum_hosting = "momentum_hosting"
    custom_domain = "custom_domain"
    export_html = "export_html"

# Core Website Models
class ColorPalette(BaseModel):
    primary: str = Field(..., description="Primary brand color (hex)")
    secondary: str = Field(..., description="Secondary brand color (hex)")
    accent: str = Field(..., description="Accent color for highlights (hex)")
    neutral: str = Field(..., description="Neutral color for backgrounds (hex)")
    text_primary: str = Field(default="#333333", description="Primary text color")
    text_secondary: str = Field(default="#666666", description="Secondary text color")

class TypographySystem(BaseModel):
    headings_font: str = Field(..., description="Font family for headings")
    body_font: str = Field(..., description="Font family for body text")
    accent_font: Optional[str] = Field(None, description="Font family for accents")
    font_sizes: Dict[str, str] = Field(default_factory=dict, description="Font size scale")
    line_heights: Dict[str, str] = Field(default_factory=dict, description="Line height scale")

class DesignSystem(BaseModel):
    color_palette: ColorPalette
    typography: TypographySystem
    border_radius: str = Field(default="8px", description="Default border radius")
    spacing_scale: Dict[str, str] = Field(default_factory=dict, description="Spacing scale")
    shadow_styles: Dict[str, str] = Field(default_factory=dict, description="Box shadow styles")
    animation_settings: Dict[str, Any] = Field(default_factory=dict, description="Animation preferences")

class WebsiteComponent(BaseModel):
    component_id: str
    component_type: ComponentType
    title: str
    content: Dict[str, Any] = Field(default_factory=dict, description="Component content and settings")
    styling: Dict[str, Any] = Field(default_factory=dict, description="Component-specific styling")
    order: int = Field(default=0, description="Display order on page")
    visible: bool = Field(default=True, description="Component visibility")
    responsive_settings: Dict[str, Any] = Field(default_factory=dict, description="Mobile/tablet settings")

class WebsitePage(BaseModel):
    page_id: str
    page_name: str
    page_slug: str = Field(..., description="URL slug for the page")
    page_title: str = Field(..., description="SEO page title")
    meta_description: str = Field(..., description="SEO meta description")
    components: List[WebsiteComponent] = Field(default_factory=list)
    custom_css: Optional[str] = Field(None, description="Custom CSS for this page")
    is_homepage: bool = Field(default=False)
    published: bool = Field(default=False)

class SEOSettings(BaseModel):
    site_title: str
    site_description: str
    keywords: List[str] = Field(default_factory=list)
    og_image: Optional[str] = Field(None, description="Open Graph image URL")
    twitter_card: str = Field(default="summary_large_image")
    canonical_url: Optional[str] = Field(None)
    robots_txt: str = Field(default="User-agent: *\nAllow: /")
    sitemap_enabled: bool = Field(default=True)
    analytics_code: Optional[str] = Field(None, description="Google Analytics tracking code")

class PerformanceSettings(BaseModel):
    image_optimization: bool = Field(default=True)
    lazy_loading: bool = Field(default=True)
    minify_css: bool = Field(default=True)
    minify_js: bool = Field(default=True)
    enable_caching: bool = Field(default=True)
    cdn_enabled: bool = Field(default=False)
    compression_enabled: bool = Field(default=True)

class IntegrationSettings(BaseModel):
    google_analytics: Optional[str] = Field(None)
    facebook_pixel: Optional[str] = Field(None)
    google_maps_api_key: Optional[str] = Field(None)
    reservation_system: Optional[str] = Field(None, description="OpenTable, Resy, etc.")
    online_ordering: Optional[str] = Field(None, description="DoorDash, Uber Eats, etc.")
    social_media_links: Dict[str, str] = Field(default_factory=dict)
    email_marketing: Optional[str] = Field(None, description="Mailchimp, Constant Contact, etc.")

# Main Website Model
class RestaurantWebsite(BaseModel):
    website_id: str
    restaurant_id: str
    website_name: str
    domain_name: Optional[str] = Field(None, description="Custom domain if configured")
    status: WebsiteStatus = Field(default=WebsiteStatus.draft)
    design_category: DesignCategory
    design_system: DesignSystem
    pages: List[WebsitePage] = Field(default_factory=list)
    seo_settings: SEOSettings
    performance_settings: PerformanceSettings = Field(default_factory=PerformanceSettings)
    integration_settings: IntegrationSettings = Field(default_factory=IntegrationSettings)
    ai_generation_metadata: Dict[str, Any] = Field(default_factory=dict, description="AI generation details")
    custom_code: Optional[str] = Field(None, description="Custom HTML/CSS/JS")
    backup_versions: List[str] = Field(default_factory=list, description="Backup version IDs")
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = Field(None)
    last_backup_at: Optional[datetime] = Field(None)

# Website Generation Request Models
class WebsiteGenerationRequest(BaseModel):
    restaurant_id: str
    website_name: str
    design_preferences: Optional[Dict[str, Any]] = Field(None, description="User design preferences")
    content_preferences: Optional[Dict[str, Any]] = Field(None, description="Content generation preferences")
    include_sections: List[ComponentType] = Field(default_factory=list, description="Specific sections to include")
    custom_requirements: Optional[str] = Field(None, description="Special requirements or requests")

class WebsiteGenerationResponse(BaseModel):
    success: bool
    website_id: Optional[str] = None
    generation_status: str
    estimated_completion_time: Optional[int] = Field(None, description="Estimated completion in seconds")
    preview_url: Optional[str] = None
    error_message: Optional[str] = None

# Website Template Models
class WebsiteTemplate(BaseModel):
    template_id: str
    template_name: str
    design_category: DesignCategory
    description: str
    preview_image: str
    design_system: DesignSystem
    default_pages: List[Dict[str, Any]] = Field(default_factory=list)
    default_components: List[Dict[str, Any]] = Field(default_factory=list)
    customization_options: Dict[str, Any] = Field(default_factory=dict)
    popularity_score: float = Field(default=0.0, description="Template usage popularity")
    created_at: datetime
    updated_at: datetime
    active: bool = Field(default=True)

# Website Analytics Models
class WebsiteAnalytics(BaseModel):
    analytics_id: str
    website_id: str
    date: datetime
    page_views: int = Field(default=0)
    unique_visitors: int = Field(default=0)
    bounce_rate: float = Field(default=0.0)
    average_session_duration: float = Field(default=0.0)
    conversion_rate: float = Field(default=0.0)
    mobile_traffic_percentage: float = Field(default=0.0)
    top_pages: List[Dict[str, Any]] = Field(default_factory=list)
    traffic_sources: Dict[str, int] = Field(default_factory=dict)
    user_interactions: Dict[str, int] = Field(default_factory=dict)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)

# Website Backup and Version Control
class WebsiteBackup(BaseModel):
    backup_id: str
    website_id: str
    backup_name: str
    backup_type: str = Field(default="manual", description="manual, auto, or pre-publish")
    website_data: Dict[str, Any] = Field(..., description="Complete website data snapshot")
    file_size: int = Field(default=0, description="Backup size in bytes")
    created_at: datetime
    created_by: Optional[str] = Field(None, description="User who created the backup")
    notes: Optional[str] = Field(None, description="Backup notes or description")

# Publishing and Deployment Models
class WebsiteDeployment(BaseModel):
    deployment_id: str
    website_id: str
    platform: PublishingPlatform
    deployment_url: str
    deployment_status: str = Field(default="pending", description="pending, deploying, success, failed")
    deployment_config: Dict[str, Any] = Field(default_factory=dict)
    build_logs: List[str] = Field(default_factory=list)
    deployed_at: Optional[datetime] = None
    deployment_time: Optional[int] = Field(None, description="Deployment time in seconds")
    error_details: Optional[str] = None

# API Request/Response Models
class WebsiteListResponse(BaseModel):
    websites: List[RestaurantWebsite]
    total_count: int
    page: int = Field(default=1)
    per_page: int = Field(default=10)

class WebsiteUpdateRequest(BaseModel):
    website_name: Optional[str] = None
    design_system: Optional[DesignSystem] = None
    seo_settings: Optional[SEOSettings] = None
    integration_settings: Optional[IntegrationSettings] = None
    custom_code: Optional[str] = None

class ComponentUpdateRequest(BaseModel):
    component_id: str
    content: Optional[Dict[str, Any]] = None
    styling: Optional[Dict[str, Any]] = None
    order: Optional[int] = None
    visible: Optional[bool] = None

class PageUpdateRequest(BaseModel):
    page_id: str
    page_name: Optional[str] = None
    page_title: Optional[str] = None
    meta_description: Optional[str] = None
    components: Optional[List[WebsiteComponent]] = None
    custom_css: Optional[str] = None

class WebsitePreviewRequest(BaseModel):
    website_id: str
    device_type: str = Field(default="desktop", description="desktop, tablet, mobile")
    page_slug: str = Field(default="/", description="Page to preview")

class WebsitePreviewResponse(BaseModel):
    success: bool
    preview_url: str
    preview_expires_at: datetime
    device_type: str
    page_slug: str

# AI Generation Specific Models
class AIGenerationProgress(BaseModel):
    generation_id: str
    website_id: str
    current_step: str
    total_steps: int
    completed_steps: int
    progress_percentage: float
    estimated_time_remaining: Optional[int] = None
    current_operation: str
    status: str = Field(default="in_progress", description="in_progress, completed, failed")
    error_details: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

class AIGenerationSettings(BaseModel):
    creativity_level: float = Field(default=0.7, ge=0.0, le=1.0, description="AI creativity level")
    content_tone: str = Field(default="professional", description="professional, casual, friendly, elegant")
    include_ai_images: bool = Field(default=True, description="Generate AI images for content")
    seo_optimization_level: str = Field(default="standard", description="basic, standard, advanced")
    mobile_priority: bool = Field(default=True, description="Prioritize mobile-first design")
    accessibility_compliance: str = Field(default="wcag_aa", description="wcag_a, wcag_aa, wcag_aaa")

# Website Performance Models
class WebsitePerformanceMetrics(BaseModel):
    metrics_id: str
    website_id: str
    measured_at: datetime
    page_load_time: float = Field(default=0.0, description="Page load time in seconds")
    first_contentful_paint: float = Field(default=0.0, description="FCP in seconds")
    largest_contentful_paint: float = Field(default=0.0, description="LCP in seconds")
    cumulative_layout_shift: float = Field(default=0.0, description="CLS score")
    first_input_delay: float = Field(default=0.0, description="FID in milliseconds")
    lighthouse_score: int = Field(default=0, description="Overall Lighthouse score")
    mobile_score: int = Field(default=0, description="Mobile Lighthouse score")
    desktop_score: int = Field(default=0, description="Desktop Lighthouse score")
    seo_score: int = Field(default=0, description="SEO score")
    accessibility_score: int = Field(default=0, description="Accessibility score")
    best_practices_score: int = Field(default=0, description="Best practices score")

# Website Builder Dashboard Models
class WebsiteBuilderDashboard(BaseModel):
    total_websites: int = Field(default=0)
    published_websites: int = Field(default=0)
    draft_websites: int = Field(default=0)
    total_page_views: int = Field(default=0)
    average_performance_score: float = Field(default=0.0)
    recent_websites: List[RestaurantWebsite] = Field(default_factory=list)
    performance_summary: Dict[str, float] = Field(default_factory=dict)
    popular_templates: List[WebsiteTemplate] = Field(default_factory=list)
    ai_generation_stats: Dict[str, int] = Field(default_factory=dict)

# Error and Validation Models
class WebsiteBuilderError(BaseModel):
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    website_id: Optional[str] = None
    user_id: Optional[str] = None

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)