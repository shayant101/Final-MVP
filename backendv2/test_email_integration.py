#!/usr/bin/env python3
"""
Test script for email service integration.
This script tests the email service without actually sending emails.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all email-related modules can be imported successfully"""
    print("Testing imports...")
    
    try:
        from app.services.email_service import ResendEmailService, EmailConfig, get_email_service
        print("✅ Email service imports successful")
    except ImportError as e:
        print(f"❌ Email service import failed: {e}")
        return False
    
    try:
        from app.utils.email_utils import (
            generate_verification_token, 
            create_verification_data,
            validate_email_template_context
        )
        print("✅ Email utils imports successful")
    except ImportError as e:
        print(f"❌ Email utils import failed: {e}")
        return False
    
    try:
        from app.core.config import settings
        print("✅ Config imports successful")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from app.models import (
            EmailVerificationRequest,
            EmailVerificationResponse,
            ResendVerificationRequest,
            ResendVerificationResponse
        )
        print("✅ Email models imports successful")
    except ImportError as e:
        print(f"❌ Email models import failed: {e}")
        return False
    
    return True

def test_email_service_initialization():
    """Test email service initialization"""
    print("\nTesting email service initialization...")
    
    try:
        from app.services.email_service import EmailConfig, ResendEmailService
        
        # Test with mock configuration
        config = EmailConfig(
            api_key="test_key",
            from_email="test@example.com",
            domain="example.com",
            verification_expire_hours=24,
            admin_email="admin@example.com"
        )
        
        service = ResendEmailService(config)
        print("✅ Email service initialization successful")
        return True
    except Exception as e:
        print(f"❌ Email service initialization failed: {e}")
        return False

def test_token_generation():
    """Test email verification token generation"""
    print("\nTesting token generation...")
    
    try:
        from app.utils.email_utils import create_verification_data, verify_token_hash
        
        token, token_hash, expiry = create_verification_data()
        
        # Verify the token matches its hash
        if verify_token_hash(token, token_hash):
            print("✅ Token generation and verification successful")
            print(f"   Token length: {len(token)}")
            print(f"   Hash length: {len(token_hash)}")
            print(f"   Expiry: {expiry}")
            return True
        else:
            print("❌ Token verification failed")
            return False
    except Exception as e:
        print(f"❌ Token generation failed: {e}")
        return False

def test_template_context_validation():
    """Test email template context validation"""
    print("\nTesting template context validation...")
    
    try:
        from app.utils.email_utils import validate_email_template_context
        
        # Test with potentially dangerous content
        context = {
            "user_email": "test@example.com",
            "restaurant_name": "Test Restaurant <script>alert('xss')</script>",
            "verification_url": "https://example.com/verify?token=abc123"
        }
        
        validated = validate_email_template_context(context)
        
        if "<script>" not in validated["restaurant_name"]:
            print("✅ Template context validation successful")
            print(f"   Original: {context['restaurant_name']}")
            print(f"   Sanitized: {validated['restaurant_name']}")
            return True
        else:
            print("❌ Template context validation failed - dangerous content not removed")
            return False
    except Exception as e:
        print(f"❌ Template context validation failed: {e}")
        return False

def test_config_validation():
    """Test configuration validation"""
    print("\nTesting configuration validation...")
    
    try:
        from app.core.config import settings, validate_environment
        
        print(f"   Email enabled: {settings.email_enabled}")
        print(f"   Email verification enabled: {settings.ENABLE_EMAIL_VERIFICATION}")
        print(f"   Admin notifications enabled: {settings.ENABLE_ADMIN_NOTIFICATIONS}")
        print(f"   Welcome emails enabled: {settings.ENABLE_WELCOME_EMAILS}")
        
        # Test environment validation
        errors = validate_environment()
        if errors:
            print("⚠️  Environment validation warnings:")
            for error in errors:
                print(f"     - {error}")
        else:
            print("✅ Environment validation passed")
        
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

async def test_email_service_methods():
    """Test email service methods (without actually sending emails)"""
    print("\nTesting email service methods...")
    
    try:
        from app.services.email_service import EmailConfig, ResendEmailService
        
        # Create a test service with mock config
        config = EmailConfig(
            api_key="test_key",
            from_email="test@example.com",
            domain="example.com",
            verification_expire_hours=24,
            admin_email="admin@example.com"
        )
        
        service = ResendEmailService(config)
        
        # Test template rendering with fallback
        context = {
            "user_email": "test@example.com",
            "restaurant_name": "Test Restaurant",
            "verification_url": "https://example.com/verify?token=abc123",
            "expire_hours": 24
        }
        
        # Test fallback template generation
        verification_html = service._get_fallback_template("verification", context)
        welcome_html = service._get_fallback_template("welcome", context)
        admin_html = service._get_fallback_template("admin_notification", context)
        
        if all([verification_html, welcome_html, admin_html]):
            print("✅ Email template generation successful")
            print(f"   Verification template length: {len(verification_html)}")
            print(f"   Welcome template length: {len(welcome_html)}")
            print(f"   Admin notification template length: {len(admin_html)}")
            return True
        else:
            print("❌ Email template generation failed")
            return False
    except Exception as e:
        print(f"❌ Email service methods test failed: {e}")
        return False

def test_model_validation():
    """Test Pydantic model validation"""
    print("\nTesting model validation...")
    
    try:
        from app.models import (
            EmailVerificationRequest,
            EmailVerificationResponse,
            ResendVerificationRequest,
            User,
            UserRole
        )
        
        # Test EmailVerificationRequest
        verification_request = EmailVerificationRequest(token="test_token_123")
        print(f"✅ EmailVerificationRequest: {verification_request.token}")
        
        # Test ResendVerificationRequest
        resend_request = ResendVerificationRequest(email="test@example.com")
        print(f"✅ ResendVerificationRequest: {resend_request.email}")
        
        # Test User model with new fields
        user = User(
            user_id="123",
            email="test@example.com",
            role=UserRole.restaurant,
            created_at=datetime.utcnow(),
            email_verified=True,
            last_login=datetime.utcnow()
        )
        print(f"✅ User model with email fields: verified={user.email_verified}")
        
        return True
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Email Service Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_email_service_initialization,
        test_token_generation,
        test_template_context_validation,
        test_config_validation,
        test_model_validation
    ]
    
    async_tests = [
        test_email_service_methods
    ]
    
    passed = 0
    total = len(tests) + len(async_tests)
    
    # Run synchronous tests
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Run asynchronous tests
    for test in async_tests:
        try:
            if asyncio.run(test()):
                passed += 1
        except Exception as e:
            print(f"❌ Async test failed: {e}")
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Email service integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)