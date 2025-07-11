import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from ..core.config import settings

def generate_verification_token() -> str:
    """
    Generate a secure email verification token.
    
    Returns:
        str: A secure random token for email verification
    """
    return secrets.token_urlsafe(32)

def hash_verification_token(token: str) -> str:
    """
    Hash a verification token for secure storage.
    
    Args:
        token: The plain text token to hash
        
    Returns:
        str: The hashed token
    """
    return hashlib.sha256(token.encode()).hexdigest()

def verify_token_hash(token: str, token_hash: str) -> bool:
    """
    Verify a token against its hash.
    
    Args:
        token: The plain text token to verify
        token_hash: The stored hash to verify against
        
    Returns:
        bool: True if token matches hash, False otherwise
    """
    return hashlib.sha256(token.encode()).hexdigest() == token_hash

def get_verification_expiry() -> datetime:
    """
    Get the expiry datetime for email verification tokens.
    
    Returns:
        datetime: The expiry time for verification tokens
    """
    return datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)

def is_token_expired(expires_at: datetime) -> bool:
    """
    Check if a verification token has expired.
    
    Args:
        expires_at: The expiry datetime of the token
        
    Returns:
        bool: True if token has expired, False otherwise
    """
    return datetime.utcnow() > expires_at

def create_verification_data() -> Tuple[str, str, datetime]:
    """
    Create complete verification data (token, hash, expiry).
    
    Returns:
        Tuple[str, str, datetime]: (plain_token, hashed_token, expiry_datetime)
    """
    token = generate_verification_token()
    token_hash = hash_verification_token(token)
    expiry = get_verification_expiry()
    
    return token, token_hash, expiry

def sanitize_email_content(content: str) -> str:
    """
    Sanitize email content to prevent injection attacks.
    
    Args:
        content: The content to sanitize
        
    Returns:
        str: Sanitized content
    """
    # Basic sanitization - remove potentially dangerous characters
    dangerous_chars = ['<script', '</script>', 'javascript:', 'vbscript:', 'onload=', 'onerror=']
    sanitized = content
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char.lower(), '')
        sanitized = sanitized.replace(char.upper(), '')
    
    return sanitized

def validate_email_template_context(context: dict) -> dict:
    """
    Validate and sanitize email template context.
    
    Args:
        context: The template context dictionary
        
    Returns:
        dict: Validated and sanitized context
    """
    validated_context = {}
    
    for key, value in context.items():
        if isinstance(value, str):
            validated_context[key] = sanitize_email_content(value)
        else:
            validated_context[key] = value
    
    return validated_context

def format_registration_time(dt: Optional[datetime] = None) -> str:
    """
    Format registration time for email templates.
    
    Args:
        dt: The datetime to format (defaults to current time)
        
    Returns:
        str: Formatted datetime string
    """
    if dt is None:
        dt = datetime.utcnow()
    
    return dt.strftime("%B %d, %Y at %I:%M %p UTC")

def get_email_subject_prefix() -> str:
    """
    Get the email subject prefix based on environment.
    
    Returns:
        str: Subject prefix (e.g., "[DEV]" for development)
    """
    if settings.DEBUG:
        return "[DEV] "
    elif settings.TESTING:
        return "[TEST] "
    else:
        return ""

def build_verification_url(token: str, base_url: Optional[str] = None) -> str:
    """
    Build a complete email verification URL.
    
    Args:
        token: The verification token
        base_url: Optional base URL (defaults to settings.FRONTEND_URL)
        
    Returns:
        str: Complete verification URL
    """
    if base_url is None:
        base_url = settings.FRONTEND_URL
    
    return f"{base_url}/verify-email?token={token}"

def build_dashboard_url(base_url: Optional[str] = None) -> str:
    """
    Build a complete dashboard URL.
    
    Args:
        base_url: Optional base URL (defaults to settings.FRONTEND_URL)
        
    Returns:
        str: Complete dashboard URL
    """
    if base_url is None:
        base_url = settings.FRONTEND_URL
    
    return f"{base_url}/dashboard"

def log_email_event(event_type: str, recipient: str, details: dict = None):
    """
    Log email events for debugging and monitoring.
    
    Args:
        event_type: Type of email event (sent, failed, etc.)
        recipient: Email recipient
        details: Additional event details
    """
    import logging
    
    logger = logging.getLogger(__name__)
    
    log_data = {
        "event": event_type,
        "recipient": recipient,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {}
    }
    
    if event_type == "sent":
        logger.info(f"Email sent successfully: {log_data}")
    elif event_type == "failed":
        logger.error(f"Email send failed: {log_data}")
    else:
        logger.info(f"Email event: {log_data}")