from telethon import TelegramClient
from pathlib import Path
import json
import base64


class SessionExporter:
    """Export Telegram sessions to different formats"""
    
    @staticmethod
    async def export_to_string(session_path, api_id, api_hash):
        """
        Export session to session string format
        """
        try:
            client = TelegramClient(str(session_path), int(api_id), api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.disconnect()
                return None
            
            # Get session string
            session_string = client.session.save()
            
            await client.disconnect()
            
            return session_string
            
        except Exception:
            return None
    
    @staticmethod
    async def export_to_json(session_path, api_id, api_hash):
        """
        Export session to JSON format
        """
        try:
            client = TelegramClient(str(session_path), int(api_id), api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.disconnect()
                return None
            
            # Get user info
            me = await client.get_me()
            
            # Build JSON data
            session_data = {
                'session_string': client.session.save(),
                'api_id': api_id,
                'api_hash': api_hash,
                'user_id': me.id,
                'phone': me.phone,
                'username': me.username,
                'first_name': me.first_name,
                'last_name': me.last_name,
            }
            
            await client.disconnect()
            
            return json.dumps(session_data, indent=2)
            
        except Exception:
            return None
    
    @staticmethod
    def read_session_file(session_path):
        """
        Read raw session file
        """
        try:
            path = Path(session_path)
            if path.exists():
                with open(path, 'rb') as f:
                    return f.read()
            return None
        except Exception:
            return None
