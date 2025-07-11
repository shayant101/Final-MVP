import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # Database Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "momentum_growth")
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))
    
    # Email Configuration (Resend)
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_FROM_EMAIL: str = os.getenv("RESEND_FROM_EMAIL", "noreply@example.com")
    RESEND_DOMAIN: str = os.getenv("RESEND_DOMAIN", "example.com")
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = int(os.getenv("EMAIL_VERIFICATION_EXPIRE_HOURS", "24"))
    ADMIN_EMAIL: Optional[str] = os.getenv("ADMIN_EMAIL")
    
    # Email Service Configuration
    EMAIL_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("EMAIL_RATE_LIMIT_PER_MINUTE", "10"))
    EMAIL_MAX_RETRIES: int = int(os.getenv("EMAIL_MAX_RETRIES", "3"))
    EMAIL_RETRY_DELAY: float = float(os.getenv("EMAIL_RETRY_DELAY", "1.0"))
    
    # Frontend Configuration
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Restaurant Marketing Platform"
    PROJECT_VERSION: str = "2.0.0"
    
    # External Services Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Feature Flags
    ENABLE_EMAIL_VERIFICATION: bool = os.getenv("ENABLE_EMAIL_VERIFICATION", "true").lower() == "true"
    ENABLE_ADMIN_NOTIFICATIONS: bool = os.getenv("ENABLE_ADMIN_NOTIFICATIONS", "true").lower() == "true"
    ENABLE_WELCOME_EMAILS: bool = os.getenv("ENABLE_WELCOME_EMAILS", "true").lower() == "true"
    
    # Development/Debug Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
    
    @property
    def email_enabled(self) -> bool:
        """Check if email service is properly configured"""
        return bool(self.RESEND_API_KEY and self.RESEND_FROM_EMAIL)
    
    @property
    def verification_url_base(self) -> str:
        """Get base URL for email verification links"""
        return f"{self.FRONTEND_URL}/verify-email"
    
    @property
    def dashboard_url(self) -> str:
        """Get dashboard URL for welcome emails"""
        return f"{self.FRONTEND_URL}/dashboard"
    
    def get_email_config(self) -> dict:
        """Get email configuration as dictionary"""
        return {
            "api_key": self.RESEND_API_KEY,
            "from_email": self.RESEND_FROM_EMAIL,
            "domain": self.RESEND_DOMAIN,
            "verification_expire_hours": self.EMAIL_VERIFICATION_EXPIRE_HOURS,
            "admin_email": self.ADMIN_EMAIL,
            "rate_limit_per_minute": self.EMAIL_RATE_LIMIT_PER_MINUTE,
            "max_retries": self.EMAIL_MAX_RETRIES,
            "retry_delay": self.EMAIL_RETRY_DELAY
        }

# Global settings instance
settings = Settings()

# Environment validation
def validate_environment():
    """Validate critical environment variables"""
    errors = []
    
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production":
        errors.append("SECRET_KEY must be set to a secure value")
    
    if not settings.MONGODB_URL:
        errors.append("MONGODB_URL must be set")
    
    if settings.ENABLE_EMAIL_VERIFICATION and not settings.RESEND_API_KEY:
        errors.append("RESEND_API_KEY must be set when email verification is enabled")
    
    if settings.ENABLE_EMAIL_VERIFICATION and not settings.RESEND_FROM_EMAIL:
        errors.append("RESEND_FROM_EMAIL must be set when email verification is enabled")
    
    if settings.ENABLE_ADMIN_NOTIFICATIONS and not settings.ADMIN_EMAIL:
        errors.append("ADMIN_EMAIL must be set when admin notifications are enabled")
    
    return errors

# Utility functions
def get_verification_url(token: str) -> str:
    """Generate email verification URL"""
    return f"{settings.verification_url_base}?token={token}"

def get_dashboard_url() -> str:
    """Get dashboard URL"""
    return settings.dashboard_url

def is_production() -> bool:
    """Check if running in production environment"""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"

def is_development() -> bool:
    """Check if running in development environment"""
    return os.getenv("ENVIRONMENT", "development").lower() == "development"