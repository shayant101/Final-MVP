#!/usr/bin/env python3
"""
Phase 3 Sample Data Population Script
Populates subscription plans, billing data, and analytics for testing
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_database
from app.models_phase3 import SubscriptionPlan, RestaurantSubscription, BillingInvoice, CampaignCredits

async def populate_subscription_plans():
    """Create subscription plans"""
    db = get_database()
    
    plans = [
        {
            "_id": "starter_plan",
            "name": "Starter",
            "description": "Perfect for small restaurants getting started with AI marketing",
            "price": 49.00,
            "billing_cycle": "monthly",
            "features": {
                "ai_content_generation": 50,
                "campaign_management": 10,
                "analytics_reports": 5,
                "customer_support": "email"
            },
            "limits": {
                "monthly_campaigns": 10,
                "content_generations": 50,
                "analytics_exports": 5
            },
            "stripe_price_id": "price_starter_monthly",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": "professional_plan",
            "name": "Professional",
            "description": "Advanced features for growing restaurants",
            "price": 99.00,
            "billing_cycle": "monthly",
            "features": {
                "ai_content_generation": 200,
                "campaign_management": 50,
                "analytics_reports": 20,
                "customer_support": "priority_email",
                "advanced_analytics": True,
                "custom_branding": True
            },
            "limits": {
                "monthly_campaigns": 50,
                "content_generations": 200,
                "analytics_exports": 20
            },
            "stripe_price_id": "price_professional_monthly",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": "enterprise_plan",
            "name": "Enterprise",
            "description": "Unlimited features for restaurant chains and large operations",
            "price": 199.00,
            "billing_cycle": "monthly",
            "features": {
                "ai_content_generation": -1,  # Unlimited
                "campaign_management": -1,    # Unlimited
                "analytics_reports": -1,     # Unlimited
                "customer_support": "phone_and_email",
                "advanced_analytics": True,
                "custom_branding": True,
                "api_access": True,
                "dedicated_account_manager": True
            },
            "limits": {
                "monthly_campaigns": -1,     # Unlimited
                "content_generations": -1,   # Unlimited
                "analytics_exports": -1      # Unlimited
            },
            "stripe_price_id": "price_enterprise_monthly",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert subscription plans
    for plan in plans:
        await db.subscription_plans.replace_one(
            {"_id": plan["_id"]}, 
            plan, 
            upsert=True
        )
    
    print(f"✅ Created {len(plans)} subscription plans")
    return plans

async def populate_restaurant_subscriptions():
    """Create sample restaurant subscriptions"""
    db = get_database()
    
    # Get existing restaurants from the database
    restaurants = await db.restaurants.find({}).to_list(length=None)
    
    if not restaurants:
        print("⚠️ No restaurants found. Creating sample restaurant subscriptions anyway.")
        # Create sample restaurant IDs
        restaurant_ids = ["rest_001", "rest_002", "rest_003"]
    else:
        restaurant_ids = [str(r["_id"]) for r in restaurants[:3]]
    
    subscriptions = []
    plans = ["starter_plan", "professional_plan", "enterprise_plan"]
    
    for i, restaurant_id in enumerate(restaurant_ids):
        plan_id = plans[i % len(plans)]
        
        subscription = {
            "_id": f"sub_{restaurant_id}",
            "restaurant_id": restaurant_id,
            "plan_id": plan_id,
            "stripe_subscription_id": f"sub_stripe_{restaurant_id}",
            "status": "active",
            "current_period_start": datetime.utcnow() - timedelta(days=15),
            "current_period_end": datetime.utcnow() + timedelta(days=15),
            "cancel_at_period_end": False,
            "usage_tracking": {
                "ai_content_generation": 25 + (i * 10),
                "campaign_management": 5 + (i * 2),
                "analytics_reports": 2 + i
            },
            "billing_history": [],
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow()
        }
        
        subscriptions.append(subscription)
        
        await db.restaurant_subscriptions.replace_one(
            {"_id": subscription["_id"]}, 
            subscription, 
            upsert=True
        )
    
    print(f"✅ Created {len(subscriptions)} restaurant subscriptions")
    return subscriptions

async def populate_billing_invoices():
    """Create sample billing invoices"""
    db = get_database()
    
    # Get restaurant subscriptions
    subscriptions = await db.restaurant_subscriptions.find({}).to_list(length=None)
    
    invoices = []
    
    for i, subscription in enumerate(subscriptions):
        # Create 3 invoices per subscription (past 3 months)
        for month_offset in range(3):
            invoice_date = datetime.utcnow() - timedelta(days=30 * (month_offset + 1))
            
            invoice = {
                "_id": f"inv_{subscription['restaurant_id']}_{month_offset}",
                "restaurant_id": subscription["restaurant_id"],
                "subscription_id": subscription["_id"],
                "stripe_invoice_id": f"in_stripe_{subscription['restaurant_id']}_{month_offset}",
                "amount_due": 49.00 + (i * 50),  # Varying amounts
                "amount_paid": 49.00 + (i * 50),
                "currency": "usd",
                "status": "paid",
                "invoice_date": invoice_date,
                "due_date": invoice_date + timedelta(days=7),
                "paid_date": invoice_date + timedelta(days=2),
                "line_items": [
                    {
                        "description": f"Subscription - {subscription['plan_id'].replace('_', ' ').title()}",
                        "amount": 49.00 + (i * 50),
                        "quantity": 1
                    }
                ],
                "created_at": invoice_date,
                "updated_at": invoice_date + timedelta(days=2)
            }
            
            invoices.append(invoice)
            
            await db.billing_invoices.replace_one(
                {"_id": invoice["_id"]}, 
                invoice, 
                upsert=True
            )
    
    print(f"✅ Created {len(invoices)} billing invoices")
    return invoices

async def populate_campaign_credits():
    """Create sample campaign credits"""
    db = get_database()
    
    # Get restaurant subscriptions
    subscriptions = await db.restaurant_subscriptions.find({}).to_list(length=None)
    
    credits = []
    
    for i, subscription in enumerate(subscriptions):
        credit = {
            "_id": f"credits_{subscription['restaurant_id']}",
            "restaurant_id": subscription["restaurant_id"],
            "total_credits": 1000 + (i * 500),
            "used_credits": 250 + (i * 100),
            "remaining_credits": 750 + (i * 400),
            "credit_history": [
                {
                    "transaction_id": f"txn_purchase_{i}",
                    "type": "purchase",
                    "amount": 1000 + (i * 500),
                    "description": "Initial credit purchase",
                    "timestamp": datetime.utcnow() - timedelta(days=20)
                },
                {
                    "transaction_id": f"txn_usage_{i}_1",
                    "type": "usage",
                    "amount": -150,
                    "description": "Campaign: Summer Special",
                    "timestamp": datetime.utcnow() - timedelta(days=15)
                },
                {
                    "transaction_id": f"txn_usage_{i}_2",
                    "type": "usage",
                    "amount": -100 - (i * 100),
                    "description": "Campaign: Weekend Promotion",
                    "timestamp": datetime.utcnow() - timedelta(days=10)
                }
            ],
            "last_purchase_date": datetime.utcnow() - timedelta(days=20),
            "expiry_date": datetime.utcnow() + timedelta(days=365),
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow()
        }
        
        credits.append(credit)
        
        await db.campaign_credits.replace_one(
            {"_id": credit["_id"]}, 
            credit, 
            upsert=True
        )
    
    print(f"✅ Created {len(credits)} campaign credit records")
    return credits

async def populate_revenue_analytics():
    """Create sample revenue analytics data"""
    db = get_database()
    
    # Get restaurant subscriptions
    subscriptions = await db.restaurant_subscriptions.find({}).to_list(length=None)
    
    analytics = []
    
    for i, subscription in enumerate(subscriptions):
        # Create monthly analytics for the past 6 months
        for month_offset in range(6):
            analytics_date = datetime.utcnow() - timedelta(days=30 * month_offset)
            
            analytic = {
                "_id": f"analytics_{subscription['restaurant_id']}_{month_offset}",
                "restaurant_id": subscription["restaurant_id"],
                "period_start": analytics_date.replace(day=1),
                "period_end": analytics_date.replace(day=28),  # Simplified
                "metrics": {
                    "total_revenue": 1000 + (i * 200) + (month_offset * 50),
                    "subscription_revenue": 49 + (i * 50),
                    "credits_revenue": 200 + (i * 30),
                    "customer_acquisition_cost": 25.50,
                    "customer_lifetime_value": 850 + (i * 100),
                    "churn_risk_score": 0.15 + (i * 0.05),
                    "feature_usage": {
                        "ai_content_generation": 45 + (i * 10),
                        "campaign_management": 8 + (i * 2),
                        "analytics_reports": 3 + i
                    }
                },
                "predictions": {
                    "next_month_revenue": 1100 + (i * 220),
                    "churn_probability": 0.12 + (i * 0.03),
                    "upsell_opportunity": "high" if i == 0 else "medium" if i == 1 else "low"
                },
                "created_at": analytics_date,
                "updated_at": analytics_date
            }
            
            analytics.append(analytic)
            
            await db.revenue_analytics.replace_one(
                {"_id": analytic["_id"]}, 
                analytic, 
                upsert=True
            )
    
    print(f"✅ Created {len(analytics)} revenue analytics records")
    return analytics

async def populate_ai_assistant_conversations():
    """Create sample AI assistant conversations"""
    db = get_database()
    
    conversations = [
        {
            "_id": "conv_admin_001",
            "admin_user_id": "admin",
            "conversation_history": [
                {
                    "timestamp": datetime.utcnow() - timedelta(hours=2),
                    "user_message": "What's our current churn rate?",
                    "assistant_response": "Based on the latest analytics, your platform has a churn rate of 8.5% this month, which is below the industry average of 12%. The main factors contributing to churn are: 1) Limited feature usage (40% of churned customers), 2) Pricing concerns (35%), and 3) Technical issues (25%).",
                    "insights": ["Churn rate trending downward", "Feature adoption is key retention factor"],
                    "recommendations": ["Implement onboarding program", "Consider usage-based pricing tier"]
                },
                {
                    "timestamp": datetime.utcnow() - timedelta(hours=1),
                    "user_message": "Which customers are at highest risk?",
                    "assistant_response": "I've identified 3 customers at high churn risk: Restaurant A (85% risk - low engagement), Restaurant B (78% risk - payment issues), Restaurant C (72% risk - feature underutilization). I recommend immediate outreach with personalized retention offers.",
                    "insights": ["3 high-risk customers identified", "Engagement patterns predict churn"],
                    "recommendations": ["Schedule customer success calls", "Offer feature training sessions"]
                }
            ],
            "total_interactions": 15,
            "created_at": datetime.utcnow() - timedelta(days=7),
            "updated_at": datetime.utcnow() - timedelta(hours=1)
        },
        {
            "_id": "conv_admin_002",
            "admin_user_id": "admin",
            "conversation_history": [
                {
                    "timestamp": datetime.utcnow() - timedelta(minutes=30),
                    "user_message": "How can we optimize our pricing strategy?",
                    "assistant_response": "Analysis suggests a 3-tier optimization: 1) Increase Starter plan to $59 (demand elasticity supports 20% increase), 2) Add 'Growth' tier at $149 between Professional and Enterprise, 3) Introduce annual discounts (15% off) to improve retention. Projected revenue increase: 23%.",
                    "insights": ["Price elasticity analysis complete", "Market positioning optimal"],
                    "recommendations": ["Test price increase with A/B testing", "Launch annual billing promotion"]
                }
            ],
            "total_interactions": 8,
            "created_at": datetime.utcnow() - timedelta(days=3),
            "updated_at": datetime.utcnow() - timedelta(minutes=30)
        }
    ]
    
    for conversation in conversations:
        await db.ai_assistant_conversations.replace_one(
            {"_id": conversation["_id"]}, 
            conversation, 
            upsert=True
        )
    
    print(f"✅ Created {len(conversations)} AI assistant conversations")
    return conversations

async def main():
    """Main function to populate all Phase 3 data"""
    print("🚀 Starting Phase 3 data population...")
    
    try:
        # Connect to database
        from app.database import connect_to_mongo
        await connect_to_mongo()
        
        # Populate all data
        await populate_subscription_plans()
        await populate_restaurant_subscriptions()
        await populate_billing_invoices()
        await populate_campaign_credits()
        await populate_revenue_analytics()
        await populate_ai_assistant_conversations()
        
        print("\n🎉 Phase 3 sample data population completed successfully!")
        print("\n📊 Summary:")
        print("   • 3 subscription plans (Starter, Professional, Enterprise)")
        print("   • Restaurant subscriptions with usage tracking")
        print("   • Billing invoices and payment history")
        print("   • Campaign credits and transaction history")
        print("   • Revenue analytics with predictions")
        print("   • AI assistant conversation history")
        
        print("\n🔗 Available API endpoints:")
        print("   • Billing: http://localhost:8000/api/billing")
        print("   • Revenue Analytics: http://localhost:8000/api/revenue")
        print("   • AI Assistant: http://localhost:8000/api/ai-assistant")
        print("   • Business Intelligence: http://localhost:8000/api/business-intelligence")
        
    except Exception as e:
        print(f"❌ Error populating Phase 3 data: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())