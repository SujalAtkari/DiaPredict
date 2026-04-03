import secrets
import hashlib
from datetime import datetime, timedelta


def hash_password(password):
    """Hash a password using PBKDF2"""
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password, method='pbkdf2:sha256')


def verify_password(password_hash, password):
    """Verify a password against its hash"""
    from werkzeug.security import check_password_hash
    return check_password_hash(password_hash, password)


def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)


def generate_reset_token():
    """Generate a secure password reset token"""
    return secrets.token_urlsafe(32)


def is_password_strong(password):
    """
    Check if password meets minimum requirements
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."

    return True, "Password is strong."
