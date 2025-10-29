from bot.utils.phone_parser import PhoneParser
from database.db import db


class CountryDetector:
    """Detect country from phone number"""
    
    @staticmethod
    def detect_country(phone_number):
        """
        Detect country from phone number
        Returns: dict with country info or None
        """
        # Parse phone number
        phone_info = PhoneParser.parse_phone_number(phone_number)
        if not phone_info:
            return None
        
        # Get country from database
        country = db.get_country_by_iso2(phone_info['country_code'])
        
        if country:
            return {
                'iso2_code': country.iso2_code,
                'name': country.name,
                'price': country.price,
                'phone_prefix': country.phone_prefix,
                'capacity': country.capacity,
                'current_count': country.current_count,
                'is_active': country.is_active,
                'phone_info': phone_info
            }
        
        # Country exists in phone library but not in our database
        return {
            'iso2_code': phone_info['country_code'],
            'name': phone_info['country_name'],
            'price': None,
            'phone_prefix': None,
            'capacity': None,
            'current_count': None,
            'is_active': False,
            'phone_info': phone_info
        }
    
    @staticmethod
    def is_country_supported(country_iso2):
        """Check if country is supported in database"""
        country = db.get_country_by_iso2(country_iso2)
        return country is not None and country.is_active
    
    @staticmethod
    def get_supported_countries():
        """Get list of all supported countries"""
        return db.get_all_countries(active_only=True)
