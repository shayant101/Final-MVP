"""
Real Twilio SMS service for sending SMS campaigns
"""
import os
import asyncio
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging

# Set up logging
logger = logging.getLogger(__name__)

class TwilioSMSService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            logger.warning("Twilio credentials not fully configured. SMS functionality will be limited.")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
                self.client = None

    def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send a single SMS message"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return {
                "success": False,
                "error": "Twilio client not initialized",
                "message_sid": None,
                "status": "failed",
                "to": to_number,
                "from": self.phone_number
            }
        
        try:
            # Format phone number
            formatted_number = self.format_phone_number(to_number)
            
            # Validate phone number
            if not self.validate_phone_number(formatted_number):
                return {
                    "success": False,
                    "error": "Invalid phone number format",
                    "message_sid": None,
                    "status": "failed",
                    "to": formatted_number,
                    "from": self.phone_number
                }
            
            # Send SMS via Twilio
            message_obj = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=formatted_number
            )
            
            return {
                "success": True,
                "error": None,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "to": formatted_number,
                "from": self.phone_number
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS to {to_number}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_sid": None,
                "status": "failed",
                "to": to_number,
                "from": self.phone_number
            }
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to_number}: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "message_sid": None,
                "status": "failed",
                "to": to_number,
                "from": self.phone_number
            }

    async def send_sms_campaign(self, customers: List[Dict], sms_message: str, offer_code: str) -> Dict[str, Any]:
        """Send SMS campaign to customers using real Twilio API"""
        if not self.client:
            logger.error("Twilio client not initialized. Falling back to mock implementation.")
            return await self._mock_send_sms_campaign(customers, sms_message, offer_code)
        
        results = {
            "success": True,
            "campaign": {
                "id": f"sms_{int(datetime.now().timestamp())}",
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
                "per_message": 0.0075,  # $0.0075 per SMS (Twilio pricing)
                "total_cost": 0.0
            }
        }
        
        # Send SMS to each customer
        for customer in customers:
            phone_number = self.format_phone_number(customer.get("phone_number", ""))
            customer_name = customer.get("customer_name", "Customer")
            
            # Validate phone number
            if not self.validate_phone_number(phone_number):
                message_result = {
                    "customer_name": customer_name,
                    "phone_number": phone_number,
                    "status": "failed",
                    "message_id": None,
                    "sent_at": datetime.now().isoformat(),
                    "error_code": "21211",
                    "error_message": "Invalid phone number format"
                }
                results["details"].append(message_result)
                results["delivery"]["failed"] += 1
                continue
            
            # Personalize message
            personalized_message = sms_message.replace("{customer_name}", customer_name)
            
            try:
                # Send SMS via Twilio
                message = self.client.messages.create(
                    body=personalized_message,
                    from_=self.phone_number,
                    to=phone_number
                )
                
                message_result = {
                    "customer_name": customer_name,
                    "phone_number": phone_number,
                    "status": "sent",
                    "message_id": message.sid,
                    "sent_at": datetime.now().isoformat(),
                    "error_code": None,
                    "error_message": None
                }
                results["delivery"]["sent"] += 1
                
            except TwilioException as e:
                logger.error(f"Twilio error sending SMS to {phone_number}: {str(e)}")
                message_result = {
                    "customer_name": customer_name,
                    "phone_number": phone_number,
                    "status": "failed",
                    "message_id": None,
                    "sent_at": datetime.now().isoformat(),
                    "error_code": getattr(e, 'code', 'UNKNOWN'),
                    "error_message": str(e)
                }
                results["delivery"]["failed"] += 1
                
            except Exception as e:
                logger.error(f"Unexpected error sending SMS to {phone_number}: {str(e)}")
                message_result = {
                    "customer_name": customer_name,
                    "phone_number": phone_number,
                    "status": "failed",
                    "message_id": None,
                    "sent_at": datetime.now().isoformat(),
                    "error_code": "UNKNOWN",
                    "error_message": f"Unexpected error: {str(e)}"
                }
                results["delivery"]["failed"] += 1
            
            results["details"].append(message_result)
            
            # Add small delay to avoid rate limiting
            await asyncio.sleep(0.1)
        
        # Calculate total cost
        results["costs"]["total_cost"] = round(
            results["delivery"]["sent"] * results["costs"]["per_message"], 4
        )
        
        return results

    async def get_sms_delivery_report(self, campaign_id: str) -> Dict[str, Any]:
        """Get SMS delivery report from Twilio"""
        if not self.client:
            logger.error("Twilio client not initialized. Falling back to mock implementation.")
            return await self._mock_get_sms_delivery_report(campaign_id)
        
        try:
            # In a real implementation, you would store message SIDs and query them
            # For now, we'll return a basic report structure
            return {
                "success": True,
                "campaign_id": campaign_id,
                "report": {
                    "message": "Delivery report functionality requires message tracking implementation",
                    "note": "This would query individual message statuses from Twilio API"
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting delivery report: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }

    def validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format"""
        if not phone_number:
            return False
        
        # Remove all non-digit characters for validation
        digits = re.sub(r'\D', '', phone_number)
        
        # Must have at least 10 digits (US format) or 11+ for international
        if len(digits) < 10:
            return False
        
        # Basic format validation
        phone_regex = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(phone_regex, phone_number))

    def format_phone_number(self, phone_number: str) -> str:
        """Format phone number for Twilio (E.164 format)"""
        if not phone_number:
            return ""
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone_number)
        
        # Add +1 if it's a 10-digit US number
        if len(digits) == 10:
            return f"+1{digits}"
        
        # Add + if it doesn't start with it and has 11+ digits
        if len(digits) >= 11 and not phone_number.startswith('+'):
            return f"+{digits}"
        
        # Return as-is if already properly formatted
        if phone_number.startswith('+'):
            return phone_number
        
        return f"+{digits}"

    async def _mock_send_sms_campaign(self, customers: List[Dict], sms_message: str, offer_code: str) -> Dict[str, Any]:
        """Fallback mock implementation when Twilio is not configured"""
        from .mock_twilio import send_sms_campaign
        logger.info("Using mock SMS implementation - Twilio not configured")
        return await send_sms_campaign(customers, sms_message, offer_code)

    async def _mock_get_sms_delivery_report(self, campaign_id: str) -> Dict[str, Any]:
        """Fallback mock implementation for delivery reports"""
        from .mock_twilio import get_sms_delivery_report
        logger.info("Using mock delivery report - Twilio not configured")
        return await get_sms_delivery_report(campaign_id)

# Create a singleton instance
twilio_service = TwilioSMSService()

# Export the main functions for backward compatibility
async def send_sms_campaign(customers: List[Dict], sms_message: str, offer_code: str) -> Dict[str, Any]:
    """Send SMS campaign using Twilio service"""
    return await twilio_service.send_sms_campaign(customers, sms_message, offer_code)

async def get_sms_delivery_report(campaign_id: str) -> Dict[str, Any]:
    """Get SMS delivery report using Twilio service"""
    return await twilio_service.get_sms_delivery_report(campaign_id)

def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number format"""
    return twilio_service.validate_phone_number(phone_number)

def format_phone_number(phone_number: str) -> str:
    """Format phone number for SMS sending"""
    return twilio_service.format_phone_number(phone_number)