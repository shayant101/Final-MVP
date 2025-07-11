"""
Core configuration and settings module for the Restaurant Marketing Platform.

This module contains application-wide configuration, settings, and utilities.
"""

from .config import settings, validate_environment, get_verification_url, get_dashboard_url, is_production, is_development

__all__ = [
    "settings",
    "validate_environment", 
    "get_verification_url",
    "get_dashboard_url",
    "is_production",
    "is_development"
]