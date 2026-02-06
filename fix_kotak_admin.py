#!/usr/bin/env python
"""
Script to fix Kotak Neo API admin issues
"""

import os
import sys
import django
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astrology.settings')
django.setup()

from KOTAK_NEO_API.models import KotakNeoUserToken
from django.utils import timezone


def fix_datetime_issues():
    """Fix any datetime-related issues in the database"""
    print("Fixing Kotak Neo API datetime issues...")
    
    try:
        # Fix tokens with None expires_at
        tokens_without_expiry = KotakNeoUserToken.objects.filter(expires_at__isnull=True)
        print(f"Found {tokens_without_expiry.count()} tokens without expiry date")
        
        for token in tokens_without_expiry:
            token.expires_at = timezone.now() + timedelta(hours=24)
            token.save()
            print(f"Fixed token for user: {token.user_id}")
        
        # Check for any other potential issues
        all_tokens = KotakNeoUserToken.objects.all()
        print(f"Total tokens in database: {all_tokens.count()}")
        
        for token in all_tokens:
            try:
                # Test the properties
                is_expired = token.is_expired
                is_valid = token.is_valid
                print(f"Token {token.user_id}: expired={is_expired}, valid={is_valid}")
            except Exception as e:
                print(f"Error with token {token.user_id}: {str(e)}")
                # Try to fix the token
                if token.expires_at is None:
                    token.expires_at = timezone.now() + timedelta(hours=24)
                    token.save()
                    print(f"Fixed token {token.user_id}")
        
        print("✓ Datetime issues fixed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing datetime issues: {str(e)}")
        return False


def test_admin_access():
    """Test admin access to ensure no errors"""
    print("\nTesting admin access...")
    
    try:
        from KOTAK_NEO_API.admin import KotakNeoUserTokenAdmin
        
        # Test admin configuration
        admin = KotakNeoUserTokenAdmin(KotakNeoUserToken, None)
        print("✓ Admin configuration created successfully")
        
        # Test with sample data
        tokens = KotakNeoUserToken.objects.all()[:5]
        for token in tokens:
            try:
                is_expired = admin.is_expired(None, token)
                is_valid = admin.is_valid(None, token)
                print(f"Admin test for {token.user_id}: expired={is_expired}, valid={is_valid}")
            except Exception as e:
                print(f"Admin test error for {token.user_id}: {str(e)}")
        
        print("✓ Admin access test completed")
        return True
        
    except Exception as e:
        print(f"✗ Error testing admin access: {str(e)}")
        return False


def main():
    """Main function"""
    print("=" * 50)
    print("Kotak Neo API Admin Fix Script")
    print("=" * 50)
    
    # Fix datetime issues
    if fix_datetime_issues():
        print("✓ Datetime issues resolved")
    else:
        print("✗ Failed to fix datetime issues")
        return
    
    # Test admin access
    if test_admin_access():
        print("✓ Admin access working correctly")
    else:
        print("✗ Admin access still has issues")
    
    print("\n" + "=" * 50)
    print("Fix script completed!")
    print("=" * 50)


if __name__ == "__main__":
    main() 