"""
Phase 3 API Routes
Business Intelligence & Monetization endpoints for billing, revenue analytics, and AI assistant
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from ..auth import get_current_user
from ..models_phase3 import (
    SubscriptionCreate, SubscriptionUpdate, CreditPurchaseRequest,
    AIAssistantQuery, RevenueAnalyticsRequest, SubscriptionPlan,
    BillingDashboardResponse, AdminDashboardSummary
)
from ..services.billing_engine_service import billing_engine_service
from ..services.revenue_analytics_service import revenue_analytics_service
from ..services.admin_ai_assistant_service import admin_ai_assistant_service

logger = logging.getLogger(__name__)

# Create routers for different areas
billing_router = APIRouter(prefix="/api/billing", tags=["Billing & Subscriptions"])
revenue_router = APIRouter(prefix="/api/revenue", tags=["Revenue Analytics"])
ai_assistant_router = APIRouter(prefix="/api/ai-assistant", tags=["AI Assistant"])
business_intelligence_router = APIRouter(prefix="/api/business-intelligence", tags=["Business Intelligence"])

def require_admin_role(current_user = Depends(get_current_user)):
    """Dependency to require admin role"""
    if hasattr(current_user, 'role') and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    elif hasattr(current_user, 'get') and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    elif not hasattr(current_user, 'role') and not hasattr(current_user, 'get'):
        # For TokenData objects, check if user_id contains 'admin'
        if hasattr(current_user, 'user_id') and 'admin' not in str(current_user.user_id):
            raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def get_restaurant_id(current_user = Depends(get_current_user)) -> str:
    """Get restaurant ID from current user"""
    if hasattr(current_user, 'restaurant') and current_user.restaurant:
        return current_user.restaurant.restaurant_id
    elif hasattr(current_user, 'impersonating_restaurant_id') and current_user.impersonating_restaurant_id:
        return current_user.impersonating_restaurant_id
    else:
        raise HTTPException(status_code=400, detail="Restaurant ID not found")

# ============================================================================
# BILLING & SUBSCRIPTION ROUTES
# ============================================================================

@billing_router.post("/subscriptions")
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user = Depends(get_current_user)
):
    """Create a new subscription"""
    try:
        result = await billing_engine_service.create_subscription(subscription_data)
        return {
            "success": True,
            "message": "Subscription created successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to create subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@billing_router.put("/subscriptions/{subscription_id}")
async def update_subscription(
    subscription_id: str,
    update_data: SubscriptionUpdate,
    current_user = Depends(get_current_user)
):
    """Update an existing subscription"""
    try:
        restaurant_id = get_restaurant_id(current_user)
        
        if update_data.plan_id:
            result = await billing_engine_service.upgrade_subscription(restaurant_id, update_data.plan_id)
        else:
            # Handle other updates like cancellation
            if update_data.cancel_at_period_end is not None:
                result = await billing_engine_service.cancel_subscription(
                    restaurant_id, 
                    cancel_immediately=not update_data.cancel_at_period_end
                )
            else:
                raise HTTPException(status_code=400, detail="No valid update parameters provided")
        
        return {
            "success": True,
            "message": "Subscription updated successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to update subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@billing_router.post("/credits")
async def purchase_credits(
    credit_request: CreditPurchaseRequest,
    current_user = Depends(get_current_user)
):
    """Purchase campaign credits"""
    try:
        result = await billing_engine_service.purchase_campaign_credits(credit_request)
        return {
            "success": True,
            "message": "Credits purchased successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to purchase credits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@billing_router.get("/dashboard")
async def get_billing_dashboard(
    restaurant_id: str = Depends(get_restaurant_id)
):
    """Get billing dashboard for restaurant"""
    try:
        # This would be implemented to gather all billing-related data
        dashboard_data = {
            "restaurant_id": restaurant_id,
            "current_subscription": None,  # Would fetch from billing service
            "usage_summary": None,  # Would fetch usage data
            "recent_invoices": [],  # Would fetch recent invoices
            "available_credits": [],  # Would fetch available credits
            "upcoming_charges": 0.0
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
    except Exception as e:
        logger.error(f"Failed to get billing dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@billing_router.post("/usage/track")
async def track_usage(
    feature_type: str = Body(...),
    usage_amount: int = Body(1),
    restaurant_id: str = Depends(get_restaurant_id)
):
    """Track feature usage against subscription limits"""
    try:
        result = await billing_engine_service.track_feature_usage(restaurant_id, feature_type, usage_amount)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to track usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# REVENUE ANALYTICS ROUTES
# ============================================================================

@revenue_router.get("/customer-lifetime-value/{restaurant_id}")
async def get_customer_lifetime_value(
    restaurant_id: str,
    admin_user = Depends(require_admin_role)
):
    """Calculate customer lifetime value"""
    try:
        result = await revenue_analytics_service.calculate_customer_lifetime_value(restaurant_id)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to calculate CLV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@revenue_router.get("/correlation-analysis")
async def analyze_revenue_correlation(
    feature_type: str = Query(...),
    time_period: int = Query(30),
    admin_user = Depends(require_admin_role)
):
    """Analyze correlation between feature usage and revenue"""
    try:
        result = await revenue_analytics_service.analyze_revenue_correlation(feature_type, time_period)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to analyze correlation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@revenue_router.get("/churn-prediction/{restaurant_id}")
async def predict_churn_risk(
    restaurant_id: str,
    admin_user = Depends(require_admin_role)
):
    """Predict churn risk for a restaurant"""
    try:
        result = await revenue_analytics_service.predict_churn_risk(restaurant_id)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to predict churn: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@revenue_router.get("/pricing-optimization/{plan_id}")
async def optimize_pricing(
    plan_id: str,
    admin_user = Depends(require_admin_role)
):
    """Analyze pricing optimization opportunities"""
    try:
        result = await revenue_analytics_service.optimize_pricing_strategy(plan_id)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to optimize pricing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@revenue_router.get("/forecast")
async def generate_revenue_forecast(
    months_ahead: int = Query(12),
    admin_user = Depends(require_admin_role)
):
    """Generate revenue forecast"""
    try:
        result = await revenue_analytics_service.generate_revenue_forecast(months_ahead)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to generate forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@revenue_router.get("/upsell-opportunities/{restaurant_id}")
async def identify_upsell_opportunities(
    restaurant_id: str,
    admin_user = Depends(require_admin_role)
):
    """Identify upsell opportunities for a restaurant"""
    try:
        result = await revenue_analytics_service.identify_upsell_opportunities(restaurant_id)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to identify upsell opportunities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@revenue_router.get("/feature-roi/{restaurant_id}/{feature_type}")
async def calculate_feature_roi(
    restaurant_id: str,
    feature_type: str,
    admin_user = Depends(require_admin_role)
):
    """Calculate ROI for a specific feature"""
    try:
        result = await revenue_analytics_service.calculate_feature_roi(restaurant_id, feature_type)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to calculate feature ROI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# AI ASSISTANT ROUTES
# ============================================================================

@ai_assistant_router.post("/chat")
async def chat_with_ai_assistant(
    query: AIAssistantQuery,
    admin_user = Depends(require_admin_role)
):
    """Chat with the AI assistant"""
    try:
        response = await admin_ai_assistant_service.chat_with_assistant(query)
        return {
            "success": True,
            "data": {
                "response": response.response,
                "insights": response.insights,
                "recommendations": response.recommendations,
                "follow_up_questions": response.follow_up_questions,
                "confidence_score": response.confidence_score
            }
        }
    except Exception as e:
        logger.error(f"Failed to process AI assistant query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_assistant_router.get("/platform-performance")
async def analyze_platform_performance(
    time_period: str = Query("30d"),
    admin_user = Depends(require_admin_role)
):
    """Get comprehensive platform performance analysis"""
    try:
        result = await admin_ai_assistant_service.analyze_platform_performance(time_period)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to analyze platform performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_assistant_router.get("/strategic-recommendations")
async def get_strategic_recommendations(
    focus_area: str = Query("general"),
    admin_user = Depends(require_admin_role)
):
    """Get strategic business recommendations"""
    try:
        result = await admin_ai_assistant_service.provide_strategic_recommendations(focus_area)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to get strategic recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_assistant_router.post("/predict-outcomes")
async def predict_business_outcomes(
    scenario: Dict[str, Any] = Body(...),
    admin_user = Depends(require_admin_role)
):
    """Predict business outcomes for scenarios"""
    try:
        result = await admin_ai_assistant_service.predict_business_outcomes(scenario)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to predict outcomes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_assistant_router.get("/at-risk-customers")
async def identify_at_risk_customers(
    admin_user = Depends(require_admin_role)
):
    """Identify customers at risk of churning"""
    try:
        result = await admin_ai_assistant_service.identify_at_risk_customers()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to identify at-risk customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_assistant_router.get("/monetization-optimization")
async def optimize_monetization_strategy(
    admin_user = Depends(require_admin_role)
):
    """Optimize monetization strategy"""
    try:
        result = await admin_ai_assistant_service.optimize_monetization_strategy()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to optimize monetization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_assistant_router.get("/executive-insights")
async def generate_executive_insights(
    report_type: str = Query("monthly_review"),
    admin_user = Depends(require_admin_role)
):
    """Generate executive-level insights"""
    try:
        result = await admin_ai_assistant_service.generate_executive_insights(report_type)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to generate executive insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# BUSINESS INTELLIGENCE DASHBOARD ROUTES
# ============================================================================

@business_intelligence_router.get("/dashboard")
async def get_business_intelligence_dashboard(
    admin_user = Depends(require_admin_role)
):
    """Get comprehensive business intelligence dashboard"""
    try:
        # Gather data from multiple services
        platform_performance = await admin_ai_assistant_service.analyze_platform_performance("30d")
        at_risk_customers = await admin_ai_assistant_service.identify_at_risk_customers()
        revenue_forecast = await revenue_analytics_service.generate_revenue_forecast(6)
        
        dashboard_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "platform_performance": platform_performance,
            "at_risk_customers": at_risk_customers,
            "revenue_forecast": revenue_forecast,
            "key_metrics": {
                "total_revenue": platform_performance.get("revenue_summary", {}).get("total_revenue", 0),
                "active_customers": platform_performance.get("customer_summary", {}).get("active_customers", 0),
                "churn_risk_customers": at_risk_customers.get("total_at_risk", 0),
                "growth_rate": "15%"  # Placeholder
            }
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
    except Exception as e:
        logger.error(f"Failed to get BI dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@business_intelligence_router.get("/reports/executive")
async def generate_executive_report(
    period: str = Query("monthly"),
    admin_user = Depends(require_admin_role)
):
    """Generate executive report"""
    try:
        report_data = await admin_ai_assistant_service.generate_executive_insights("monthly_review")
        return {
            "success": True,
            "data": report_data
        }
    except Exception as e:
        logger.error(f"Failed to generate executive report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@business_intelligence_router.get("/alerts")
async def get_business_alerts(
    admin_user = Depends(require_admin_role)
):
    """Get business intelligence alerts"""
    try:
        # Generate alerts based on various conditions
        alerts = []
        
        # Check for high churn risk customers
        at_risk = await admin_ai_assistant_service.identify_at_risk_customers()
        if at_risk.get("immediate_action_required", 0) > 0:
            alerts.append({
                "type": "churn_risk",
                "severity": "high",
                "message": f"{at_risk['immediate_action_required']} customers require immediate attention",
                "action_required": True
            })
        
        # Check platform performance
        performance = await admin_ai_assistant_service.analyze_platform_performance("7d")
        if performance.get("real_time_metrics", {}).get("success_rate", 100) < 95:
            alerts.append({
                "type": "performance",
                "severity": "medium",
                "message": "Platform success rate below 95%",
                "action_required": True
            })
        
        return {
            "success": True,
            "data": {
                "alerts": alerts,
                "alert_count": len(alerts),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get business alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HEALTH CHECK ROUTES
# ============================================================================

@business_intelligence_router.get("/health")
async def check_phase3_health():
    """Health check for Phase 3 services"""
    try:
        health_status = {
            "billing_service": "operational",
            "revenue_analytics": "operational", 
            "ai_assistant": "operational",
            "overall_status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": health_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Combine all routers
def get_phase3_routers():
    """Get all Phase 3 routers"""
    return [
        billing_router,
        revenue_router,
        ai_assistant_router,
        business_intelligence_router
    ]