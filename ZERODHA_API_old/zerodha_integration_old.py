import os
from kiteconnect import KiteConnect
#from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ZERODHA_API_KEY = 'wx9fzilixlw1ihob'
ZERODHA_API_SECRET = 'wpg21j1wmbyh4fpvg5vilx7nrhh2gqf1'
ZERODHA_ACCESS_TOKEN = None

class ZerodhaAPI:
    def __init__(self):
        #load_dotenv()
        self.api_key = ZERODHA_API_KEY
        self.api_secret = ZERODHA_API_SECRET
        self.access_token = ZERODHA_ACCESS_TOKEN    
        self.kite = None
        self.initialize()

    def initialize(self):
        """Initialize the KiteConnect instance"""
        try:
            self.kite = KiteConnect(api_key=self.api_key)
            if self.access_token:
                self.kite.set_access_token(self.access_token)
            logger.info("Zerodha API initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Zerodha API: {str(e)}")
            raise

    def get_login_url(self):
        """Get the login URL for user authentication"""
        try:
            return self.kite.login_url()
        except Exception as e:
            logger.error(f"Error getting login URL: {str(e)}")
            raise

    def generate_session(self, request_token):
        """Generate session using request token"""
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            return data
        except Exception as e:
            logger.error(f"Error generating session: {str(e)}")
            raise

    def get_profile(self):
        """Get user profile information"""
        try:
            return self.kite.profile()
        except Exception as e:
            logger.error(f"Error getting profile: {str(e)}")
            raise

    def get_margins(self):
        """Get account margins"""
        try:
            return self.kite.margins()
        except Exception as e:
            logger.error(f"Error getting margins: {str(e)}")
            raise

    def place_order(self, variety, exchange, tradingsymbol, transaction_type, quantity, product, order_type, price=None):
        """Place an order"""
        try:
            order_params = {
                "variety": variety,
                "exchange": exchange,
                "tradingsymbol": tradingsymbol,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "product": product,
                "order_type": order_type
            }
            if price:
                order_params["price"] = price

            return self.kite.place_order(**order_params)
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            raise

    def get_orders(self):
        """Get all orders"""
        try:
            return self.kite.orders()
        except Exception as e:
            logger.error(f"Error getting orders: {str(e)}")
            raise

    def get_positions(self):
        """Get current positions"""
        try:
            return self.kite.positions()
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            raise

    def get_holdings(self):
        """Get current holdings"""
        try:
            return self.kite.holdings()
        except Exception as e:
            logger.error(f"Error getting holdings: {str(e)}")
            raise

    def get_historical_data(self, instrument_token, from_date, to_date, interval):
        """Get historical data for an instrument"""
        try:
            return self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            raise

# Example usage:
if __name__ == "__main__":
    # Initialize the API
    zerodha = ZerodhaAPI()
    
    # Example: Get user profile
    try:
        profile = zerodha.get_profile()
        print("User Profile:", profile)
    except Exception as e:
        print(f"Error: {str(e)}") 