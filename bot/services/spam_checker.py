from telethon import TelegramClient
from telethon.tl.functions.contacts import ResolveUsernameRequest
import asyncio


class SpamChecker:
    """Check if account is marked as spam using @spaminfobot"""
    
    @staticmethod
    async def check_spam(phone_number, session_path, api_id, api_hash):
        """
        Check if phone number is marked as spam
        Uses @spaminfobot to check status
        Returns: dict with spam status
        """
        try:
            client = TelegramClient(str(session_path), int(api_id), api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.disconnect()
                return {
                    'is_spam': None,
                    'error': 'Not authorized'
                }
            
            # Try to send message to spaminfobot
            try:
                # Get spaminfobot
                result = await client(ResolveUsernameRequest('spaminfobot'))
                
                # Send phone number
                await client.send_message('spaminfobot', phone_number)
                
                # Wait for response
                await asyncio.sleep(3)
                
                # Get last message from spaminfobot
                messages = await client.get_messages('spaminfobot', limit=1)
                
                if messages:
                    response = messages[0].message.lower()
                    
                    # Check response for spam indicators
                    is_spam = any(keyword in response for keyword in [
                        'spam', 'scam', 'fake', 'reported', 'restricted'
                    ])
                    
                    await client.disconnect()
                    
                    return {
                        'is_spam': is_spam,
                        'response': messages[0].message,
                        'checked': True
                    }
                
            except Exception as e:
                # SpamInfoBot might not be accessible
                await client.disconnect()
                return {
                    'is_spam': False,
                    'error': f'Could not check: {str(e)}',
                    'checked': False
                }
            
            await client.disconnect()
            return {
                'is_spam': False,
                'checked': True
            }
            
        except Exception as e:
            return {
                'is_spam': None,
                'error': str(e),
                'checked': False
            }
