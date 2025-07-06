"""
Billing Engine Service
Comprehensive billing and subscription management with Stripe integration
"""
import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import stripe
import os
from ..database import get_database
from ..models_phase3 import (
    SubscriptionPlan, RestaurantSubscription, BillingInvoice, CampaignCredits,
    SubscriptionStatus, SubscriptionCreate, SubscriptionUpdate, CreditPurchaseRequest,
    UsageTracking, InvoiceLineItem, InvoiceStatus, CreditType
)

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")

class BillingEngineService:
    def __init__(self):
        self.db = None
        
    async def get_db(self):
        """Get database connection"""
        if self.db is None:
            self.db = get_database()
        return self.db

    async def create_subscription(self, subscription_data: SubscriptionCreate) -> Dict[str, Any]:
        """Create new subscription with Stripe integration"""
        try:
            db = await self.get_db()
            
            # Get subscription plan
            plan = await db.subscription_plans.find_one({"plan_id": subscription_data.plan_id})
            if not plan:
                raise ValueError(f"Subscription plan {subscription_data.plan_id} not found")
            
            # Get restaurant info
            restaurant = await db.restaurants.find_one({"restaurant_id": subscription_data.restaurant_id})
            if not restaurant:
                raise ValueError(f"Restaurant {subscription_data.restaurant_id} not found")
            
            # Create or get Stripe customer
            stripe_customer = await self._get_or_create_stripe_customer(restaurant)
            
            # Create Stripe subscription
            stripe_subscription = await self._create_stripe_subscription(
                stripe_customer["id"],
                plan["stripe_price_id_monthly"],
                subscription_data.payment_method_id,
                subscription_data.trial_days
            )
            
            # Create subscription record
            subscription_id = str(uuid.uuid4())
            now = datetime.utcnow()
            trial_end = now + timedelta(days=subscription_data.trial_days) if subscription_data.trial_days > 0 else None
            
            subscription_doc = {
                "subscription_id": subscription_id,
                "restaurant_id": subscription_data.restaurant_id,
                "plan_id": subscription_data.plan_id,
                "status": SubscriptionStatus.trialing if trial_end else SubscriptionStatus.active,
                "current_period_start": now,
                "current_period_end": now + timedelta(days=30),
                "stripe_subscription_id": stripe_subscription["id"],
                "stripe_customer_id": stripe_customer["id"],
                "trial_end": trial_end,
                "cancel_at_period_end": False,
                "usage_tracking": {
                    "ai_requests_used": 0,
                    "campaign_credits_used": 0,
                    "last_reset_date": now,
                    "overage_charges": 0.0
                },
                "created_at": now,
                "updated_at": now
            }
            
            await db.restaurant_subscriptions.insert_one(subscription_doc)
            
            # Initialize campaign credits based on plan
            await self._initialize_plan_credits(subscription_data.restaurant_id, plan)
            
            logger.info(f"Created subscription {subscription_id} for restaurant {subscription_data.restaurant_id}")
            
            return {
                "success": True,
                "subscription_id": subscription_id,
                "stripe_subscription_id": stripe_subscription["id"],
                "status": subscription_doc["status"],
                "trial_end": trial_end.isoformat() if trial_end else None,
                "current_period_end": subscription_doc["current_period_end"].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {str(e)}")
            raise

    async def upgrade_subscription(self, restaurant_id: str, new_plan_id: str) -> Dict[str, Any]:
        """Upgrade/downgrade subscription with prorated billing"""
        try:
            db = await self.get_db()
            
            # Get current subscription
            current_sub = await db.restaurant_subscriptions.find_one({"restaurant_id": restaurant_id})
            if not current_sub:
                raise ValueError(f"No active subscription found for restaurant {restaurant_id}")
            
            # Get new plan
            new_plan = await db.subscription_plans.find_one({"plan_id": new_plan_id})
            if not new_plan:
                raise ValueError(f"Plan {new_plan_id} not found")
            
            # Update Stripe subscription
            stripe_subscription = stripe.Subscription.modify(
                current_sub["stripe_subscription_id"],
                items=[{
                    'id': current_sub["stripe_subscription_id"],
                    'price': new_plan["stripe_price_id_monthly"],
                }],
                proration_behavior='create_prorations'
            )
            
            # Update subscription record
            await db.restaurant_subscriptions.update_one(
                {"restaurant_id": restaurant_id},
                {
                    "$set": {
                        "plan_id": new_plan_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Update campaign credits based on new plan
            await self._update_plan_credits(restaurant_id, new_plan)
            
            logger.info(f"Upgraded subscription for restaurant {restaurant_id} to plan {new_plan_id}")
            
            return {
                "success": True,
                "new_plan_id": new_plan_id,
                "stripe_subscription_id": stripe_subscription["id"]
            }
            
        except Exception as e:
            logger.error(f"Failed to upgrade subscription: {str(e)}")
            raise

    async def cancel_subscription(self, restaurant_id: str, cancel_immediately: bool = False) -> Dict[str, Any]:
        """Cancel subscription with optional immediate termination"""
        try:
            db = await self.get_db()
            
            # Get current subscription
            subscription = await db.restaurant_subscriptions.find_one({"restaurant_id": restaurant_id})
            if not subscription:
                raise ValueError(f"No active subscription found for restaurant {restaurant_id}")
            
            # Cancel Stripe subscription
            if cancel_immediately:
                stripe.Subscription.delete(subscription["stripe_subscription_id"])
                new_status = SubscriptionStatus.canceled
            else:
                stripe.Subscription.modify(
                    subscription["stripe_subscription_id"],
                    cancel_at_period_end=True
                )
                new_status = subscription["status"]  # Keep current status until period end
            
            # Update subscription record
            await db.restaurant_subscriptions.update_one(
                {"restaurant_id": restaurant_id},
                {
                    "$set": {
                        "status": new_status,
                        "cancel_at_period_end": not cancel_immediately,
                        "canceled_at": datetime.utcnow() if cancel_immediately else None,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Canceled subscription for restaurant {restaurant_id}, immediate: {cancel_immediately}")
            
            return {
                "success": True,
                "canceled_immediately": cancel_immediately,
                "status": new_status
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            raise

    async def purchase_campaign_credits(self, credit_request: CreditPurchaseRequest) -> Dict[str, Any]:
        """Purchase additional campaign credits"""
        try:
            db = await self.get_db()
            
            # Calculate cost
            credit_pricing = {
                CreditType.facebook_ads: 2.50,  # $2.50 per credit
                CreditType.sms_campaigns: 0.10,  # $0.10 per credit
                CreditType.content_generation: 0.50,  # $0.50 per credit
                CreditType.image_enhancement: 1.00  # $1.00 per credit
            }
            
            cost_per_credit = credit_pricing.get(credit_request.credit_type, 1.00)
            total_cost = cost_per_credit * credit_request.quantity
            
            # Create Stripe payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(total_cost * 100),  # Convert to cents
                currency='usd',
                payment_method=credit_request.payment_method_id,
                confirmation_method='manual',
                confirm=True,
                metadata={
                    'restaurant_id': credit_request.restaurant_id,
                    'credit_type': credit_request.credit_type,
                    'quantity': credit_request.quantity
                }
            )
            
            if payment_intent.status == 'succeeded':
                # Create credit record
                credit_id = str(uuid.uuid4())
                now = datetime.utcnow()
                expiry_date = now + timedelta(days=365)  # Credits expire in 1 year
                
                credit_doc = {
                    "credit_id": credit_id,
                    "restaurant_id": credit_request.restaurant_id,
                    "credit_type": credit_request.credit_type,
                    "credits_purchased": credit_request.quantity,
                    "credits_used": 0,
                    "credits_remaining": credit_request.quantity,
                    "purchase_date": now,
                    "expiry_date": expiry_date,
                    "cost_per_credit": cost_per_credit,
                    "total_cost": total_cost,
                    "stripe_payment_intent_id": payment_intent.id,
                    "created_at": now
                }
                
                await db.campaign_credits.insert_one(credit_doc)
                
                logger.info(f"Purchased {credit_request.quantity} {credit_request.credit_type} credits for restaurant {credit_request.restaurant_id}")
                
                return {
                    "success": True,
                    "credit_id": credit_id,
                    "credits_purchased": credit_request.quantity,
                    "total_cost": total_cost,
                    "expiry_date": expiry_date.isoformat()
                }
            else:
                raise ValueError(f"Payment failed: {payment_intent.status}")
                
        except Exception as e:
            logger.error(f"Failed to purchase credits: {str(e)}")
            raise

    async def track_feature_usage(self, restaurant_id: str, feature_type: str, usage_amount: int = 1) -> Dict[str, Any]:
        """Track feature usage against subscription limits"""
        try:
            db = await self.get_db()
            
            # Get current subscription
            subscription = await db.restaurant_subscriptions.find_one({"restaurant_id": restaurant_id})
            if not subscription:
                return {"allowed": False, "reason": "No active subscription"}
            
            # Get subscription plan
            plan = await db.subscription_plans.find_one({"plan_id": subscription["plan_id"]})
            if not plan:
                return {"allowed": False, "reason": "Invalid subscription plan"}
            
            # Check usage limits
            usage_tracking = subscription["usage_tracking"]
            current_usage = usage_tracking.get("ai_requests_used", 0)
            monthly_limit = plan["features"]["ai_requests_per_month"]
            
            # Check if usage would exceed limit
            if current_usage + usage_amount > monthly_limit:
                # Calculate overage cost
                overage_amount = (current_usage + usage_amount) - monthly_limit
                overage_cost = overage_amount * 0.10  # $0.10 per overage request
                
                # Update overage charges
                await db.restaurant_subscriptions.update_one(
                    {"restaurant_id": restaurant_id},
                    {
                        "$inc": {
                            "usage_tracking.ai_requests_used": usage_amount,
                            "usage_tracking.overage_charges": overage_cost
                        },
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
                
                return {
                    "allowed": True,
                    "overage": True,
                    "overage_cost": overage_cost,
                    "new_usage": current_usage + usage_amount
                }
            else:
                # Update usage within limits
                await db.restaurant_subscriptions.update_one(
                    {"restaurant_id": restaurant_id},
                    {
                        "$inc": {"usage_tracking.ai_requests_used": usage_amount},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
                
                return {
                    "allowed": True,
                    "overage": False,
                    "remaining": monthly_limit - (current_usage + usage_amount),
                    "new_usage": current_usage + usage_amount
                }
                
        except Exception as e:
            logger.error(f"Failed to track usage: {str(e)}")
            return {"allowed": False, "reason": f"Error tracking usage: {str(e)}"}

    async def use_campaign_credits(self, restaurant_id: str, credit_type: CreditType, amount: int = 1) -> Dict[str, Any]:
        """Use campaign credits for campaigns"""
        try:
            db = await self.get_db()
            
            # Find available credits (oldest first)
            credits_cursor = db.campaign_credits.find({
                "restaurant_id": restaurant_id,
                "credit_type": credit_type,
                "credits_remaining": {"$gt": 0},
                "expiry_date": {"$gt": datetime.utcnow()}
            }).sort("purchase_date", 1)
            
            credits = await credits_cursor.to_list(length=None)
            
            total_available = sum(credit["credits_remaining"] for credit in credits)
            
            if total_available < amount:
                return {
                    "success": False,
                    "reason": f"Insufficient credits. Available: {total_available}, Required: {amount}"
                }
            
            # Use credits from oldest purchases first
            remaining_to_use = amount
            used_credits = []
            
            for credit in credits:
                if remaining_to_use <= 0:
                    break
                    
                available_in_this_credit = credit["credits_remaining"]
                to_use_from_this = min(remaining_to_use, available_in_this_credit)
                
                # Update credit record
                await db.campaign_credits.update_one(
                    {"credit_id": credit["credit_id"]},
                    {
                        "$inc": {
                            "credits_used": to_use_from_this,
                            "credits_remaining": -to_use_from_this
                        }
                    }
                )
                
                used_credits.append({
                    "credit_id": credit["credit_id"],
                    "used": to_use_from_this
                })
                
                remaining_to_use -= to_use_from_this
            
            logger.info(f"Used {amount} {credit_type} credits for restaurant {restaurant_id}")
            
            return {
                "success": True,
                "credits_used": amount,
                "used_from": used_credits,
                "remaining_total": total_available - amount
            }
            
        except Exception as e:
            logger.error(f"Failed to use credits: {str(e)}")
            return {"success": False, "reason": f"Error using credits: {str(e)}"}

    async def generate_invoice(self, restaurant_id: str, billing_period: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Generate detailed invoice with usage breakdown"""
        try:
            db = await self.get_db()
            start_date, end_date = billing_period
            
            # Get subscription and plan
            subscription = await db.restaurant_subscriptions.find_one({"restaurant_id": restaurant_id})
            if not subscription:
                raise ValueError(f"No subscription found for restaurant {restaurant_id}")
            
            plan = await db.subscription_plans.find_one({"plan_id": subscription["plan_id"]})
            if not plan:
                raise ValueError(f"Plan {subscription['plan_id']} not found")
            
            # Calculate line items
            line_items = []
            total_amount = 0.0
            
            # Subscription fee
            line_items.append({
                "description": f"{plan['name']} Plan - Monthly Subscription",
                "amount": plan["price_monthly"],
                "quantity": 1,
                "unit_price": plan["price_monthly"]
            })
            total_amount += plan["price_monthly"]
            
            # Overage charges
            overage_charges = subscription["usage_tracking"].get("overage_charges", 0.0)
            if overage_charges > 0:
                line_items.append({
                    "description": "AI Request Overage Charges",
                    "amount": overage_charges,
                    "quantity": 1,
                    "unit_price": overage_charges
                })
                total_amount += overage_charges
            
            # Campaign credit purchases
            credit_purchases = await db.campaign_credits.find({
                "restaurant_id": restaurant_id,
                "purchase_date": {"$gte": start_date, "$lte": end_date}
            }).to_list(length=None)
            
            for purchase in credit_purchases:
                line_items.append({
                    "description": f"{purchase['credit_type'].replace('_', ' ').title()} Credits ({purchase['credits_purchased']} credits)",
                    "amount": purchase["total_cost"],
                    "quantity": purchase["credits_purchased"],
                    "unit_price": purchase["cost_per_credit"]
                })
                total_amount += purchase["total_cost"]
            
            # Create invoice
            invoice_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            invoice_doc = {
                "invoice_id": invoice_id,
                "restaurant_id": restaurant_id,
                "subscription_id": subscription["subscription_id"],
                "amount": total_amount,
                "currency": "usd",
                "status": InvoiceStatus.pending,
                "invoice_date": now,
                "due_date": now + timedelta(days=30),
                "line_items": line_items,
                "tax_amount": 0.0,
                "discount_amount": 0.0,
                "created_at": now,
                "updated_at": now
            }
            
            await db.billing_invoices.insert_one(invoice_doc)
            
            logger.info(f"Generated invoice {invoice_id} for restaurant {restaurant_id}")
            
            return {
                "success": True,
                "invoice_id": invoice_id,
                "amount": total_amount,
                "line_items": line_items,
                "due_date": invoice_doc["due_date"].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate invoice: {str(e)}")
            raise

    async def handle_failed_payment(self, restaurant_id: str, invoice_id: str) -> Dict[str, Any]:
        """Handle failed payment scenarios with grace periods"""
        try:
            db = await self.get_db()
            
            # Update invoice status
            await db.billing_invoices.update_one(
                {"invoice_id": invoice_id},
                {
                    "$set": {
                        "status": InvoiceStatus.failed,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Update subscription status to past_due
            await db.restaurant_subscriptions.update_one(
                {"restaurant_id": restaurant_id},
                {
                    "$set": {
                        "status": SubscriptionStatus.past_due,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # TODO: Send notification to restaurant
            # TODO: Schedule retry attempts
            
            logger.warning(f"Payment failed for restaurant {restaurant_id}, invoice {invoice_id}")
            
            return {
                "success": True,
                "action": "marked_past_due",
                "grace_period_days": 7
            }
            
        except Exception as e:
            logger.error(f"Failed to handle payment failure: {str(e)}")
            raise

    # Helper methods
    async def _get_or_create_stripe_customer(self, restaurant: Dict[str, Any]) -> Dict[str, Any]:
        """Get or create Stripe customer for restaurant"""
        try:
            # Check if customer already exists
            customers = stripe.Customer.list(email=restaurant["email"], limit=1)
            
            if customers.data:
                return customers.data[0]
            
            # Create new customer
            customer = stripe.Customer.create(
                email=restaurant["email"],
                name=restaurant["name"],
                metadata={
                    'restaurant_id': restaurant["restaurant_id"]
                }
            )
            
            return customer
            
        except Exception as e:
            logger.error(f"Failed to get/create Stripe customer: {str(e)}")
            raise

    async def _create_stripe_subscription(self, customer_id: str, price_id: str, 
                                        payment_method_id: Optional[str], trial_days: int) -> Dict[str, Any]:
        """Create Stripe subscription"""
        try:
            subscription_params = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'expand': ['latest_invoice.payment_intent'],
            }
            
            if payment_method_id:
                subscription_params['default_payment_method'] = payment_method_id
            
            if trial_days > 0:
                subscription_params['trial_period_days'] = trial_days
            
            subscription = stripe.Subscription.create(**subscription_params)
            
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to create Stripe subscription: {str(e)}")
            raise

    async def _initialize_plan_credits(self, restaurant_id: str, plan: Dict[str, Any]):
        """Initialize campaign credits based on subscription plan"""
        try:
            db = await self.get_db()
            
            campaign_credits = plan["features"].get("campaign_credits", 0)
            if campaign_credits > 0:
                credit_id = str(uuid.uuid4())
                now = datetime.utcnow()
                
                credit_doc = {
                    "credit_id": credit_id,
                    "restaurant_id": restaurant_id,
                    "credit_type": CreditType.content_generation,  # Default type
                    "credits_purchased": campaign_credits,
                    "credits_used": 0,
                    "credits_remaining": campaign_credits,
                    "purchase_date": now,
                    "expiry_date": now + timedelta(days=365),
                    "cost_per_credit": 0.0,  # Included in plan
                    "total_cost": 0.0,
                    "created_at": now
                }
                
                await db.campaign_credits.insert_one(credit_doc)
                
        except Exception as e:
            logger.error(f"Failed to initialize plan credits: {str(e)}")

    async def _update_plan_credits(self, restaurant_id: str, new_plan: Dict[str, Any]):
        """Update campaign credits when plan changes"""
        try:
            # This would implement logic to adjust credits based on plan change
            # For now, we'll just log the change
            logger.info(f"Plan credits updated for restaurant {restaurant_id}")
            
        except Exception as e:
            logger.error(f"Failed to update plan credits: {str(e)}")

# Create service instance
billing_engine_service = BillingEngineService()