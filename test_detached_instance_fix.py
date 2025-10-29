#!/usr/bin/env python3
"""
Test to verify that SQLAlchemy DetachedInstanceError is fixed
for all database query methods that return model objects.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_country_detector():
    """Test CountryDetector doesn't throw DetachedInstanceError"""
    print("Testing CountryDetector.detect_country()...")
    
    from bot.utils.country_detector import CountryDetector
    
    try:
        # Test with valid phone number
        result = CountryDetector.detect_country('+8801712345678')
        assert result is not None, "Should detect country for valid phone number"
        assert result['iso2_code'] == 'BD', "Should detect Bangladesh"
        assert result['name'] == 'Bangladesh', "Should have country name"
        assert result['price'] == 2.0, "Should have price"
        assert result['is_active'] is True, "Should be active"
        print("✓ CountryDetector works without DetachedInstanceError")
        return True
    except Exception as e:
        print(f"✗ CountryDetector failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_user():
    """Test db.get_user() doesn't throw DetachedInstanceError"""
    print("\nTesting db.get_user()...")
    
    from database.db import db
    
    try:
        # Create a test user
        user = db.get_or_create_user(123456, "test_user")
        
        # Get the user
        fetched_user = db.get_user(123456)
        assert fetched_user is not None, "Should find the user"
        
        # Access attributes (this would fail if detached)
        assert fetched_user.user_id == 123456, "Should have correct user_id"
        assert fetched_user.username == "test_user", "Should have correct username"
        balance = fetched_user.balance  # This triggers attribute access
        assert balance == 0.0, "Should have zero balance initially"
        
        print("✓ db.get_user() works without DetachedInstanceError")
        return True
    except Exception as e:
        print(f"✗ db.get_user() failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_country_by_iso2():
    """Test db.get_country_by_iso2() doesn't throw DetachedInstanceError"""
    print("\nTesting db.get_country_by_iso2()...")
    
    from database.db import db
    
    try:
        # Get a country
        country = db.get_country_by_iso2('BD')
        assert country is not None, "Should find Bangladesh"
        
        # Access all attributes (this would fail if detached)
        assert country.iso2_code == 'BD', "Should have correct ISO2 code"
        assert country.name == 'Bangladesh', "Should have correct name"
        assert country.phone_prefix == '+880', "Should have correct phone prefix"
        assert country.price == 2.0, "Should have correct price"
        assert country.capacity == 1000, "Should have correct capacity"
        assert country.current_count == 0, "Should have correct current_count"
        assert country.is_active is True, "Should be active"
        
        print("✓ db.get_country_by_iso2() works without DetachedInstanceError")
        return True
    except Exception as e:
        print(f"✗ db.get_country_by_iso2() failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_all_countries():
    """Test db.get_all_countries() doesn't throw DetachedInstanceError"""
    print("\nTesting db.get_all_countries()...")
    
    from database.db import db
    
    try:
        # Get all countries
        countries = db.get_all_countries()
        assert len(countries) > 0, "Should have at least one country"
        
        # Access attributes on each country (this would fail if detached)
        for country in countries:
            _ = country.iso2_code
            _ = country.name
            _ = country.phone_prefix
            _ = country.price
            _ = country.capacity
            _ = country.current_count
            _ = country.is_active
        
        print(f"✓ db.get_all_countries() works without DetachedInstanceError ({len(countries)} countries)")
        return True
    except Exception as e:
        print(f"✗ db.get_all_countries() failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_account():
    """Test db.create_account() doesn't throw DetachedInstanceError"""
    print("\nTesting db.create_account()...")
    
    from database.db import db
    import random
    
    try:
        # Create a test user first
        test_user_id = random.randint(100000, 999999)
        db.get_or_create_user(test_user_id, "test_account_user")
        
        # Create an account
        test_phone = f"+88017{random.randint(10000000, 99999999)}"
        account = db.create_account(
            user_id=test_user_id,
            phone_number=test_phone,
            country_iso2='BD',
            api_id='12345',
            api_hash='test_hash'
        )
        
        assert account is not None, "Should create account"
        
        # Access attributes (this would fail if detached)
        assert account.user_id == test_user_id, "Should have correct user_id"
        assert account.phone_number == test_phone, "Should have correct phone number"
        assert account.country_iso2 == 'BD', "Should have correct country"
        assert account.status == 'pending', "Should have pending status"
        
        print("✓ db.create_account() works without DetachedInstanceError")
        return True
    except Exception as e:
        print(f"✗ db.create_account() failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_user_accounts():
    """Test db.get_user_accounts() doesn't throw DetachedInstanceError"""
    print("\nTesting db.get_user_accounts()...")
    
    from database.db import db
    import random
    
    try:
        # Create a test user first
        test_user_id = random.randint(100000, 999999)
        db.get_or_create_user(test_user_id, "test_accounts_user")
        
        # Create an account for this user
        test_phone = f"+88017{random.randint(10000000, 99999999)}"
        db.create_account(
            user_id=test_user_id,
            phone_number=test_phone,
            country_iso2='BD',
            api_id='12345',
            api_hash='test_hash'
        )
        
        # Get all accounts for this user
        accounts = db.get_user_accounts(test_user_id)
        assert len(accounts) > 0, "Should have at least one account"
        
        # Access attributes on each account (this would fail if detached)
        for account in accounts:
            _ = account.user_id
            _ = account.phone_number
            _ = account.country_iso2
            _ = account.status
        
        print(f"✓ db.get_user_accounts() works without DetachedInstanceError ({len(accounts)} accounts)")
        return True
    except Exception as e:
        print(f"✗ db.get_user_accounts() failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("SQLAlchemy DetachedInstanceError Fix Test")
    print("=" * 60)
    
    tests = [
        ("CountryDetector", test_country_detector),
        ("get_user", test_get_user),
        ("get_country_by_iso2", test_get_country_by_iso2),
        ("get_all_countries", test_get_all_countries),
        ("create_account", test_create_account),
        ("get_user_accounts", test_get_user_accounts),
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
        print("\n🎉 All tests passed! No DetachedInstanceError issues found.")
    else:
        print("\n❌ Some tests failed. DetachedInstanceError may still occur.")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
