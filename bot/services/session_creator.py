from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneNumberInvalidError
from pathlib import Path
import config
import asyncio
from database.db import db


class SessionCreator:
    """Create Telegram sessions using Telethon"""
    
    def __init__(self):
        self.sessions_dir = config.SESSION_DIR
    
    def get_session_path(self, country_iso2, phone_number):
        """Get session file path for a phone number"""
        # Create country directory if not exists
        country_dir = self.sessions_dir / country_iso2.upper()
        country_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean phone number for filename (remove + and spaces)
        clean_phone = phone_number.replace('+', '').replace(' ', '')
        
        # Return session path
        return country_dir / f"{clean_phone}.session"
    
    async def create_session(self, phone_number, api_id, api_hash, country_iso2, password=None):
        """
        Create a Telegram session
        Returns: dict with session info and client for OTP verification
        """
        try:
            # Get session file path
            session_path = self.get_session_path(country_iso2, phone_number)
            
            # Create Telethon client
            client = TelegramClient(str(session_path), int(api_id), api_hash)
            
            # Connect to Telegram
            await client.connect()
            
            # Check if already authorized
            if await client.is_user_authorized():
                await client.disconnect()
                return {
                    'success': True,
                    'message': 'Already authorized',
                    'session_path': str(session_path),
                    'client': None
                }
            
            # Send code request
            await client.send_code_request(phone_number)
            
            return {
                'success': True,
                'message': 'Code sent',
                'session_path': str(session_path),
                'client': client,
                'requires_otp': True,
                'requires_password': False
            }
            
        except PhoneNumberInvalidError:
            return {
                'success': False,
                'message': 'Invalid phone number',
                'error': 'phone_invalid'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'error': str(e)
            }
    
    async def verify_otp(self, client, phone_number, otp_code, password=None):
        """
        Verify OTP code and complete session creation
        """
        try:
            # Sign in with OTP
            await client.sign_in(phone_number, otp_code)
            
            # Get session string
            session_string = client.session.save()
            
            # Disconnect
            await client.disconnect()
            
            return {
                'success': True,
                'message': 'Session created successfully',
                'session_string': session_string
            }
            
        except SessionPasswordNeededError:
            # 2FA is enabled
            return {
                'success': False,
                'message': '2FA password required',
                'requires_password': True,
                'client': client
            }
        except PhoneCodeInvalidError:
            return {
                'success': False,
                'message': 'Invalid OTP code',
                'error': 'invalid_otp'
            }
        except Exception as e:
            try:
                await client.disconnect()
            except:
                pass
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'error': str(e)
            }
    
    async def verify_password(self, client, password):
        """
        Verify 2FA password
        """
        try:
            # Sign in with password
            await client.sign_in(password=password)
            
            # Get session string
            session_string = client.session.save()
            
            # Disconnect
            await client.disconnect()
            
            return {
                'success': True,
                'message': 'Session created successfully',
                'session_string': session_string
            }
            
        except Exception as e:
            try:
                await client.disconnect()
            except:
                pass
            return {
                'success': False,
                'message': f'Invalid password: {str(e)}',
                'error': 'invalid_password'
            }
    
    async def check_session_valid(self, session_path):
        """Check if a session is still valid"""
        try:
            # Try to connect with existing session
            client = TelegramClient(str(session_path), config.BOT_API_ID, config.BOT_API_HASH)
            await client.connect()
            
            is_authorized = await client.is_user_authorized()
            
            await client.disconnect()
            
            return is_authorized
            
        except Exception:
            return False
    
    def delete_session(self, session_path):
        """Delete session file"""
        try:
            path = Path(session_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False
