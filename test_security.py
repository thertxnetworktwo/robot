#!/usr/bin/env python3
"""
Test script to verify security features for OTP code reuse prevention
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_security_utils():
    """Test security utility functions"""
    print("Testing security utilities...")
    
    try:
        from bot.utils.security import hash_otp_code, validate_otp_format, check_rate_limit
        
        # Test OTP hashing
        hash1 = hash_otp_code("+14155552671", "12345")
        hash2 = hash_otp_code("+14155552671", "12345")
        hash3 = hash_otp_code("+14155552671", "54321")
        
        assert hash1 == hash2, "Same code should produce same hash"
        assert hash1 != hash3, "Different codes should produce different hashes"
        print("✓ OTP hashing works correctly")
        
        # Test OTP validation
        assert validate_otp_format("12345") == True, "Valid 5-digit code should pass"
        assert validate_otp_format("1234") == True, "Valid 4-digit code should pass"
        assert validate_otp_format("123456") == True, "Valid 6-digit code should pass"
        assert validate_otp_format("abc") == False, "Non-numeric code should fail"
        assert validate_otp_format("123") == False, "Too short code should fail"
        assert validate_otp_format("1234567") == False, "Too long code should fail"
        print("✓ OTP validation works correctly")
        
        # Test rate limiting
        assert check_rate_limit(3, max_attempts=5) == False, "Below limit should not trigger"
        assert check_rate_limit(5, max_attempts=5) == True, "At limit should trigger"
        assert check_rate_limit(10, max_attempts=5) == True, "Above limit should trigger"
        print("✓ Rate limiting works correctly")
        
        return True
    except Exception as e:
        print(f"✗ Security utils test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_login_attempt_tracking():
    """Test login attempt tracking in database"""
    print("\nTesting login attempt tracking...")
    
    try:
        from database.db import db
        from bot.utils.security import hash_otp_code
        
        # Log a successful attempt
        attempt1 = db.log_login_attempt(
            user_id=123456,
            phone_number="+14155552671",
            attempt_type="otp_verify",
            success=True,
            code_hash=hash_otp_code("+14155552671", "12345")
        )
        print(f"✓ Logged successful attempt: ID {attempt1.id}")
        
        # Log a failed attempt
        attempt2 = db.log_login_attempt(
            user_id=123456,
            phone_number="+14155552671",
            attempt_type="otp_verify",
            success=False,
            error_message="Invalid OTP code"
        )
        print(f"✓ Logged failed attempt: ID {attempt2.id}")
        
        # Check code reuse detection
        code_hash = hash_otp_code("+14155552671", "12345")
        is_reused = db.check_code_reuse("+14155552671", code_hash)
        assert is_reused == True, "Should detect code was already used"
        print("✓ Code reuse detection works")
        
        # Check different code is not flagged as reused
        new_code_hash = hash_otp_code("+14155552671", "54321")
        is_reused_new = db.check_code_reuse("+14155552671", new_code_hash)
        assert is_reused_new == False, "New code should not be flagged as reused"
        print("✓ New codes are not flagged as reused")
        
        # Check failed attempts count
        failed_count = db.get_failed_attempts_count("+14155552671", hours=1)
        assert failed_count >= 1, "Should count failed attempts"
        print(f"✓ Failed attempts count: {failed_count}")
        
        return True
    except Exception as e:
        print(f"✗ Login attempt tracking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_model():
    """Test LoginAttempt model exists and works"""
    print("\nTesting LoginAttempt model...")
    
    try:
        from database.models import LoginAttempt
        from database.db import db
        
        # Verify table was created
        with db.get_session() as session:
            count = session.query(LoginAttempt).count()
            print(f"✓ LoginAttempt table exists with {count} records")
        
        return True
    except Exception as e:
        print(f"✗ LoginAttempt model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all security tests"""
    print("=" * 60)
    print("Security Feature Tests")
    print("=" * 60)
    
    tests = [
        ("Security Utils", test_security_utils),
        ("LoginAttempt Model", test_database_model),
        ("Login Attempt Tracking", test_login_attempt_tracking),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 All security tests passed!")
        print("\nSecurity features implemented:")
        print("✓ OTP code hashing for reuse detection")
        print("✓ OTP format validation")
        print("✓ Rate limiting for failed attempts")
        print("✓ Login attempt tracking in database")
        print("✓ Security warnings for users")
    else:
        print("\n❌ Some security tests failed. Please fix the errors above.")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
