from telethon import TelegramClient


class ContactChecker:
    """Check if account has contacts"""
    
    @staticmethod
    async def check_contacts(session_path, api_id, api_hash):
        """
        Check if account has contacts
        Returns: dict with contact status
        """
        try:
            client = TelegramClient(str(session_path), int(api_id), api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.disconnect()
                return {
                    'has_contacts': None,
                    'error': 'Not authorized'
                }
            
            # Get contacts
            contacts = await client.get_contacts()
            
            await client.disconnect()
            
            return {
                'has_contacts': len(contacts) > 0,
                'contact_count': len(contacts),
                'checked': True
            }
            
        except Exception as e:
            return {
                'has_contacts': None,
                'error': str(e),
                'checked': False
            }
