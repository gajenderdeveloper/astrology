#!/usr/bin/env python3
"""
Test script for ZERODHA API order placement functionality
This script demonstrates how to place different types of orders using the ZERODHA_API
"""

import logging
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astrology.ZERODHA_API.zerodha_integration import ZerodhaAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_zerodha_connection():
    """Test basic connection to Zerodha API"""
    try:
        logger.info("Testing Zerodha API connection...")
        zerodha = ZerodhaAPI()
        
        # Get user profile
        profile = zerodha.get_profile()
        logger.info(f"Successfully connected! User: {profile.get('user_name', 'Unknown')}")
        
        # Get account margins
        margins = zerodha.get_margins()
        logger.info(f"Available cash: {margins['equity']['available']['cash']}")
        
        return zerodha
    except Exception as e:
        logger.error(f"Failed to connect to Zerodha API: {str(e)}")
        return None


def test_market_order(zerodha, symbol="NIFTY24JUN22000CE", quantity=50):
    """Test placing a market order"""
    try:
        logger.info(f"Placing MARKET BUY order for {symbol}")
        
        order_id = zerodha.place_order(
            variety=zerodha.VARIETY_REGULAR,
            exchange=zerodha.EXCHANGE_NFO,
            tradingsymbol=symbol,
            transaction_type="BUY",
            quantity=quantity,
            product="NRML",
            order_type="MARKET"
        )
        
        logger.info(f"Market order placed successfully! Order ID: {order_id}")
        return order_id
    except Exception as e:
        logger.error(f"Failed to place market order: {str(e)}")
        return None


def test_limit_order(zerodha, symbol="BANKNIFTY24JUN48000CE", quantity=15, price=150.50):
    """Test placing a limit order"""
    try:
        logger.info(f"Placing LIMIT BUY order for {symbol} at price {price}")
        
        order_id = zerodha.place_order(
            variety=zerodha.VARIETY_REGULAR,
            exchange=zerodha.EXCHANGE_NFO,
            tradingsymbol=symbol,
            transaction_type="BUY",
            quantity=quantity,
            product="NRML",
            order_type="LIMIT",
            price=price
        )
        
        logger.info(f"Limit order placed successfully! Order ID: {order_id}")
        return order_id
    except Exception as e:
        logger.error(f"Failed to place limit order: {str(e)}")
        return None


def test_stop_loss_order(zerodha, symbol="RELIANCE", quantity=100, price=2400.00, trigger_price=2450.00):
    """Test placing a stop loss order"""
    try:
        logger.info(f"Placing STOP LOSS SELL order for {symbol}")
        
        order_id = zerodha.place_order(
            variety=zerodha.VARIETY_REGULAR,
            exchange=zerodha.EXCHANGE_NSE,
            tradingsymbol=symbol,
            transaction_type="SELL",
            quantity=quantity,
            product="CNC",
            order_type="SL",
            price=price,
            trigger_price=trigger_price
        )
        
        logger.info(f"Stop loss order placed successfully! Order ID: {order_id}")
        return order_id
    except Exception as e:
        logger.error(f"Failed to place stop loss order: {str(e)}")
        return None


def test_get_positions(zerodha):
    """Test getting current positions"""
    try:
        logger.info("Getting current positions...")
        positions = zerodha.get_positions()
        logger.info(f"Current positions: {positions}")
        return positions
    except Exception as e:
        logger.error(f"Failed to get positions: {str(e)}")
        return None


def test_get_orders(zerodha):
    """Test getting order history"""
    try:
        logger.info("Getting order history...")
        orders = zerodha.get_orders()
        logger.info(f"Order history retrieved. Total orders: {len(orders)}")
        return orders
    except Exception as e:
        logger.error(f"Failed to get orders: {str(e)}")
        return None


def test_search_instruments(zerodha, search_term="NIFTY"):
    """Test searching for instruments"""
    try:
        logger.info(f"Searching for instruments with term: {search_term}")
        instruments = zerodha.search_instruments(search_term, exchange="NFO", instrument_type="CE")
        logger.info(f"Found {len(instruments)} instruments")
        
        # Display first few results
        for i, instrument in enumerate(instruments[:5]):
            logger.info(f"{i+1}. {instrument['tradingsymbol']} - {instrument['name']}")
        
        return instruments
    except Exception as e:
        logger.error(f"Failed to search instruments: {str(e)}")
        return None


def main():
    """Main function to run all tests"""
    logger.info("Starting Zerodha API order placement tests...")
    
    # Test connection first
    zerodha = test_zerodha_connection()
    if not zerodha:
        logger.error("Cannot proceed without successful connection")
        return
    
    # Test getting account information
    test_get_positions(zerodha)
    test_get_orders(zerodha)
    
    # Test searching for instruments
    test_search_instruments(zerodha, "NIFTY")
    
    # Test order placement (commented out for safety - uncomment to test)
    # WARNING: These will place real orders with real money!
    
    # test_market_order(zerodha, "NIFTY24JUN22000CE", 50)
    # test_limit_order(zerodha, "BANKNIFTY24JUN48000CE", 15, 150.50)
    # test_stop_loss_order(zerodha, "RELIANCE", 100, 2400.00, 2450.00)
    
    logger.info("All tests completed!")


if __name__ == "__main__":
    main() 