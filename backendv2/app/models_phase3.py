"""
Phase 3 Business Intelligence & Monetization Models
Enhanced data models for billing, subscriptions, revenue analytics, and AI insights
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums for Phase 3
class SubscriptionStatus(str, Enum):
    active = "active"
    canceled = "canceled"
    past_due = "past_due"
    trialing = "trialing"
    incomplete = "incomplete"
    incomplete_expired = "incomplete_expired"

class PlanTier(str, Enum):
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"

class CreditType(str, Enum):
    facebook_ads = "facebook_ads"
    sms_campaigns = "sms_campaigns"
    content_generation = "content_generation"
    image_enhancement = "image_enhancement"

class InvoiceStatus(str, Enum):
    paid = "paid"
    pending = "pending"
    failed = "failed"
    draft = "draft"
    void = "void"

class InsightType(str, Enum):
    performance = "performance"
    recommendation = "recommendation"
    prediction = "prediction"
    alert = "alert"

# Subscription Plan Models
class SubscriptionPlanFeatures(BaseModel):
    ai_requests_per_month: int
    campaign_credits: int
    advanced_analytics: bool
    priority_support: bool
    custom_integrations: bool
    white_label: bool = False
    dedicated_support: bool = False

class SubscriptionPlan(BaseModel):
    plan_id: str
    name: str
    tier: PlanTier
    price_monthly: float
    price_yearly: float
    features: SubscriptionPlanFeatures
    stripe_price_id_monthly: Optional[str] = None
    stripe_price_id_yearly: Optional[str] = None
    active: bool = True
    created_at: datetime
    updated_at: datetime

class SubscriptionPlanCreate(BaseModel):
    name: str
    tier: PlanTier
    price_monthly: float = Field(..., gt=0)
    price_yearly: float = Field(..., gt=0)
    features: SubscriptionPlanFeatures

# Subscription Models
class UsageTracking(BaseModel):
    ai_requests_used: int = 0
    campaign_credits_used: int = 0
    last_reset_date: datetime
    overage_charges: float = 0.0

class RestaurantSubscription(BaseModel):
    subscription_id: str
    restaurant_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    trial_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    canceled_at: Optional[datetime] = None
    usage_tracking: UsageTracking
    created_at: datetime
    updated_at: datetime

class SubscriptionCreate(BaseModel):
    restaurant_id: str
    plan_id: str
    payment_method_id: Optional[str] = None
    trial_days: int = 14

class SubscriptionUpdate(BaseModel):
    plan_id: Optional[str] = None
    cancel_at_period_end: Optional[bool] = None
    payment_method_id: Optional[str] = None

# Billing Models
class InvoiceLineItem(BaseModel):
    description: str
    amount: float
    quantity: int = 1
    unit_price: float

class BillingInvoice(BaseModel):
    invoice_id: str
    restaurant_id: str
    subscription_id: Optional[str] = None
    stripe_invoice_id: Optional[str] = None
    amount: float
    currency: str = "usd"
    status: InvoiceStatus
    invoice_date: datetime
    due_date: datetime
    paid_date: Optional[datetime] = None
    line_items: List[InvoiceLineItem]
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    created_at: datetime
    updated_at: datetime

# Campaign Credits Models
class CampaignCredits(BaseModel):
    credit_id: str
    restaurant_id: str
    credit_type: CreditType
    credits_purchased: int
    credits_used: int = 0
    credits_remaining: int
    purchase_date: datetime
    expiry_date: Optional[datetime] = None
    cost_per_credit: float
    total_cost: float
    stripe_payment_intent_id: Optional[str] = None
    created_at: datetime

class CreditPurchaseRequest(BaseModel):
    restaurant_id: str
    credit_type: CreditType
    quantity: int = Field(..., gt=0)
    payment_method_id: str

# Revenue Analytics Models
class RevenueSource(BaseModel):
    subscription_revenue: float = 0.0
    campaign_credits_revenue: float = 0.0
    overage_charges: float = 0.0
    setup_fees: float = 0.0

class UsageMetrics(BaseModel):
    ai_requests: int = 0
    campaigns_launched: int = 0
    content_generated: int = 0
    features_used: List[str] = []

class CustomerMetrics(BaseModel):
    customer_lifetime_value: float = 0.0
    monthly_recurring_revenue: float = 0.0
    churn_risk_score: float = 0.0
    engagement_score: float = 0.0

class ROICalculations(BaseModel):
    platform_roi: float = 0.0
    feature_roi_breakdown: Dict[str, float] = {}
    cost_per_acquisition: float = 0.0

class RevenueAnalytics(BaseModel):
    analytics_id: str
    restaurant_id: str
    date: datetime
    revenue_sources: RevenueSource
    usage_metrics: UsageMetrics
    customer_metrics: CustomerMetrics
    roi_calculations: ROICalculations
    created_at: datetime

# Platform Revenue Models
class PlatformCustomerMetrics(BaseModel):
    total_customers: int = 0
    new_customers: int = 0
    churned_customers: int = 0
    average_revenue_per_user: float = 0.0

class GrowthMetrics(BaseModel):
    monthly_growth_rate: float = 0.0
    yearly_growth_rate: float = 0.0
    revenue_forecast: Dict[str, float] = {}

class PlatformRevenue(BaseModel):
    aggregate_id: str
    date: datetime
    total_revenue: float
    revenue_by_plan: Dict[str, float] = {}
    revenue_by_feature: Dict[str, float] = {}
    customer_metrics: PlatformCustomerMetrics
    growth_metrics: GrowthMetrics
    created_at: datetime

# AI Assistant Models
class AIAssistantConversation(BaseModel):
    conversation_id: str
    admin_user_id: str
    timestamp: datetime
    query: str
    response: str
    context_data: Dict[str, Any] = {}
    insights_generated: List[str] = []
    actions_recommended: List[str] = []
    follow_up_required: bool = False

class AIInsightCache(BaseModel):
    insight_id: str
    insight_type: InsightType
    generated_at: datetime
    data_sources: List[str] = []
    insight_content: Dict[str, Any] = {}
    confidence_score: float = 0.0
    expiry_date: datetime

class AIAssistantQuery(BaseModel):
    query: str
    context: Optional[str] = None
    admin_id: str

class AIAssistantResponse(BaseModel):
    response: str
    insights: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    follow_up_questions: List[str] = []
    confidence_score: float = 0.0

# Predictive Analytics Models
class MLModelMetrics(BaseModel):
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0

class MLModel(BaseModel):
    model_id: str
    model_type: str  # "churn_prediction", "revenue_forecast", "pricing_optimization"
    model_version: str
    training_data_period: Dict[str, datetime]
    accuracy_metrics: MLModelMetrics
    last_trained: datetime
    model_parameters: Dict[str, Any] = {}
    feature_importance: Dict[str, float] = {}
    active: bool = True

class Prediction(BaseModel):
    prediction_id: str
    model_id: str
    target_entity: str  # restaurant_id or "platform"
    prediction_type: str
    predicted_value: float
    confidence_score: float
    prediction_date: datetime
    actual_outcome: Optional[float] = None
    accuracy_score: Optional[float] = None
    metadata: Dict[str, Any] = {}

# Request/Response Models for APIs
class RevenueAnalyticsRequest(BaseModel):
    restaurant_id: Optional[str] = None
    start_date: datetime
    end_date: datetime
    metrics: List[str] = ["revenue", "usage", "customer"]

class RevenueAnalyticsResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    period: Dict[str, str]
    summary: Dict[str, float]

class CustomerHealthScore(BaseModel):
    restaurant_id: str
    health_score: float  # 0-100
    risk_factors: List[str] = []
    recommendations: List[str] = []
    last_calculated: datetime

class ChurnPrediction(BaseModel):
    restaurant_id: str
    churn_probability: float  # 0-1
    risk_level: str  # "low", "medium", "high"
    contributing_factors: List[str] = []
    recommended_actions: List[str] = []
    prediction_date: datetime

# Billing API Models
class PaymentMethodCreate(BaseModel):
    restaurant_id: str
    stripe_payment_method_id: str
    is_default: bool = True

class BillingDashboardResponse(BaseModel):
    current_subscription: Optional[RestaurantSubscription]
    current_plan: Optional[SubscriptionPlan]
    usage_summary: UsageTracking
    recent_invoices: List[BillingInvoice]
    available_credits: List[CampaignCredits]
    upcoming_charges: float = 0.0

# Admin Dashboard Models
class AdminDashboardSummary(BaseModel):
    total_revenue: float
    monthly_growth: float
    active_customers: int
    churn_rate: float
    top_performing_features: List[Dict[str, Any]]
    at_risk_customers: List[CustomerHealthScore]
    recent_insights: List[AIInsightCache]

class ExecutiveReport(BaseModel):
    report_id: str
    report_type: str
    generated_at: datetime
    period: Dict[str, datetime]
    financial_summary: Dict[str, float]
    growth_metrics: GrowthMetrics
    customer_analysis: Dict[str, Any]
    market_insights: Dict[str, Any]
    recommendations: List[str]

# Webhook Models
class StripeWebhookEvent(BaseModel):
    event_id: str
    event_type: str
    data: Dict[str, Any]
    processed: bool = False
    processed_at: Optional[datetime] = None
    created_at: datetime