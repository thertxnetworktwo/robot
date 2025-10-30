# Security Features

This document describes the security features implemented in the bot to protect users and prevent abuse.

## OTP Code Reuse Prevention

### Problem
Telegram login codes (OTP) are meant for single use only. If a code is shared or reused, it can indicate:
- Code sharing between users (security violation)
- Replay attacks
- Compromised authentication flows

### Solution
The bot now implements OTP code reuse detection:

1. **Code Hashing**: Each OTP code is hashed using HMAC-SHA256 with a secret key
   - Codes are combined with phone numbers before hashing
   - Hashes are stored instead of actual codes (secure)
   - Same code produces same hash for detection

2. **Reuse Detection**: Before verifying an OTP, the system checks:
   - Has this exact code been used before for this phone number?
   - Was it used in the last 24 hours?
   - Was it successfully verified?

3. **User Notification**: If code reuse is detected:
   ```
   ⚠️ This code has already been used. Please request a new code.
   
   🔒 Security Note: Never share your login codes with anyone.
   Telegram codes are single-use only.
   ```

## Rate Limiting

### Problem
Unlimited login attempts allow:
- Brute force attacks
- OTP code guessing
- System abuse

### Solution
The bot implements rate limiting on OTP verification:

- **Limit**: Maximum 5 failed attempts per phone number per hour
- **Tracking**: All failed attempts are logged with timestamps
- **Response**: When limit exceeded:
  ```
  ⚠️ Too many failed attempts. Please try again in 1 hour.
  ```

## Login Attempt Tracking

### Database Model
A new `login_attempts` table tracks all login activity:

```python
class LoginAttempt:
    - id: Unique identifier
    - user_id: Telegram user ID
    - phone_number: Phone number being verified
    - attempt_type: otp_request / otp_verify / password_verify
    - success: Boolean (True/False)
    - error_message: Description of failure (if failed)
    - code_hash: Hashed OTP code (for reuse detection)
    - ip_address: IP address of the attempt (optional)
    - user_agent: User agent string (optional)
    - attempt_time: Timestamp
```

### Benefits
1. **Security Monitoring**: Track suspicious patterns
2. **Audit Trail**: Complete history of login attempts
3. **Analytics**: Identify attack attempts
4. **Debugging**: Troubleshoot user issues

## OTP Format Validation

### Problem
Invalid OTP formats waste API calls and expose system to errors.

### Solution
Pre-validation before Telegram API call:

```python
def validate_otp_format(otp_code):
    - Accepts any input type and converts to string internally
    - Must be numeric (digits only)
    - Length: 4-6 digits (Telegram standard)
    - Returns: True/False
```

Benefits:
- Early error detection
- Reduced API calls
- Better user experience

## Security Warnings

### User Education
The bot now displays security warnings when users submit phone numbers:

```
⚠️ SECURITY WARNING:
• Your login code is for ONE-TIME use only
• NEVER share your code with anyone else
• Each code can only be used once
• Sharing codes violates Telegram's security policy
```

### Error Messages
Enhanced error messages include security tips:

```
❌ Invalid OTP code. Please check and try again.

🔒 Security Tip: Each code can only be used once.
Do not share codes with others.
```

## Implementation Details

### Files Modified/Created

1. **database/models.py**
   - Added `LoginAttempt` model

2. **database/db.py**
   - `log_login_attempt()`: Record attempts
   - `check_code_reuse()`: Detect reused codes
   - `get_failed_attempts_count()`: Rate limiting

3. **bot/utils/security.py** (NEW)
   - `hash_otp_code()`: Secure code hashing
   - `validate_otp_format()`: Format validation
   - `check_rate_limit()`: Rate limit checking

4. **bot/services/session_creator.py**
   - Enhanced `verify_otp()` with security checks
   - Enhanced `verify_password()` with logging

5. **bot/handlers/account.py**
   - Added security warnings in messages
   - Pass user_id to security functions

### Security Best Practices

1. **Never Log Actual Codes**: Only store hashed versions
2. **Time-Limited Detection**: Check reuse within 24 hours
3. **Secure Hashing**: Use HMAC-SHA256 with secret key
4. **User Privacy**: Hash combines phone + code (user-specific)
5. **Rate Limiting**: Prevent brute force attacks

## Testing

Run security tests:
```bash
python test_security.py
```

Tests verify:
- ✓ OTP code hashing
- ✓ Format validation
- ✓ Rate limiting logic
- ✓ Database operations
- ✓ Code reuse detection

## Future Enhancements

Potential improvements:
1. **IP-based rate limiting**: Track by IP address
2. **Device fingerprinting**: Detect suspicious devices
3. **2FA enforcement**: Require 2FA for all accounts
4. **Email notifications**: Alert admins of suspicious activity
5. **Temporary bans**: Auto-ban repeat offenders
6. **Geographic restrictions**: Limit by country/region

## Security Considerations

### What This Prevents
- ✓ OTP code reuse/sharing
- ✓ Brute force attacks
- ✓ Replay attacks
- ✓ Excessive failed attempts

### What This Doesn't Prevent
- ✗ User giving credentials to others
- ✗ Session hijacking (separate concern)
- ✗ Social engineering attacks
- ✗ Telegram API vulnerabilities

### Important Notes

⚠️ **Legal Compliance**: This bot collects and stores user phone numbers and login attempts. Ensure compliance with:
- GDPR (EU)
- CCPA (California)
- Local data protection laws

⚠️ **Telegram Terms**: Creating and storing Telegram sessions may violate Telegram's Terms of Service. Use responsibly and ensure users understand the implications.

## Support

For questions or issues:
1. Review this documentation
2. Check test results: `python test_security.py`
3. Review code comments in security.py
4. Open an issue on GitHub
