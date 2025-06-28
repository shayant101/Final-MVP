"""
Mock Twilio API service for sending SMS campaigns
"""
import asyncio
import random
import time
import re
from datetime import datetime
from typing import Dict, Any, List

async def send_sms_campaign(customers: List[Dict], sms_message: str, offer_code: str) -> Dict[str, Any]:
    """Send SMS campaign to customers (mock implementation)"""
    # Simulate API delay
    await asyncio.sleep(1.8)
    
    results = {
        "success": True,
        "campaign": {
            "id": f"sms_{int(time.time())}_{random.randint(100000000, 999999999)}",
            "offer_code": offer_code,
            "message": sms_message,
            "created_at": datetime.now().isoformat()
        },
        "delivery": {
            "total_customers": len(customers),
            "sent": 0,
            "failed": 0,
            "pending": 0
        },
        "details": [],
        "costs": {
            "per_message": 0.0075,  # $0.0075 per SMS
            "total_cost": 0.0
        }
    }
    
    # Simulate sending to each customer
    for customer in customers:
        delivery_status = simulate_delivery()
        
        message_result = {
            "customer_name": customer.get("customer_name"),
            "phone_number": customer.get("phone_number"),
            "status": delivery_status["status"],
            "message_id": f"msg_{int(time.time())}_{random.randint(100000, 999999)}",
            "sent_at": datetime.now().isoformat(),
            "error_code": delivery_status.get("error_code"),
            "error_message": delivery_status.get("error_message")
        }
        
        results["details"].append(message_result)
        
        # Update counters
        if delivery_status["status"] == "sent":
            results["delivery"]["sent"] += 1
        elif delivery_status["status"] == "failed":
            results["delivery"]["failed"] += 1
        else:
            results["delivery"]["pending"] += 1
    
    # Calculate total cost
    results["costs"]["total_cost"] = round(
        results["delivery"]["sent"] * results["costs"]["per_message"], 4
    )
    
    return results

def simulate_delivery() -> Dict[str, Any]:
    """Simulate SMS delivery with realistic success/failure rates"""
    random_val = random.random()
    
    # 85% success rate
    if random_val < 0.85:
        return {"status": "sent"}
    # 10% pending
    elif random_val < 0.95:
        return {"status": "pending"}
    # 5% failed
    else:
        error_codes = [
            {"code": 21211, "message": "Invalid phone number"},
            {"code": 21610, "message": "Message blocked by carrier"},
            {"code": 21614, "message": "Message body is required"}
        ]
        error = random.choice(error_codes)
        return {
            "status": "failed",
            "error_code": error["code"],
            "error_message": error["message"]
        }

def validate_phone_number(phone_number: str) -> bool:
    """Basic phone number validation"""
    phone_regex = r'^\+?[\d\s\-\(\)]{10,}$'
    return bool(re.match(phone_regex, phone_number))

def format_phone_number(phone_number: str) -> str:
    """Format phone number for SMS sending"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone_number)
    
    # Add +1 if it's a 10-digit US number
    if len(digits) == 10:
        return f"+1{digits}"
    
    # Add + if it doesn't start with it
    if not phone_number.startswith('+'):
        return f"+{digits}"
    
    return phone_number

async def get_sms_delivery_report(campaign_id: str) -> Dict[str, Any]:
    """Get SMS delivery report (mock implementation)"""
    # Simulate API delay
    await asyncio.sleep(0.6)
    
    total_messages = random.randint(20, 120)
    delivered = random.randint(15, int(total_messages * 0.9))
    failed = random.randint(1, 6)
    pending = max(0, total_messages - delivered - failed)
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "report": {
            "total_messages": total_messages,
            "delivered": delivered,
            "failed": failed,
            "pending": pending,
            "delivery_rate": f"{round((delivered / total_messages) * 100, 1)}%",
            "avg_delivery_time": f"{round(random.uniform(1.5, 3.5), 1)} seconds",
            "total_cost": round(random.uniform(0.5, 2.5), 4)
        },
        "generated_at": datetime.now().isoformat()
    }

async def pause_sms_campaign(campaign_id: str) -> Dict[str, Any]:
    """Pause an SMS campaign (mock implementation)"""
    await asyncio.sleep(0.5)
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "status": "PAUSED",
        "message": "SMS campaign paused successfully",
        "paused_at": datetime.now().isoformat()
    }

async def resume_sms_campaign(campaign_id: str) -> Dict[str, Any]:
    """Resume an SMS campaign (mock implementation)"""
    await asyncio.sleep(0.5)
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "status": "ACTIVE",
        "message": "SMS campaign resumed successfully",
        "resumed_at": datetime.now().isoformat()
    }