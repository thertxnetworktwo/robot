from telethon import TelegramClient
from telethon.errors import UserDeactivatedError, AuthKeyUnregisteredError


class FreezeChecker:
    """Check if account is frozen or banned"""
    
    @staticmethod
    async def check_freeze(session_path, api_id, api_hash):
        """
        Check if account is frozen/banned
        Returns: dict with freeze status
        """
        try:
            client = TelegramClient(str(session_path), int(api_id), api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.disconnect()
                return {
                    'is_frozen': True,
                    'reason': 'Not authorized',
                    'checked': True
                }
            
            # Try to get own info - if this fails, account is likely banned
            try:
                me = await client.get_me()
                
                # Check if account can send messages (basic test)
                # If we can get our own info, account is likely active
                await client.disconnect()
                
                return {
                    'is_frozen': False,
                    'checked': True,
                    'user_id': me.id
                }
                
            except (UserDeactivatedError, AuthKeyUnregisteredError):
                await client.disconnect()
                return {
                    'is_frozen': True,
                    'reason': 'Account deactivated or banned',
                    'checked': True
                }
            except Exception as e:
                await client.disconnect()
                return {
                    'is_frozen': True,
                    'reason': str(e),
                    'checked': True
                }
            
        except Exception as e:
            return {
                'is_frozen': None,
                'error': str(e),
                'checked': False
            }
    
    @staticmethod
    async def check_can_receive_messages(session_path, api_id, api_hash):
        """
        Check if account can receive messages
        """
        try:
            client = TelegramClient(str(session_path), int(api_id), api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.disconnect()
                return {
                    'can_receive': None,
                    'error': 'Not authorized'
                }
            
            # Try to get dialogs (recent chats)
            # If we can access dialogs, we can likely receive messages
            dialogs = await client.get_dialogs(limit=1)
            
            await client.disconnect()
            
            return {
                'can_receive': True,
                'checked': True
            }
            
        except Exception as e:
            return {
                'can_receive': False,
                'error': str(e),
                'checked': False
            }
