#!/usr/bin/env python3
"""
Test script to verify the setup
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    
    try:
        import config
        print("✓ Config imported")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from database.db import db
        print("✓ Database imported")
    except Exception as e:
        print(f"✗ Database import failed: {e}")
        return False
    
    try:
        from database.models import User, Account, Country
        print("✓ Models imported")
    except Exception as e:
        print(f"✗ Models import failed: {e}")
        return False
    
    try:
        from bot.utils.phone_parser import PhoneParser
        from bot.utils.country_detector import CountryDetector
        print("✓ Bot utils imported")
    except Exception as e:
        print(f"✗ Bot utils import failed: {e}")
        return False
    
    return True


def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    
    try:
        from database.db import db
        print("✓ Database initialized")
        
        # Test getting settings
        bot_status = db.get_setting('bot_status')
        print(f"✓ Database operations work (bot_status: {bot_status})")
        
        # Test getting countries
        with db.get_session() as session:
            from database.models import Country
            countries = session.query(Country).all()
            print(f"✓ Found {len(countries)} countries in database")
            for country in countries:
                print(f"  - {country.name} ({country.iso2_code}): ${country.price}")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phone_parser():
    """Test phone number parsing"""
    print("\nTesting phone parser...")
    
    try:
        from bot.utils.phone_parser import PhoneParser
        
        # Test valid phone numbers
        test_numbers = [
            "+8801712345678",  # Bangladesh
            "+14155552671",    # USA
            "+447123456789",   # UK
        ]
        
        for number in test_numbers:
            result = PhoneParser.parse_phone_number(number)
            if result:
                print(f"✓ Parsed {number}: {result['country_code']} - {result['country_name']}")
            else:
                print(f"✗ Failed to parse {number}")
        
        return True
    except Exception as e:
        print(f"✗ Phone parser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Session Bot Setup Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Phone Parser", test_phone_parser),
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
        print("\n🎉 All tests passed! The bot is ready to use.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Start the bot: python bot/main.py")
        print("3. Start the web admin: python web_admin/app.py")
    else:
        print("\n❌ Some tests failed. Please fix the errors above.")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
