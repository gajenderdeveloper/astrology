#!/usr/bin/env python3
"""
Simple example script showing how to use the ZERODHA_API order placement functions
"""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.cron import zerodha_place_specific_order, zerodha_place_order_example
from astrology.ZERODHA_API.zerodha_integration import ZerodhaAPI


def example_1_basic_market_order():
    """Example 1: Place a basic market order"""
    print("=== Example 1: Basic Market Order ===")
    
    try:
        # Place a market buy order for NIFTY options
        order_id = zerodha_place_specific_order(
            symbol="NIFTY24JUN22000CE",  # Replace with actual symbol
            transaction_type="BUY",
            quantity=50,  # Lot size for NIFTY options
            order_type="MARKET"
        )
        print(f"✅ Market order placed successfully! Order ID: {order_id}")
    except Exception as e:
        print(f"❌ Error placing market order: {str(e)}")


def example_2_limit_order():
    """Example 2: Place a limit order"""
    print("\n=== Example 2: Limit Order ===")
    
    try:
        # Place a limit buy order for BANKNIFTY options
        order_id = zerodha_place_specific_order(
            symbol="BANKNIFTY24JUN48000CE",  # Replace with actual symbol
            transaction_type="BUY",
            quantity=15,  # Lot size for BANKNIFTY options
            order_type="LIMIT",
            price=150.50  # Limit price
        )
        print(f"✅ Limit order placed successfully! Order ID: {order_id}")
    except Exception as e:
        print(f"❌ Error placing limit order: {str(e)}")


def example_3_stop_loss_order():
    """Example 3: Place a stop loss order"""
    print("\n=== Example 3: Stop Loss Order ===")
    
    try:
        # Place a stop loss sell order for equity
        order_id = zerodha_place_specific_order(
            symbol="RELIANCE",
            transaction_type="SELL",
            quantity=100,
            order_type="SL",
            price=2400.00,  # Stop loss price
            trigger_price=2450.00  # Trigger price
        )
        print(f"✅ Stop loss order placed successfully! Order ID: {order_id}")
    except Exception as e:
        print(f"❌ Error placing stop loss order: {str(e)}")


def example_4_get_account_info():
    """Example 4: Get account information"""
    print("\n=== Example 4: Account Information ===")
    
    try:
        zerodha = ZerodhaAPI()
        
        # Get user profile
        profile = zerodha.get_profile()
        print(f"👤 User: {profile.get('user_name', 'Unknown')}")
        
        # Get account margins
        margins = zerodha.get_margins()
        available_cash = margins['equity']['available']['cash']
        print(f"💰 Available cash: ₹{available_cash:,.2f}")
        
        # Get current positions
        positions = zerodha.get_positions()
        print(f"📊 Current positions: {len(positions.get('net', []))} positions")
        
    except Exception as e:
        print(f"❌ Error getting account info: {str(e)}")


def example_5_search_instruments():
    """Example 5: Search for instruments"""
    print("\n=== Example 5: Search Instruments ===")
    
    try:
        zerodha = ZerodhaAPI()
        
        # Search for NIFTY call options
        instruments = zerodha.search_instruments("NIFTY", exchange="NFO", instrument_type="CE")
        print(f"🔍 Found {len(instruments)} NIFTY call options")
        
        # Display first 5 results
        for i, instrument in enumerate(instruments[:5]):
            print(f"  {i+1}. {instrument['tradingsymbol']} - Strike: {instrument['strike']}")
            
    except Exception as e:
        print(f"❌ Error searching instruments: {str(e)}")


def main():
    """Main function to run examples"""
    print("🚀 ZERODHA API Order Placement Examples")
    print("=" * 50)
    
    # Test connection first
    try:
        zerodha = ZerodhaAPI()
        print("✅ Successfully connected to Zerodha API")
    except Exception as e:
        print(f"❌ Failed to connect to Zerodha API: {str(e)}")
        return
    
    # Run examples (commented out for safety - uncomment to test)
    # WARNING: These will place real orders with real money!
    
    # example_1_basic_market_order()
    # example_2_limit_order()
    # example_3_stop_loss_order()
    
    # Safe examples (no real orders)
    example_4_get_account_info()
    example_5_search_instruments()
    
    print("\n" + "=" * 50)
    print("📝 Note: Order placement examples are commented out for safety.")
    print("   Uncomment them in the code to test real order placement.")
    print("   ⚠️  WARNING: Real orders will be placed with real money!")


if __name__ == "__main__":
    main() 