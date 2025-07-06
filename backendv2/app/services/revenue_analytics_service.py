"""
Revenue Analytics Service
Advanced revenue analytics and business intelligence for platform optimization
"""
import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import statistics
from ..database import get_database
from ..models_phase3 import (
    RevenueAnalytics, PlatformRevenue, CustomerMetrics, RevenueSource,
    UsageMetrics, ROICalculations, PlatformCustomerMetrics, GrowthMetrics
)

logger = logging.getLogger(__name__)

class RevenueAnalyticsService:
    def __init__(self):
        self.db = None
        
    async def get_db(self):
        """Get database connection"""
        if self.db is None:
            self.db = get_database()
        return self.db

    async def calculate_customer_lifetime_value(self, restaurant_id: str) -> Dict[str, Any]:
        """Calculate CLV based on subscription and usage patterns"""
        try:
            db = await self.get_db()
            
            # Get subscription history
            subscription = await db.restaurant_subscriptions.find_one({"restaurant_id": restaurant_id})
            if not subscription:
                return {"clv": 0.0, "error": "No subscription found"}
            
            # Get billing history
            invoices = await db.billing_invoices.find({
                "restaurant_id": restaurant_id,
                "status": "paid"
            }).sort("invoice_date", 1).to_list(length=None)
            
            if not invoices:
                return {"clv": 0.0, "months_active": 0}
            
            # Calculate metrics
            total_revenue = sum(invoice.get("amount", 0) for invoice in invoices)
            first_invoice = invoices[0]["invoice_date"]
            last_invoice = invoices[-1]["invoice_date"]
            months_active = max(1, (last_invoice - first_invoice).days / 30.44)
            
            monthly_revenue = total_revenue / months_active if months_active > 0 else 0
            
            # Get churn probability (simplified calculation)
            days_since_last_payment = (datetime.utcnow() - last_invoice).days
            churn_risk = min(1.0, days_since_last_payment / 90)  # Higher risk after 90 days
            
            # Calculate CLV using simplified formula
            # CLV = (Monthly Revenue * Gross Margin) / Monthly Churn Rate
            gross_margin = 0.8  # Assume 80% gross margin
            monthly_churn_rate = max(0.05, churn_risk / 12)  # Minimum 5% annual churn
            
            clv = (monthly_revenue * gross_margin) / monthly_churn_rate if monthly_churn_rate > 0 else 0
            
            # Get usage patterns for additional insights
            usage_data = await self._get_usage_patterns(restaurant_id)
            
            return {
                "clv": round(clv, 2),
                "monthly_revenue": round(monthly_revenue, 2),
                "months_active": round(months_active, 1),
                "total_revenue": round(total_revenue, 2),
                "churn_risk": round(churn_risk, 3),
                "usage_patterns": usage_data,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate CLV for {restaurant_id}: {str(e)}")
            return {"clv": 0.0, "error": str(e)}

    async def analyze_revenue_correlation(self, feature_type: str, time_period: int = 30) -> Dict[str, Any]:
        """Analyze correlation between feature usage and revenue"""
        try:
            db = await self.get_db()
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_period)
            
            # Get feature usage data
            usage_pipeline = [
                {"$match": {
                    "timestamp": {"$gte": start_date, "$lte": end_date},
                    "feature_type": feature_type
                }},
                {"$group": {
                    "_id": "$restaurant_id",
                    "usage_count": {"$sum": 1},
                    "avg_processing_time": {"$avg": "$processing_time_ms"},
                    "total_cost": {"$sum": "$estimated_cost"}
                }}
            ]
            
            usage_data = await db.ai_usage_analytics.aggregate(usage_pipeline).to_list(None)
            
            # Get revenue data for the same period
            revenue_data = {}
            for usage in usage_data:
                restaurant_id = usage["_id"]
                
                # Get subscription revenue
                subscription = await db.restaurant_subscriptions.find_one({"restaurant_id": restaurant_id})
                if subscription:
                    plan = await db.subscription_plans.find_one({"plan_id": subscription["plan_id"]})
                    monthly_revenue = plan["price_monthly"] if plan else 0
                    
                    # Get additional charges (credits, overages)
                    additional_revenue = await self._calculate_additional_revenue(restaurant_id, start_date, end_date)
                    
                    revenue_data[restaurant_id] = {
                        "subscription_revenue": monthly_revenue,
                        "additional_revenue": additional_revenue,
                        "total_revenue": monthly_revenue + additional_revenue
                    }
            
            # Calculate correlation
            correlation_analysis = self._calculate_correlation(usage_data, revenue_data)
            
            # Generate insights
            insights = self._generate_revenue_insights(feature_type, correlation_analysis, usage_data, revenue_data)
            
            return {
                "feature_type": feature_type,
                "time_period_days": time_period,
                "correlation_analysis": correlation_analysis,
                "insights": insights,
                "sample_size": len(usage_data),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze revenue correlation: {str(e)}")
            return {"error": str(e)}

    async def predict_churn_risk(self, restaurant_id: str) -> Dict[str, Any]:
        """Predict churn risk using multiple factors"""
        try:
            db = await self.get_db()
            
            # Get subscription data
            subscription = await db.restaurant_subscriptions.find_one({"restaurant_id": restaurant_id})
            if not subscription:
                return {"churn_risk": 0.0, "error": "No subscription found"}
            
            # Calculate risk factors
            risk_factors = []
            risk_score = 0.0
            
            # 1. Payment history
            failed_payments = await db.billing_invoices.count_documents({
                "restaurant_id": restaurant_id,
                "status": "failed"
            })
            if failed_payments > 0:
                payment_risk = min(0.3, failed_payments * 0.1)
                risk_score += payment_risk
                risk_factors.append(f"Payment failures: {failed_payments}")
            
            # 2. Usage patterns
            last_30_days = datetime.utcnow() - timedelta(days=30)
            recent_usage = await db.ai_usage_analytics.count_documents({
                "restaurant_id": restaurant_id,
                "timestamp": {"$gte": last_30_days}
            })
            
            plan = await db.subscription_plans.find_one({"plan_id": subscription["plan_id"]})
            expected_usage = plan["features"]["ai_requests_per_month"] * 0.3 if plan else 10  # 30% of limit
            
            if recent_usage < expected_usage:
                usage_risk = min(0.4, (expected_usage - recent_usage) / expected_usage)
                risk_score += usage_risk
                risk_factors.append(f"Low usage: {recent_usage} vs expected {expected_usage}")
            
            # 3. Support tickets
            # Note: This would require a support ticket system
            # For now, we'll use a placeholder
            
            # 4. Login frequency
            # Note: This would require login tracking
            # For now, we'll use subscription age as a proxy
            subscription_age_days = (datetime.utcnow() - subscription["created_at"]).days
            if subscription_age_days > 90:  # Older subscriptions have higher churn risk
                age_risk = min(0.2, subscription_age_days / 365)
                risk_score += age_risk
                risk_factors.append(f"Subscription age: {subscription_age_days} days")
            
            # 5. Feature adoption
            unique_features = await db.ai_usage_analytics.distinct("feature_type", {
                "restaurant_id": restaurant_id,
                "timestamp": {"$gte": last_30_days}
            })
            
            if len(unique_features) < 2:
                adoption_risk = 0.2
                risk_score += adoption_risk
                risk_factors.append(f"Low feature adoption: {len(unique_features)} features used")
            
            # Normalize risk score (0-1)
            risk_score = min(1.0, risk_score)
            
            # Determine risk level
            if risk_score < 0.3:
                risk_level = "low"
            elif risk_score < 0.7:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            # Generate recommendations
            recommendations = self._generate_churn_prevention_recommendations(risk_level, risk_factors)
            
            return {
                "restaurant_id": restaurant_id,
                "churn_risk": round(risk_score, 3),
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to predict churn risk: {str(e)}")
            return {"churn_risk": 0.0, "error": str(e)}

    async def optimize_pricing_strategy(self, plan_id: str) -> Dict[str, Any]:
        """Analyze pricing optimization opportunities"""
        try:
            db = await self.get_db()
            
            # Get plan details
            plan = await db.subscription_plans.find_one({"plan_id": plan_id})
            if not plan:
                return {"error": "Plan not found"}
            
            # Get subscribers to this plan
            subscribers = await db.restaurant_subscriptions.find({"plan_id": plan_id}).to_list(length=None)
            
            if not subscribers:
                return {"error": "No subscribers found for this plan"}
            
            # Analyze usage patterns
            usage_analysis = await self._analyze_plan_usage(plan_id, subscribers)
            
            # Calculate price elasticity (simplified)
            price_elasticity = await self._calculate_price_elasticity(plan_id)
            
            # Generate pricing recommendations
            recommendations = self._generate_pricing_recommendations(plan, usage_analysis, price_elasticity)
            
            return {
                "plan_id": plan_id,
                "plan_name": plan["name"],
                "current_price": plan["price_monthly"],
                "subscriber_count": len(subscribers),
                "usage_analysis": usage_analysis,
                "price_elasticity": price_elasticity,
                "recommendations": recommendations,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize pricing strategy: {str(e)}")
            return {"error": str(e)}

    async def generate_revenue_forecast(self, months_ahead: int = 12) -> Dict[str, Any]:
        """Generate revenue forecasts using predictive models"""
        try:
            db = await self.get_db()
            
            # Get historical revenue data
            historical_data = await self._get_historical_revenue_data(months_ahead * 2)  # Get 2x data for better prediction
            
            if len(historical_data) < 3:
                return {"error": "Insufficient historical data for forecasting"}
            
            # Calculate trends
            revenue_trend = self._calculate_revenue_trend(historical_data)
            customer_trend = self._calculate_customer_trend()
            
            # Generate forecasts
            forecasts = []
            base_date = datetime.utcnow().replace(day=1)  # Start of current month
            
            for month in range(1, months_ahead + 1):
                forecast_date = base_date + timedelta(days=30 * month)
                
                # Simple linear trend projection with seasonal adjustments
                base_revenue = historical_data[-1]["revenue"]
                trend_adjustment = revenue_trend["monthly_growth"] * month
                seasonal_adjustment = self._get_seasonal_adjustment(forecast_date.month)
                
                forecasted_revenue = base_revenue * (1 + trend_adjustment + seasonal_adjustment)
                
                # Add confidence intervals
                confidence_interval = self._calculate_confidence_interval(forecasted_revenue, month)
                
                forecasts.append({
                    "month": forecast_date.strftime("%Y-%m"),
                    "forecasted_revenue": round(forecasted_revenue, 2),
                    "confidence_low": round(confidence_interval["low"], 2),
                    "confidence_high": round(confidence_interval["high"], 2),
                    "confidence_level": 0.8  # 80% confidence
                })
            
            # Calculate summary metrics
            total_forecasted = sum(f["forecasted_revenue"] for f in forecasts)
            current_annual = sum(h["revenue"] for h in historical_data[-12:]) if len(historical_data) >= 12 else 0
            growth_projection = ((total_forecasted - current_annual) / current_annual * 100) if current_annual > 0 else 0
            
            return {
                "forecast_period": f"{months_ahead} months",
                "forecasts": forecasts,
                "summary": {
                    "total_forecasted_revenue": round(total_forecasted, 2),
                    "projected_annual_growth": round(growth_projection, 1),
                    "average_monthly_revenue": round(total_forecasted / months_ahead, 2)
                },
                "trends": {
                    "revenue_trend": revenue_trend,
                    "customer_trend": customer_trend
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate revenue forecast: {str(e)}")
            return {"error": str(e)}

    async def identify_upsell_opportunities(self, restaurant_id: str) -> Dict[str, Any]:
        """Identify opportunities for plan upgrades"""
        try:
            db = await self.get_db()
            
            # Get current subscription
            subscription = await db.restaurant_subscriptions.find_one({"restaurant_id": restaurant_id})
            if not subscription:
                return {"error": "No subscription found"}
            
            current_plan = await db.subscription_plans.find_one({"plan_id": subscription["plan_id"]})
            if not current_plan:
                return {"error": "Current plan not found"}
            
            # Get usage data
            last_30_days = datetime.utcnow() - timedelta(days=30)
            usage_stats = await self._get_detailed_usage_stats(restaurant_id, last_30_days)
            
            # Get available higher-tier plans
            higher_plans = await db.subscription_plans.find({
                "price_monthly": {"$gt": current_plan["price_monthly"]},
                "active": True
            }).sort("price_monthly", 1).to_list(length=None)
            
            # Analyze upsell opportunities
            opportunities = []
            
            # Check usage limits
            current_usage = usage_stats["ai_requests"]
            current_limit = current_plan["features"]["ai_requests_per_month"]
            usage_percentage = (current_usage / current_limit) * 100 if current_limit > 0 else 0
            
            if usage_percentage > 80:
                opportunities.append({
                    "type": "usage_limit",
                    "reason": f"Using {usage_percentage:.1f}% of AI request limit",
                    "recommended_action": "Upgrade to higher plan to avoid overage charges",
                    "potential_savings": self._calculate_overage_savings(usage_stats, higher_plans)
                })
            
            # Check feature usage patterns
            if not current_plan["features"]["advanced_analytics"] and usage_stats["feature_diversity"] > 3:
                opportunities.append({
                    "type": "feature_access",
                    "reason": "High feature usage suggests need for advanced analytics",
                    "recommended_action": "Upgrade to Professional or Enterprise plan",
                    "value_proposition": "Advanced analytics can improve ROI by 25-40%"
                })
            
            # Check support needs (simplified)
            if not current_plan["features"]["priority_support"]:
                opportunities.append({
                    "type": "support_upgrade",
                    "reason": "Priority support can reduce downtime and improve efficiency",
                    "recommended_action": "Consider Professional plan for priority support",
                    "value_proposition": "Faster issue resolution and dedicated support"
                })
            
            # Calculate ROI for each opportunity
            for opportunity in opportunities:
                opportunity["estimated_roi"] = self._calculate_upsell_roi(opportunity, current_plan, higher_plans)
            
            return {
                "restaurant_id": restaurant_id,
                "current_plan": current_plan["name"],
                "usage_analysis": usage_stats,
                "opportunities": opportunities,
                "recommended_plan": self._recommend_best_plan(opportunities, higher_plans),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to identify upsell opportunities: {str(e)}")
            return {"error": str(e)}

    async def calculate_feature_roi(self, restaurant_id: str, feature_type: str) -> Dict[str, Any]:
        """Calculate ROI for specific features"""
        try:
            db = await self.get_db()
            
            # Get feature usage data
            last_90_days = datetime.utcnow() - timedelta(days=90)
            usage_data = await db.ai_usage_analytics.find({
                "restaurant_id": restaurant_id,
                "feature_type": feature_type,
                "timestamp": {"$gte": last_90_days}
            }).to_list(length=None)
            
            if not usage_data:
                return {"roi": 0.0, "error": "No usage data found for this feature"}
            
            # Calculate costs
            total_cost = sum(item.get("estimated_cost", 0) for item in usage_data)
            usage_count = len(usage_data)
            
            # Estimate value based on feature type
            estimated_value = self._estimate_feature_value(feature_type, usage_count, restaurant_id)
            
            # Calculate ROI
            roi = ((estimated_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
            
            # Get benchmarks
            benchmark_data = await self._get_feature_benchmarks(feature_type)
            
            return {
                "restaurant_id": restaurant_id,
                "feature_type": feature_type,
                "period_days": 90,
                "usage_count": usage_count,
                "total_cost": round(total_cost, 2),
                "estimated_value": round(estimated_value, 2),
                "roi_percentage": round(roi, 1),
                "benchmark_roi": benchmark_data.get("average_roi", 0),
                "performance_vs_benchmark": "above" if roi > benchmark_data.get("average_roi", 0) else "below",
                "recommendations": self._generate_feature_recommendations(feature_type, roi, benchmark_data),
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate feature ROI: {str(e)}")
            return {"roi": 0.0, "error": str(e)}

    # Helper methods
    async def _get_usage_patterns(self, restaurant_id: str) -> Dict[str, Any]:
        """Get detailed usage patterns for a restaurant"""
        try:
            db = await self.get_db()
            last_30_days = datetime.utcnow() - timedelta(days=30)
            
            usage_data = await db.ai_usage_analytics.find({
                "restaurant_id": restaurant_id,
                "timestamp": {"$gte": last_30_days}
            }).to_list(length=None)
            
            if not usage_data:
                return {"total_requests": 0, "features_used": [], "avg_daily_usage": 0}
            
            features_used = list(set(item["feature_type"] for item in usage_data))
            daily_usage = len(usage_data) / 30
            
            return {
                "total_requests": len(usage_data),
                "features_used": features_used,
                "avg_daily_usage": round(daily_usage, 1),
                "feature_diversity": len(features_used)
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage patterns: {str(e)}")
            return {"total_requests": 0, "features_used": [], "avg_daily_usage": 0}

    async def _calculate_additional_revenue(self, restaurant_id: str, start_date: datetime, end_date: datetime) -> float:
        """Calculate additional revenue from credits and overages"""
        try:
            db = await self.get_db()
            
            # Get credit purchases
            credits = await db.campaign_credits.find({
                "restaurant_id": restaurant_id,
                "purchase_date": {"$gte": start_date, "$lte": end_date}
            }).to_list(length=None)
            
            credit_revenue = sum(credit["total_cost"] for credit in credits)
            
            # Get overage charges
            subscription = await db.restaurant_subscriptions.find_one({"restaurant_id": restaurant_id})
            overage_charges = subscription["usage_tracking"].get("overage_charges", 0) if subscription else 0
            
            return credit_revenue + overage_charges
            
        except Exception as e:
            logger.error(f"Failed to calculate additional revenue: {str(e)}")
            return 0.0

    def _calculate_correlation(self, usage_data: List[Dict], revenue_data: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate correlation between usage and revenue"""
        try:
            if len(usage_data) < 2:
                return {"correlation": 0.0, "significance": "insufficient_data"}
            
            # Extract paired data
            usage_values = []
            revenue_values = []
            
            for usage in usage_data:
                restaurant_id = usage["_id"]
                if restaurant_id in revenue_data:
                    usage_values.append(usage["usage_count"])
                    revenue_values.append(revenue_data[restaurant_id]["total_revenue"])
            
            if len(usage_values) < 2:
                return {"correlation": 0.0, "significance": "insufficient_paired_data"}
            
            # Calculate Pearson correlation coefficient (simplified)
            mean_usage = statistics.mean(usage_values)
            mean_revenue = statistics.mean(revenue_values)
            
            numerator = sum((u - mean_usage) * (r - mean_revenue) for u, r in zip(usage_values, revenue_values))
            denominator_usage = sum((u - mean_usage) ** 2 for u in usage_values)
            denominator_revenue = sum((r - mean_revenue) ** 2 for r in revenue_values)
            
            if denominator_usage == 0 or denominator_revenue == 0:
                correlation = 0.0
            else:
                correlation = numerator / (denominator_usage * denominator_revenue) ** 0.5
            
            # Determine significance
            if abs(correlation) > 0.7:
                significance = "strong"
            elif abs(correlation) > 0.3:
                significance = "moderate"
            else:
                significance = "weak"
            
            return {
                "correlation": round(correlation, 3),
                "significance": significance,
                "sample_size": len(usage_values)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate correlation: {str(e)}")
            return {"correlation": 0.0, "significance": "error"}

    def _generate_revenue_insights(self, feature_type: str, correlation: Dict, usage_data: List, revenue_data: Dict) -> List[str]:
        """Generate insights from revenue correlation analysis"""
        insights = []
        
        if correlation["correlation"] > 0.5:
            insights.append(f"Strong positive correlation between {feature_type} usage and revenue")
            insights.append("Consider promoting this feature to increase customer value")
        elif correlation["correlation"] < -0.5:
            insights.append(f"Negative correlation detected - {feature_type} usage may indicate customer issues")
            insights.append("Investigate why high usage correlates with lower revenue")
        else:
            insights.append(f"Weak correlation between {feature_type} usage and revenue")
            insights.append("Feature may need optimization or better positioning")
        
        # Add usage-based insights
        if usage_data:
            avg_usage = statistics.mean(item["usage_count"] for item in usage_data)
            if avg_usage > 100:
                insights.append("High usage volume indicates strong feature adoption")
            elif avg_usage < 10:
                insights.append("Low usage suggests need for better onboarding or feature promotion")
        
        return insights

    def _generate_churn_prevention_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Generate recommendations for churn prevention"""
        recommendations = []
        
        if risk_level == "high":
            recommendations.append("Immediate intervention required - schedule customer success call")
            recommendations.append("Offer personalized onboarding or training session")
            recommendations.append("Consider temporary discount or additional credits")
        elif risk_level == "medium":
            recommendations.append("Proactive outreach recommended within 1 week")
            recommendations.append("Send feature adoption guide and best practices")
            recommendations.append("Monitor usage closely for next 30 days")
        else:
            recommendations.append("Continue regular check-ins")
            recommendations.append("Share success stories and advanced features")
        
        # Add specific recommendations based on risk factors
        for factor in risk_factors:
            if "payment" in factor.lower():
                recommendations.append("Update payment method or offer payment plan")
            elif "usage" in factor.lower():
                recommendations.append("Provide feature training and usage optimization tips")
            elif "adoption" in factor.lower():
                recommendations.append("Demonstrate value of unused features")
        
        return recommendations

    async def _get_historical_revenue_data(self, months: int) -> List[Dict[str, Any]]:
        """Get historical revenue data for forecasting"""
        try:
            db = await self.get_db()
            
            # This is a simplified version - in production, you'd have proper revenue aggregation
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30 * months)
            
            # Get monthly revenue aggregates (placeholder data for now)
            monthly_data = []
            current_date = start_date.replace(day=1)
            
            while current_date < end_date:
                next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
                
                # Get subscription revenue for this month
                subscriptions = await db.restaurant_subscriptions.find({
                    "created_at": {"$lte": next_month},
                    "$or": [
                        {"canceled_at": {"$gte": current_date}},
                        {"canceled_at": None}
                    ]
                }).to_list(length=None)
                
                monthly_revenue = 0.0
                for sub in subscriptions:
                    plan = await db.subscription_plans.find_one({"plan_id": sub["plan_id"]})
                    if plan:
                        monthly_revenue += plan["price_monthly"]
                
                monthly_data.append({
                    "month": current_date.strftime("%Y-%m"),
                    "revenue": monthly_revenue,
                    "date": current_date
                })
                
                current_date = next_month
            
            return monthly_data
            
        except Exception as e:
            logger.error(f"Failed to get historical revenue data: {str(e)}")
            return []

    def _calculate_revenue_trend(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Calculate revenue trend from historical data"""
        if len(historical_data) < 2:
            return {"monthly_growth": 0.0, "trend": "insufficient_data"}
        
        revenues = [item["revenue"] for item in historical_data]
        
        # Calculate month-over-month growth rates
        growth_rates = []
        for i in range(1, len(revenues)):
            if revenues[i-1] > 0:
                growth_rate = (revenues[i] - revenues[i-1]) / revenues[i-1]
                growth_rates.append(growth_rate)
        
        if not growth_rates:
            return {"monthly_growth": 0.0, "trend": "no_growth_data"}
        
        avg_growth = statistics.mean(growth_rates)
        
        if avg_growth > 0.05:
            trend = "strong_growth"
        elif avg_growth > 0.02:
            trend = "moderate_growth"
        elif avg_growth > -0.02:
            trend = "stable"
        else:
            trend = "declining"
        
        return {
            "monthly_growth": round(avg_growth, 4),
            "trend": trend,
            "growth_rates": [round(gr, 4) for gr in growth_rates]
        }

    def _calculate_customer_trend(self) -> Dict[str, Any]:
        """Calculate customer acquisition and churn trends"""
        # Placeholder implementation
        return {
            "acquisition_rate": 0.15,  # 15% monthly growth
            "churn_rate": 0.05,  # 5% monthly churn
            "net_growth": 0.10  # 10% net growth
        }

    def _get_seasonal_adjustment(self, month: int) -> float:
        """Get seasonal adjustment factor for revenue forecasting"""
        # Simplified seasonal adjustments (restaurant industry patterns)
        seasonal_factors = {
            1: -0.1,   # January (post-holiday decline)
            2: -0.05,  # February
            3: 0.0,    # March
            4: 0.05,   # April
            5: 0.1,    # May (spring increase)
            6: 0.15,   # June (summer peak)
            7: 0.15,   # July
            8: 0.1,    # August
            9: 0.05,   # September
            10: 0.1,   # October
            11: 0.15,  # November (holiday season)
            12: 0.2    # December (peak holiday)
        }
        
        return seasonal_factors.get(month, 0.0)

    def _calculate_confidence_interval(self, forecasted_value: float, months_ahead: int) -> Dict[str, float]:
        """Calculate confidence intervals for forecasts"""
        # Confidence decreases with time
        uncertainty = 0.1 + (months_ahead * 0.02)  # 10% base + 2% per month
        return {
            "low": forecasted_value * (1 - uncertainty),
            "high": forecasted_value * (1 + uncertainty)
        }

    async def _analyze_plan_usage(self, plan_id: str, subscribers: List[Dict]) -> Dict[str, Any]:
        """Analyze usage patterns for a specific plan"""
        try:
            db = await self.get_db()
            
            usage_stats = {
                "total_subscribers": len(subscribers),
                "avg_usage_percentage": 0.0,
                "high_usage_count": 0,
                "low_usage_count": 0
            }
            
            plan = await db.subscription_plans.find_one({"plan_id": plan_id})
            if not plan:
                return usage_stats
            
            monthly_limit = plan["features"]["ai_requests_per_month"]
            usage_percentages = []
            
            for subscriber in subscribers:
                usage = subscriber["usage_tracking"]["ai_requests_used"]
                usage_percentage = (usage / monthly_limit) * 100 if monthly_limit > 0 else 0
                usage_percentages.append(usage_percentage)
                
                if usage_percentage > 80:
                    usage_stats["high_usage_count"] += 1
                elif usage_percentage < 20:
                    usage_stats["low_usage_count"] += 1
            
            if usage_percentages:
                usage_stats["avg_usage_percentage"] = statistics.mean(usage_percentages)
            
            return usage_stats
            
        except Exception as e:
            logger.error(f"Failed to analyze plan usage: {str(e)}")
            return {"error": str(e)}

    async def _calculate_price_elasticity(self, plan_id: str) -> Dict[str, Any]:
        """Calculate price elasticity for a plan (simplified)"""
        # This is a placeholder - real implementation would require historical pricing data
        return {
            "elasticity": -0.5,  # Typical SaaS elasticity
            "confidence": "estimated",
            "note": "Based on industry benchmarks"
        }

    def _generate_pricing_recommendations(self, plan: Dict, usage_analysis: Dict, price_elasticity: Dict) -> List[str]:
        """Generate pricing optimization recommendations"""
        recommendations = []
        
        current_price = plan["price_monthly"]
        avg_usage = usage_analysis.get("avg_usage_percentage", 0)
        high_usage_count = usage_analysis.get("high_usage_count", 0)
        low_usage_count = usage_analysis.get("low_usage_count", 0)
        total_subscribers = usage_analysis.get("total_subscribers", 0)
        
        if avg_usage > 80:
            recommendations.append(f"Consider 10-15% price increase - high usage indicates strong value perception")
        elif avg_usage < 30:
            recommendations.append(f"Consider reducing features or price - low usage suggests poor value fit")
        
        if high_usage_count > total_subscribers * 0.3:
            recommendations.append("Add usage-based pricing tier for high-usage customers")
        
        if low_usage_count > total_subscribers * 0.4:
            recommendations.append("Create lower-tier plan to retain price-sensitive customers")
        
        return recommendations

    async def _get_detailed_usage_stats(self, restaurant_id: str, since_date: datetime) -> Dict[str, Any]:
        """Get detailed usage statistics for upsell analysis"""
        try:
            db = await self.get_db()
            
            usage_data = await db.ai_usage_analytics.find({
                "restaurant_id": restaurant_id,
                "timestamp": {"$gte": since_date}
            }).to_list(length=None)
            
            features_used = list(set(item["feature_type"] for item in usage_data))
            
            return {
                "ai_requests": len(usage_data),
                "feature_diversity": len(features_used),
                "features_used": features_used,
                "avg_processing_time": statistics.mean([item.get("processing_time_ms", 0) for item in usage_data]) if usage_data else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get detailed usage stats: {str(e)}")
            return {"ai_requests": 0, "feature_diversity": 0, "features_used": []}

    def _calculate_overage_savings(self, usage_stats: Dict, higher_plans: List[Dict]) -> float:
        """Calculate potential savings from avoiding overage charges"""
        # Simplified calculation
        current_usage = usage_stats["ai_requests"]
        overage_cost = max(0, (current_usage - 100) * 0.10)  # Assume $0.10 per overage
        
        return overage_cost

    def _calculate_upsell_roi(self, opportunity: Dict, current_plan: Dict, higher_plans: List[Dict]) -> float:
        """Calculate ROI for upsell opportunity"""
        # Simplified ROI calculation
        if opportunity["type"] == "usage_limit":
            return 150.0  # 150% ROI from avoiding overages
        elif opportunity["type"] == "feature_access":
            return 200.0  # 200% ROI from advanced features
        else:
            return 100.0  # 100% baseline ROI

    def _recommend_best_plan(self, opportunities: List[Dict], higher_plans: List[Dict]) -> Optional[str]:
        """Recommend the best plan based on opportunities"""
        if not higher_plans:
            return None
        
        # Simple logic - recommend the lowest-priced higher plan if there are opportunities
        if opportunities:
            return higher_plans[0]["name"]
        
        return None

    async def _estimate_feature_value(self, feature_type: str, usage_count: int, restaurant_id: str) -> float:
        """Estimate the business value generated by a feature"""
        # Simplified value estimation based on feature type
        value_per_use = {
            "content_generation": 5.0,  # $5 value per content piece
            "image_enhancement": 3.0,   # $3 value per image
            "marketing_assistant": 10.0, # $10 value per marketing insight
            "menu_optimizer": 15.0,     # $15 value per menu optimization
            "digital_grader": 8.0       # $8 value per grade/analysis
        }
        
        base_value = value_per_use.get(feature_type, 5.0) * usage_count
        
        # Add multiplier based on restaurant size/revenue (simplified)
        # In real implementation, this would use actual restaurant data
        size_multiplier = 1.2  # Assume 20% premium for established restaurants
        
        return base_value * size_multiplier

    async def _get_feature_benchmarks(self, feature_type: str) -> Dict[str, Any]:
        """Get benchmark data for feature performance"""
        # Placeholder benchmarks - in production, these would be calculated from actual data
        benchmarks = {
            "content_generation": {"average_roi": 180.0, "top_quartile_roi": 250.0},
            "image_enhancement": {"average_roi": 150.0, "top_quartile_roi": 200.0},
            "marketing_assistant": {"average_roi": 220.0, "top_quartile_roi": 300.0},
            "menu_optimizer": {"average_roi": 280.0, "top_quartile_roi": 400.0},
            "digital_grader": {"average_roi": 160.0, "top_quartile_roi": 220.0}
        }
        
        return benchmarks.get(feature_type, {"average_roi": 150.0, "top_quartile_roi": 200.0})

    def _generate_feature_recommendations(self, feature_type: str, roi: float, benchmark_data: Dict) -> List[str]:
        """Generate recommendations for feature optimization"""
        recommendations = []
        
        benchmark_roi = benchmark_data.get("average_roi", 150.0)
        top_quartile_roi = benchmark_data.get("top_quartile_roi", 200.0)
        
        if roi > top_quartile_roi:
            recommendations.append(f"Excellent ROI! Consider increasing usage of {feature_type}")
            recommendations.append("Share success story with other customers")
        elif roi > benchmark_roi:
            recommendations.append(f"Above-average ROI for {feature_type}")
            recommendations.append("Explore advanced features to maximize value")
        elif roi > 0:
            recommendations.append(f"Below-average ROI for {feature_type}")
            recommendations.append("Consider optimization training or feature review")
        else:
            recommendations.append(f"Negative ROI detected for {feature_type}")
            recommendations.append("Immediate review recommended - may need different approach")
        
        return recommendations

# Create service instance
revenue_analytics_service = RevenueAnalyticsService()
        