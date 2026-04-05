import secrets
import hashlib
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional
from email_validator import validate_email as validate_email_lib, EmailNotValidError


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2"""
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password, method='pbkdf2:sha256')


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a password against its hash"""
    from werkzeug.security import check_password_hash
    return check_password_hash(password_hash, password)


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email using email-validator library"""
    if not email or len(email) > 254:
        return False, "Email is required and must be less than 254 characters"
    
    try:
        # Validate and normalize email
        valid = validate_email_lib(email)
        normalized_email = valid.email
        return True, None
    except EmailNotValidError as e:
        return False, f"Invalid email address: {str(e)}"
    except Exception as e:
        return False, f"Email validation error: {str(e)}"


def generate_verification_token() -> str:
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """Generate a secure password reset token"""
    return secrets.token_urlsafe(32)


def is_password_strong(password: str) -> Tuple[bool, str]:
    """
    Check if password meets minimum requirements
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character from !@#$%^&*
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter (A-Z)"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter (a-z)"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit (0-9)"
    
    if not any(c in '!@#$%^&*' for c in password):
        return False, "Password must contain at least one special character (!@#$%^&*)"

    return True, "Password meets security requirements"

