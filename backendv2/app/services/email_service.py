import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class EmailConfig:
    """Email configuration settings"""
    api_key: str
    from_email: str
    domain: str
    verification_expire_hours: int = 24
    admin_email: Optional[str] = None
    rate_limit_per_minute: int = 10
    max_retries: int = 3
    retry_delay: float = 1.0

class EmailTemplateError(Exception):
    """Raised when email template operations fail"""
    pass

class EmailSendError(Exception):
    """Raised when email sending fails"""
    pass

class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass

class ResendEmailService:
    """
    Resend email service for handling authentication emails and notifications.
    
    Features:
    - Email verification
    - Welcome emails
    - Admin notifications
    - Template system with Jinja2
    - Rate limiting protection
    - Retry logic with exponential backoff
    - Comprehensive error handling
    """
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.base_url = "https://api.resend.com"
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        # Rate limiting tracking
        self._rate_limit_tracker = {}
        
        # Setup Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        if template_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                autoescape=select_autoescape(['html', 'xml'])
            )
        else:
            logger.warning(f"Email templates directory not found: {template_dir}")
            self.jinja_env = None
    
    async def _check_rate_limit(self) -> None:
        """Check if we're within rate limits"""
        current_time = datetime.utcnow()
        minute_key = current_time.strftime("%Y-%m-%d-%H-%M")
        
        if minute_key not in self._rate_limit_tracker:
            self._rate_limit_tracker[minute_key] = 0
        
        # Clean old entries (keep only current and previous minute)
        keys_to_remove = [
            key for key in self._rate_limit_tracker.keys()
            if key != minute_key and key != (current_time - timedelta(minutes=1)).strftime("%Y-%m-%d-%H-%M")
        ]
        for key in keys_to_remove:
            del self._rate_limit_tracker[key]
        
        if self._rate_limit_tracker[minute_key] >= self.config.rate_limit_per_minute:
            raise RateLimitError(f"Rate limit exceeded: {self.config.rate_limit_per_minute} emails per minute")
        
        self._rate_limit_tracker[minute_key] += 1
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context"""
        if not self.jinja_env:
            raise EmailTemplateError("Template environment not initialized")
        
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering failed for {template_name}: {str(e)}")
            raise EmailTemplateError(f"Failed to render template {template_name}: {str(e)}")
    
    def _get_fallback_template(self, email_type: str, context: Dict[str, Any]) -> str:
        """Generate fallback HTML template when template files are not available"""
        if email_type == "verification":
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Verify Your Email</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
                    .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to {context.get('restaurant_name', 'Our Platform')}!</h1>
                    </div>
                    <div class="content">
                        <h2>Please verify your email address</h2>
                        <p>Hi {context.get('user_email', 'there')},</p>
                        <p>Thank you for registering with us. Please click the button below to verify your email address:</p>
                        <p style="text-align: center;">
                            <a href="{context.get('verification_url', '#')}" class="button">Verify Email</a>
                        </p>
                        <p>Or copy and paste this link into your browser:</p>
                        <p style="word-break: break-all;">{context.get('verification_url', '#')}</p>
                        <p>This verification link will expire in {context.get('expire_hours', 24)} hours.</p>
                    </div>
                    <div class="footer">
                        <p>If you didn't create an account, please ignore this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        elif email_type == "welcome":
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome!</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #28a745; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 4px; }}
                    .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to Our Platform!</h1>
                    </div>
                    <div class="content">
                        <h2>Your account is ready!</h2>
                        <p>Hi {context.get('user_email', 'there')},</p>
                        <p>Welcome to our restaurant marketing platform! Your account for <strong>{context.get('restaurant_name', 'your restaurant')}</strong> has been successfully created and verified.</p>
                        <p>You can now access all our features to grow your restaurant business:</p>
                        <ul>
                            <li>Create marketing campaigns</li>
                            <li>Manage customer relationships</li>
                            <li>Track performance analytics</li>
                            <li>And much more!</li>
                        </ul>
                        <p style="text-align: center;">
                            <a href="{context.get('dashboard_url', '#')}" class="button">Go to Dashboard</a>
                        </p>
                    </div>
                    <div class="footer">
                        <p>Need help? Contact our support team anytime.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        elif email_type == "admin_notification":
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>New User Registration</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #6c757d; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .info-box {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }}
                    .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>New User Registration</h1>
                    </div>
                    <div class="content">
                        <h2>A new restaurant has joined the platform</h2>
                        <div class="info-box">
                            <strong>Restaurant:</strong> {context.get('restaurant_name', 'N/A')}<br>
                            <strong>Email:</strong> {context.get('user_email', 'N/A')}<br>
                            <strong>Phone:</strong> {context.get('phone', 'N/A')}<br>
                            <strong>Address:</strong> {context.get('address', 'N/A')}<br>
                            <strong>Registration Time:</strong> {context.get('registration_time', 'N/A')}
                        </div>
                        <p>Please review the new registration and provide any necessary onboarding support.</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated notification from the restaurant platform.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            raise EmailTemplateError(f"Unknown email type: {email_type}")
    
    async def _send_email_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send email request to Resend API with retry logic"""
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                await self._check_rate_limit()
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.base_url}/emails",
                        headers=self.headers,
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Email sent successfully: {result.get('id', 'unknown')}")
                        return result
                    elif response.status_code == 429:
                        # Rate limited by Resend
                        logger.warning(f"Rate limited by Resend API, attempt {attempt + 1}")
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                            continue
                        raise EmailSendError("Rate limited by Resend API")
                    else:
                        error_detail = response.text
                        logger.error(f"Email send failed with status {response.status_code}: {error_detail}")
                        raise EmailSendError(f"API request failed: {response.status_code} - {error_detail}")
                        
            except httpx.TimeoutException as e:
                last_exception = e
                logger.warning(f"Email send timeout, attempt {attempt + 1}: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
            except httpx.RequestError as e:
                last_exception = e
                logger.warning(f"Email send request error, attempt {attempt + 1}: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
            except RateLimitError:
                # Don't retry rate limit errors
                raise
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error sending email, attempt {attempt + 1}: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
        
        raise EmailSendError(f"Failed to send email after {self.config.max_retries} attempts: {str(last_exception)}")
    
    async def send_verification_email(
        self,
        to_email: str,
        user_name: str,
        restaurant_name: str,
        verification_token: str,
        base_url: str = "http://localhost:3000"
    ) -> Dict[str, Any]:
        """
        Send email verification email
        
        Args:
            to_email: Recipient email address
            user_name: User's name or email
            restaurant_name: Restaurant name
            verification_token: Email verification token
            base_url: Base URL for verification link
            
        Returns:
            Dict containing email send result
        """
        verification_url = f"{base_url}/verify-email?token={verification_token}"
        
        context = {
            "user_email": to_email,
            "user_name": user_name,
            "restaurant_name": restaurant_name,
            "verification_url": verification_url,
            "verification_token": verification_token,
            "expire_hours": self.config.verification_expire_hours
        }
        
        try:
            # Try to use template file first
            if self.jinja_env:
                html_content = self._render_template("verification.html", context)
            else:
                html_content = self._get_fallback_template("verification", context)
        except EmailTemplateError:
            # Fall back to built-in template
            html_content = self._get_fallback_template("verification", context)
        
        payload = {
            "from": self.config.from_email,
            "to": [to_email],
            "subject": f"Verify your email for {restaurant_name}",
            "html": html_content
        }
        
        try:
            result = await self._send_email_request(payload)
            logger.info(f"Verification email sent to {to_email} for restaurant {restaurant_name}")
            return {
                "success": True,
                "message": "Verification email sent successfully",
                "email_id": result.get("id"),
                "to": to_email
            }
        except Exception as e:
            logger.error(f"Failed to send verification email to {to_email}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send verification email: {str(e)}",
                "to": to_email
            }
    
    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
        restaurant_name: str,
        dashboard_url: str = "http://localhost:3000/dashboard"
    ) -> Dict[str, Any]:
        """
        Send welcome email after successful verification
        
        Args:
            to_email: Recipient email address
            user_name: User's name or email
            restaurant_name: Restaurant name
            dashboard_url: URL to the dashboard
            
        Returns:
            Dict containing email send result
        """
        context = {
            "user_email": to_email,
            "user_name": user_name,
            "restaurant_name": restaurant_name,
            "dashboard_url": dashboard_url
        }
        
        try:
            # Try to use template file first
            if self.jinja_env:
                html_content = self._render_template("welcome.html", context)
            else:
                html_content = self._get_fallback_template("welcome", context)
        except EmailTemplateError:
            # Fall back to built-in template
            html_content = self._get_fallback_template("welcome", context)
        
        payload = {
            "from": self.config.from_email,
            "to": [to_email],
            "subject": f"Welcome to our platform, {restaurant_name}!",
            "html": html_content
        }
        
        try:
            result = await self._send_email_request(payload)
            logger.info(f"Welcome email sent to {to_email} for restaurant {restaurant_name}")
            return {
                "success": True,
                "message": "Welcome email sent successfully",
                "email_id": result.get("id"),
                "to": to_email
            }
        except Exception as e:
            logger.error(f"Failed to send welcome email to {to_email}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send welcome email: {str(e)}",
                "to": to_email
            }
    
    async def send_admin_notification(
        self,
        user_email: str,
        restaurant_name: str,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        registration_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Send admin notification for new user registration
        
        Args:
            user_email: New user's email
            restaurant_name: Restaurant name
            phone: Restaurant phone number
            address: Restaurant address
            registration_time: When the user registered
            
        Returns:
            Dict containing email send result
        """
        if not self.config.admin_email:
            logger.warning("Admin email not configured, skipping admin notification")
            return {
                "success": False,
                "message": "Admin email not configured",
                "to": None
            }
        
        context = {
            "user_email": user_email,
            "restaurant_name": restaurant_name,
            "phone": phone or "Not provided",
            "address": address or "Not provided",
            "registration_time": registration_time.strftime("%Y-%m-%d %H:%M:%S UTC") if registration_time else "Unknown"
        }
        
        try:
            # Try to use template file first
            if self.jinja_env:
                html_content = self._render_template("admin_notification.html", context)
            else:
                html_content = self._get_fallback_template("admin_notification", context)
        except EmailTemplateError:
            # Fall back to built-in template
            html_content = self._get_fallback_template("admin_notification", context)
        
        payload = {
            "from": self.config.from_email,
            "to": [self.config.admin_email],
            "subject": f"New Registration: {restaurant_name}",
            "html": html_content
        }
        
        try:
            result = await self._send_email_request(payload)
            logger.info(f"Admin notification sent for new registration: {restaurant_name}")
            return {
                "success": True,
                "message": "Admin notification sent successfully",
                "email_id": result.get("id"),
                "to": self.config.admin_email
            }
        except Exception as e:
            logger.error(f"Failed to send admin notification for {restaurant_name}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send admin notification: {str(e)}",
                "to": self.config.admin_email
            }
    
    async def send_custom_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send custom email with provided content
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            from_email: Optional custom from email (defaults to config from_email)
            
        Returns:
            Dict containing email send result
        """
        payload = {
            "from": from_email or self.config.from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        
        try:
            result = await self._send_email_request(payload)
            logger.info(f"Custom email sent to {to_email} with subject: {subject}")
            return {
                "success": True,
                "message": "Custom email sent successfully",
                "email_id": result.get("id"),
                "to": to_email
            }
        except Exception as e:
            logger.error(f"Failed to send custom email to {to_email}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send custom email: {str(e)}",
                "to": to_email
            }

# Global email service instance
_email_service: Optional[ResendEmailService] = None

def get_email_service() -> ResendEmailService:
    """Get the global email service instance"""
    global _email_service
    if _email_service is None:
        # Load configuration from environment
        config = EmailConfig(
            api_key=os.getenv("RESEND_API_KEY", ""),
            from_email=os.getenv("RESEND_FROM_EMAIL", "noreply@example.com"),
            domain=os.getenv("RESEND_DOMAIN", "example.com"),
            verification_expire_hours=int(os.getenv("EMAIL_VERIFICATION_EXPIRE_HOURS", "24")),
            admin_email=os.getenv("ADMIN_EMAIL"),
            rate_limit_per_minute=int(os.getenv("EMAIL_RATE_LIMIT_PER_MINUTE", "10")),
            max_retries=int(os.getenv("EMAIL_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("EMAIL_RETRY_DELAY", "1.0"))
        )
        
        if not config.api_key:
            logger.warning("RESEND_API_KEY not configured - email service will not work")
        
        _email_service = ResendEmailService(config)
    
    return _email_service

# Convenience functions for easy usage
async def send_verification_email(to_email: str, user_name: str, restaurant_name: str, verification_token: str, base_url: str = "http://localhost:3000") -> Dict[str, Any]:
    """Convenience function to send verification email"""
    service = get_email_service()
    return await service.send_verification_email(to_email, user_name, restaurant_name, verification_token, base_url)

async def send_welcome_email(to_email: str, user_name: str, restaurant_name: str, dashboard_url: str = "http://localhost:3000/dashboard") -> Dict[str, Any]:
    """Convenience function to send welcome email"""
    service = get_email_service()
    return await service.send_welcome_email(to_email, user_name, restaurant_name, dashboard_url)

async def send_admin_notification(user_email: str, restaurant_name: str, phone: Optional[str] = None, address: Optional[str] = None, registration_time: Optional[datetime] = None) -> Dict[str, Any]:
    """Convenience function to send admin notification"""
    service = get_email_service()
    return await service.send_admin_notification(user_email, restaurant_name, phone, address, registration_time)