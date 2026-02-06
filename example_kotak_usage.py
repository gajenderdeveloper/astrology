#!/usr/bin/env python
"""
Example usage of Kotak Neo API in standalone mode
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from KOTAK_NEO_API.kotak_integration_standalone import KotakNeoAPI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Example usage of KotakNeoAPI"""
    print("=" * 60)
    print("Kotak Neo API Standalone Usage Example")
    print("=" * 60)
    
    # Initialize API with your credentials
    api = KotakNeoAPI(
        user_id='your_user_id',
        api_key='your_api_key',
        api_secret='your_api_secret'
    )
    
    print(f"✓ API initialized for user: {api.user_id}")
    print(f"✓ Token status: {api.user_token.status}")
    print(f"✓ Token valid: {api.user_token.is_valid}")
    
    # Example 1: Get market status
    print("\n1. Getting market status...")
    try:
        status = api.get_market_status()
        print(f"✓ Market status: {status}")
    except Exception as e:
        print(f"⚠️  Market status failed: {e}")
    
    # Example 2: Get quotes for instruments
    print("\n2. Getting quotes...")
    try:
        quotes = api.get_quote(['NIFTY', 'BANKNIFTY'])
        print(f"✓ Retrieved quotes for {len(quotes)} instruments")
    except Exception as e:
        print(f"⚠️  Quotes failed: {e}")
    
    # Example 3: Get holdings
    print("\n3. Getting holdings...")
    try:
        holdings = api.get_holdings()
        print(f"✓ Retrieved holdings data")
    except Exception as e:
        print(f"⚠️  Holdings failed: {e}")
    
    # Example 4: Place an order (example)
    print("\n4. Placing order (example)...")
    try:
        order = api.place_order(
            tradingsymbol='NIFTY',
            transaction_type='BUY',
            quantity=1,
            product='NRML',
            order_type='LIMIT',
            price=19500.0
        )
        print(f"✓ Order placed: {order}")
    except Exception as e:
        print(f"⚠️  Order placement failed: {e}")
    
    # Example 5: Get option chain
    print("\n5. Getting option chain...")
    try:
        option_chain = api.get_option_chain('NIFTY')
        print(f"✓ Retrieved option chain data")
    except Exception as e:
        print(f"⚠️  Option chain failed: {e}")
    
    # Example 6: Sync operations
    print("\n6. Sync operations...")
    try:
        api.sync_holdings()
        print("✓ Holdings sync completed")
    except Exception as e:
        print(f"⚠️  Holdings sync failed: {e}")
    
    try:
        api.sync_market_data(['NIFTY', 'BANKNIFTY', 'RELIANCE'])
        print("✓ Market data sync completed")
    except Exception as e:
        print(f"⚠️  Market data sync failed: {e}")
    
    print("\n" + "=" * 60)
    print("✓ Example completed successfully!")
    print("=" * 60)
    
    print("\n📝 Usage Notes:")
    print("- Replace 'your_user_id', 'your_api_key', 'your_api_secret' with your actual credentials")
    print("- The API will make real HTTP requests to Kotak Neo servers")
    print("- All API calls are logged with timestamps and response times")
    print("- The standalone version doesn't require Django or database setup")
    print("- Error handling is built-in for network issues and API errors")


if __name__ == "__main__":
    main() 