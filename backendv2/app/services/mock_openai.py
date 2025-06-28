"""
Mock OpenAI API service for generating ad copy and SMS messages
"""
import asyncio
import random
from datetime import datetime
from typing import Dict, Any

async def generate_ad_copy(restaurant_name: str, item_to_promote: str, offer: str) -> Dict[str, Any]:
    """Generate Facebook ad copy (mock implementation)"""
    # Simulate API delay
    await asyncio.sleep(1.5)
    
    emojis = ['🍕', '🍔', '🌮', '🍜', '🥗', '🍰', '☕', '🥘']
    random_emoji = random.choice(emojis)
    
    ad_templates = [
        {
            "headline": f"{random_emoji} Craving something special? {restaurant_name} has you covered!",
            "body": f"Get our famous {item_to_promote} with this amazing deal: {offer}\nFresh ingredients, authentic flavors, unbeatable value!\nDon't miss out - limited time only!",
            "cta": "📍 Visit us or order online today!"
        },
        {
            "headline": f"{random_emoji} {restaurant_name} Alert: {item_to_promote} Special!",
            "body": f"{offer} - because you deserve the best!\nMade fresh daily with premium ingredients.\nYour taste buds will thank you!",
            "cta": "🚗 Dine in, takeout, or delivery available!"
        },
        {
            "headline": f"{random_emoji} Local Favorite Alert! {restaurant_name}",
            "body": f"Our signature {item_to_promote} is calling your name!\n{offer}\nTaste the difference quality makes!",
            "cta": "📞 Order now or visit us today!"
        }
    ]
    
    selected_template = random.choice(ad_templates)
    full_ad_copy = f"{selected_template['headline']}\n\n{selected_template['body']}\n\n{selected_template['cta']}"
    
    return {
        "success": True,
        "ad_copy": full_ad_copy,
        "metadata": {
            "character_count": len(full_ad_copy),
            "generated_at": datetime.now().isoformat(),
            "model": "gpt-4-turbo"
        }
    }

async def generate_sms_message(restaurant_name: str, customer_name: str, offer: str, offer_code: str) -> Dict[str, Any]:
    """Generate SMS message (mock implementation)"""
    # Simulate API delay
    await asyncio.sleep(1.2)
    
    sms_templates = [
        f"Hi {customer_name}! We miss you at {restaurant_name}! {offer} Use code {offer_code}. Valid thru Sunday!",
        f"{customer_name}, come back to {restaurant_name}! {offer} Code: {offer_code}. Limited time!",
        f"Hey {customer_name}! {restaurant_name} misses you. {offer} Use {offer_code} - expires soon!",
        f"{customer_name}, special offer from {restaurant_name}: {offer} Code {offer_code}. Don't wait!"
    ]
    
    selected_message = random.choice(sms_templates)
    
    # Ensure message is under 160 characters
    final_message = selected_message[:157] + "..." if len(selected_message) > 160 else selected_message
    
    return {
        "success": True,
        "sms_message": final_message,
        "metadata": {
            "character_count": len(final_message),
            "generated_at": datetime.now().isoformat(),
            "model": "gpt-3.5-turbo"
        }
    }

def generate_promo_code(item_to_promote: str) -> str:
    """Generate promo code based on item and day"""
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    today = datetime.now()
    day_code = days[today.weekday()]
    
    # Clean item name and take first 6 characters
    import re
    item_code = re.sub(r'[^a-zA-Z]', '', item_to_promote).upper()[:6]
    
    return f"{item_code}{day_code}"

async def generate_campaign_suggestions(restaurant_name: str, campaign_type: str) -> Dict[str, Any]:
    """Generate campaign suggestions (mock implementation)"""
    await asyncio.sleep(1.0)
    
    if campaign_type == "facebook_ad":
        suggestions = {
            "items_to_promote": [
                "Signature Burger", "Daily Special", "Weekend Brunch", 
                "Happy Hour", "Chef's Special", "Seasonal Menu"
            ],
            "offer_ideas": [
                "20% off your next visit", "Buy one get one 50% off",
                "Free appetizer with entree", "$5 off orders over $25",
                "Complimentary dessert", "Happy hour pricing all day"
            ],
            "budget_recommendations": {
                "small_business": {"min": 10, "max": 25, "recommended": 15},
                "medium_business": {"min": 25, "max": 75, "recommended": 50},
                "large_business": {"min": 75, "max": 200, "recommended": 100}
            }
        }
    else:  # SMS campaign
        suggestions = {
            "offer_ideas": [
                "Come back for 15% off", "We miss you! 20% off next visit",
                "Special customer discount: $10 off", "Free appetizer on us",
                "Buy one entree, get dessert free", "Happy hour prices for you"
            ],
            "timing_recommendations": [
                "Tuesday-Thursday for best response rates",
                "Send between 11 AM - 2 PM or 5 PM - 7 PM",
                "Avoid Monday mornings and Friday evenings"
            ],
            "message_tips": [
                "Keep messages under 160 characters",
                "Include clear expiration date",
                "Use customer's name for personalization",
                "Include clear call-to-action"
            ]
        }
    
    return {
        "success": True,
        "suggestions": suggestions,
        "generated_at": datetime.now().isoformat()
    }