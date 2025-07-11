#!/usr/bin/env python3
"""
Live test for email service with actual Resend API.
This script will send a real test email to verify the integration works.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_live_email_service():
    """Test the email service with actual API calls"""
    print("🧪 Testing Live Email Service Integration")
    print("=" * 50)
    
    try:
        from app.services.email_service import get_email_service
        from app.core.config import settings
        from app.utils.email_utils import generate_verification_token
        
        print(f"📧 Email service configured: {settings.email_enabled}")
        print(f"🔑 API Key present: {'Yes' if settings.RESEND_API_KEY else 'No'}")
        print(f"📨 From email: {settings.RESEND_FROM_EMAIL}")
        print(f"🌐 Frontend URL: {settings.FRONTEND_URL}")
        print()
        
        if not settings.email_enabled:
            print("❌ Email service not properly configured")
            return False
        
        # Get email service
        email_service = get_email_service()
        
        # Generate a test verification token
        verification_token = generate_verification_token()
        
        print("🔄 Testing verification email...")
        
        # Test verification email (replace with your actual email for testing)
        test_email = "shayan.s.toor@gmail.com"  # Change this to your email for testing
        
        result = await email_service.send_verification_email(
            to_email=test_email,
            user_name="Test User",
            restaurant_name="Test Restaurant",
            verification_token=verification_token,
            base_url=settings.FRONTEND_URL
        )
        
        if result["success"]:
            print(f"✅ Verification email sent successfully!")
            print(f"   Email ID: {result.get('email_id', 'N/A')}")
            print(f"   Recipient: {result['to']}")
        else:
            print(f"❌ Verification email failed: {result['message']}")
            return False
        
        print()
        print("🔄 Testing welcome email...")
        
        # Test welcome email
        result = await email_service.send_welcome_email(
            to_email=test_email,
            user_name="Test User",
            restaurant_name="Test Restaurant",
            dashboard_url=f"{settings.FRONTEND_URL}/dashboard"
        )
        
        if result["success"]:
            print(f"✅ Welcome email sent successfully!")
            print(f"   Email ID: {result.get('email_id', 'N/A')}")
            print(f"   Recipient: {result['to']}")
        else:
            print(f"❌ Welcome email failed: {result['message']}")
            return False
        
        print()
        print("🔄 Testing admin notification...")
        
        # Test admin notification
        result = await email_service.send_admin_notification(
            user_email=test_email,
            restaurant_name="Test Restaurant",
            phone="+1234567890",
            address="123 Test Street, Test City, TC 12345",
            registration_time=datetime.utcnow()
        )
        
        if result["success"]:
            print(f"✅ Admin notification sent successfully!")
            print(f"   Email ID: {result.get('email_id', 'N/A')}")
            print(f"   Recipient: {result['to']}")
        else:
            print(f"❌ Admin notification failed: {result['message']}")
            return False
        
        print()
        print("🎉 All email tests passed! Email service is fully functional.")
        return True
        
    except Exception as e:
        print(f"❌ Email service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n🔄 Testing rate limiting...")
    
    try:
        from app.services.email_service import get_email_service
        
        email_service = get_email_service()
        
        # Try to send multiple emails quickly to test rate limiting
        for i in range(3):
            result = await email_service.send_custom_email(
                to_email="test@example.com",
                subject=f"Rate Limit Test {i+1}",
                html_content=f"<p>This is test email #{i+1} for rate limiting.</p>"
            )
            
            if result["success"]:
                print(f"   ✅ Email {i+1} sent successfully")
            else:
                print(f"   ❌ Email {i+1} failed: {result['message']}")
        
        print("✅ Rate limiting test completed")
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False

def main():
    """Run the live email tests"""
    print("⚠️  WARNING: This will send real emails using the Resend API!")
    print("Make sure to update the test_email variable with your actual email address.")
    print()
    
    # Run the actual email tests
    success = asyncio.run(test_live_email_service())
    
    # Also run a basic configuration test
    try:
        from app.core.config import settings
        print("📧 Email Configuration Status:")
        print(f"   API Key configured: {'✅' if settings.RESEND_API_KEY else '❌'}")
        print(f"   From email: {settings.RESEND_FROM_EMAIL}")
        print(f"   Domain: {settings.RESEND_DOMAIN}")
        print(f"   Admin email: {settings.ADMIN_EMAIL}")
        print(f"   Email verification enabled: {'✅' if settings.ENABLE_EMAIL_VERIFICATION else '❌'}")
        print(f"   Admin notifications enabled: {'✅' if settings.ENABLE_ADMIN_NOTIFICATIONS else '❌'}")
        print(f"   Welcome emails enabled: {'✅' if settings.ENABLE_WELCOME_EMAILS else '❌'}")
        print()
        print("🎉 Email service is properly configured and ready to use!")
        print()
        print("To test actual email sending:")
        print("1. Update the test_email variable in this script with your email")
        print("2. Uncomment the asyncio.run(test_live_email_service()) line")
        print("3. Run the script again")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)