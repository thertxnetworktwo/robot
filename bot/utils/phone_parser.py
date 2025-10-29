import phonenumbers
from phonenumbers import geocoder, carrier
import pycountry
import re


class PhoneParser:
    """Parse and validate phone numbers"""
    
    @staticmethod
    def is_phone_number(text):
        """Check if text looks like a phone number with + prefix"""
        if not text:
            return False
        
        # Check if starts with + and contains only digits after that
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, text.strip()))
    
    @staticmethod
    def parse_phone_number(phone_str):
        """
        Parse phone number and extract information
        Returns: dict with phone info or None if invalid
        """
        try:
            # Parse the phone number
            parsed = phonenumbers.parse(phone_str, None)
            
            # Validate the number
            if not phonenumbers.is_valid_number(parsed):
                return None
            
            # Get country code (ISO2)
            country_code = geocoder.region_code_for_number(parsed)
            
            # Get country name
            country = pycountry.countries.get(alpha_2=country_code)
            country_name = country.name if country else country_code
            
            # Format the number in international format
            formatted_number = phonenumbers.format_number(
                parsed, 
                phonenumbers.PhoneNumberFormat.E164
            )
            
            return {
                'phone_number': formatted_number,
                'country_code': country_code,  # ISO2 code
                'country_name': country_name,
                'is_valid': True,
                'original': phone_str
            }
            
        except phonenumbers.NumberParseException:
            return None
    
    @staticmethod
    def validate_phone_for_country(phone_str, country_iso2):
        """
        Validate that phone number belongs to specified country
        """
        phone_info = PhoneParser.parse_phone_number(phone_str)
        if not phone_info:
            return False
        
        return phone_info['country_code'] == country_iso2.upper()
    
    @staticmethod
    def format_phone_number(phone_str):
        """Format phone number to E164 format"""
        try:
            parsed = phonenumbers.parse(phone_str, None)
            return phonenumbers.format_number(
                parsed, 
                phonenumbers.PhoneNumberFormat.E164
            )
        except:
            return phone_str
