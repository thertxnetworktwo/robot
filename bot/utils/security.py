"""Security utilities for the bot"""
import hashlib
import hmac
from config import SECRET_KEY


def hash_otp_code(phone_number, otp_code):
    """
    Create a secure hash of an OTP code
    This is used to detect code reuse without storing the actual code
    """
    # Combine phone number and code for hashing
    message = f"{phone_number}:{otp_code}"
    
    # Use HMAC-SHA256 with secret key for security
    hash_obj = hmac.new(
        SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    
    return hash_obj.hexdigest()


def validate_otp_format(otp_code):
    """
    Validate OTP code format
    Returns True if valid, False otherwise
    """
    # Remove whitespace
    otp_code = str(otp_code).strip()
    
    # Check if it's numeric
    if not otp_code.isdigit():
        return False
    
    # Check length (Telegram OTP codes are typically 5 digits)
    if len(otp_code) < 4 or len(otp_code) > 6:
        return False
    
    return True


def check_rate_limit(failed_attempts, max_attempts=5):
    """
    Check if rate limit has been exceeded
    Returns True if rate limit exceeded, False otherwise
    """
    return failed_attempts >= max_attempts
