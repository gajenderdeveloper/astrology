import os
from kiteconnect import KiteConnect
import logging
import webbrowser
import json
from datetime import datetime, timedelta
import pandas as pd


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# API credentials - NEVER commit these to version control in production
ZERODHA_API_KEY = 'wx9fzilixlw1ihob'
ZERODHA_API_SECRET = 'wpg21j1wmbyh4fpvg5vilx7nrhh2gqf1'

# Token storage file
#TOKEN_FILE = 'zerodha_token.json'
# Join TOKEN_FILE with base directory path
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'astrology/' 'zerodha_token.json')

file_csv = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'astrology/' 'zerodha_prev_option_chain.csv')



class ZerodhaAPI:
    def __init__(self, request=None):
        self.api_key = ZERODHA_API_KEY
        self.api_secret = ZERODHA_API_SECRET
       
        #self.request = request
        self.access_token = self._get_token()
        self.kite = KiteConnect(api_key=self.api_key)
        logger.info("Zerodha API client initialized")
        self.authenticate()

        self.VARIETY_REGULAR = "regular"
        self.EXCHANGE_NSE = "NSE"
        self.EXCHANGE_NFO = "NFO"
        self.ORDER_TYPE_LIMIT = "LIMIT"
        self.VALIDITY_DAY = "DAY"
        self.TRANSACTION_TYPE_BUY = "BUY"
        self.TRANSACTION_TYPE_SELL = "SELL"
        self.PRODUCT_NRML = "NRML"
        self.PRODUCT_MIS = "MIS"
        self.PRODUCT_CNC = "CNC"

    def _get_token(self):
        """Get token from JSON file if it exists and is not expired"""
        logger.info("*********Checking for existing token***********")
        
        try:
            if os.path.exists(os.path.dirname(TOKEN_FILE)):
            
                with open(TOKEN_FILE, 'r') as f:
                    token_data = json.load(f)
                    
                    # Check if token is expired
                    if 'expiry' in token_data:
                        expiry = datetime.fromisoformat(token_data['expiry'])
                        if datetime.now() < expiry:
                            logger.info("Token is still valid")
                            return token_data['access_token']
                        logger.info("Token expired, need to re-authenticate")
                    else:
                        return token_data.get('access_token')
        except Exception as e:
            logger.error(f"Error reading token file: {str(e)}")
        return None

    def _set_token(self, token_data):
        """Set token in JSON file with expiry information"""
        try:
            # Calculate expiry (Zerodha tokens typically expire in 24 hours)
            data = {}
            data['access_token'] = token_data['access_token']
            #expiry = datetime.now() + timedelta(hours=24)
            expiry = datetime.now() + timedelta(hours=23-datetime.now().hour)
            data['expiry'] = expiry.isoformat()
            
            with open(TOKEN_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error writing token file: {str(e)}")
            raise

    def authenticate(self):
        """Complete the authentication flow"""
        try:
            # Step 1: Get login URL and open in browser
            if self.access_token is None:
                login_url = self.kite.login_url()
                print(f"Please visit this URL to login: {login_url}")
                logger.info(f"Opening login URL: {login_url}")
                webbrowser.open(login_url)
                
                # Step 2: Get the request token from the redirect URL
                request_token = input("Enter the request token from the redirect URL: ")
                
                # Step 3: Generate session and set access token
                data = self.kite.generate_session(request_token, api_secret=self.api_secret)
                self.access_token = data["access_token"]
                self._set_token(data)
                self.kite.set_access_token(self.access_token)
            
                logger.info("Authentication successful")
                return data
            else:
                self.kite.set_access_token(self.access_token)
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
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
    def get_quote(self,intruments):
        """Get quote for given instruments"""
        try:
            return self.kite.quote(intruments)
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
    def get_ohlc_data(self,instruments, interval="day", from_date=None, to_date=None):

        if from_date is None:
            from_date = datetime.now() - timedelta(days=30)
        if to_date is None:
            to_date = datetime.now()

        if isinstance(from_date, str):
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
        if isinstance(to_date, str):
            to_date = datetime.strptime(to_date, '%Y-%m-%d')

        all_data = []

        for trading_symbol,instrument_token in instruments.items():
            try:
                # Fetch historical data
                data = self.kite.historical_data(
                    instrument_token=instrument_token,
                    from_date=from_date,
                    to_date=to_date,
                    interval=interval,
                    continuous=False,
                    oi=False
                )

                # Convert to DataFrame and add trading symbol
                df = pd.DataFrame(data)
                df['trading_symbol'] = trading_symbol

                # Add instrument token if needed
                df['instrument_token'] = instrument_token

                all_data.append(df)

            except Exception as e:
                print(f"Error fetching data for {trading_symbol} ({instrument_token}): {e}")

        if not all_data:
            return pd.DataFrame()

        # Combine all DataFrames
        combined_df = pd.concat(all_data, ignore_index=True)

        # Reorder columns
        columns = ['trading_symbol', 'instrument_token', 'date', 'open', 'high', 'low', 'close', 'volume']
        columns = [col for col in columns if col in combined_df.columns]

        return combined_df[columns]
    def get_instruments(self, exchange=None):
        try:
            if exchange:
                instruments = self.kite.instruments(exchange)
            else: 
                instruments = self.kite.instruments()
            instruments_df = pd.DataFrame(instruments)
            return instruments_df
        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            raise  

    def get_instrument_token_by_symbol(self, symbol, exchange=None):
        """
        Get instrument token by symbol name
        
        Args:
            symbol (str): The trading symbol to search for (e.g., 'RELIANCE', 'INFY')
            exchange (str, optional): Specific exchange to search in (e.g., 'NSE', 'BSE')
        
        Returns:
            dict: Instrument details including token, or None if not found
        """
        try:
            instruments = self.kite.instruments(exchange=exchange)
            
            # Search for the symbol (case-insensitive)
            symbol_upper = symbol.upper()
            for instrument in instruments:
                if instrument['tradingsymbol'].upper() == symbol_upper:
                    return {
                        'instrument_token': instrument['instrument_token'],
                        'tradingsymbol': instrument['tradingsymbol'],
                        'exchange': instrument['exchange'],
                        'name': instrument['name'],
                        'instrument_type': instrument['instrument_type'],
                        'segment': instrument['segment'],
                        'expiry': instrument['expiry'],
                        'strike': instrument['strike'],
                        'lot_size': instrument['lot_size']
                    }
            
            logger.warning(f"Instrument with symbol '{symbol}' not found")
            return None
            
        except Exception as e:
            logger.error(f"Error getting instrument token by symbol: {str(e)}")
            raise

    def search_instruments(self, search_term, exchange=None, instrument_type=None):
        """
        Search for instruments by partial symbol or name match
        
        Args:
            search_term (str): Partial search term
            exchange (str, optional): Specific exchange to search in
            instrument_type (str, optional): Filter by instrument type (EQ, FUT, OPT, etc.)
        
        Returns:
            list: List of matching instruments
        """
        try:
            instruments = self.kite.instruments(exchange=exchange)
            search_term_upper = search_term.upper()
            matches = []
            
            for instrument in instruments:
                # Check if instrument type filter is applied
                if instrument_type and instrument['instrument_type'] != instrument_type:
                    continue
                
                # Check if search term matches symbol or name
                if (search_term_upper in instrument['tradingsymbol'].upper() or 
                    search_term_upper in instrument['name'].upper()):
                    matches.append({
                        'instrument_token': instrument['instrument_token'],
                        'tradingsymbol': instrument['tradingsymbol'],
                        'exchange': instrument['exchange'],
                        'name': instrument['name'],
                        'instrument_type': instrument['instrument_type'],
                        'segment': instrument['segment'],
                        'expiry': instrument['expiry'],
                        'strike': instrument['strike'],
                        'lot_size': instrument['lot_size']
                    })
            
            return matches
            
        except Exception as e:
            logger.error(f"Error searching instruments: {str(e)}")
            raise

    def get_all_strikes_with_ltp_and_oi(self,symbol, exchange="NFO", expiry_date="2025-06-26"):

        try:
            # Get all instruments for the exchange

            instruments = self.kite.instruments(exchange)

            # get oi from previous instruments
            prev_instrument_df = pd.read_csv(file_csv)
            prev_instrument_df = prev_instrument_df[(prev_instrument_df['expiry'] == expiry_date) &
                                                    (prev_instrument_df['name'] == symbol)]

            # Filter instruments for the specific symbol and option type (CE/PE)
            filtered = [
                inst for inst in instruments
                if inst["name"] == symbol and
                inst["instrument_type"] in ["CE", "PE"] 
            
            ]

            # Convert to DataFrame
            filtered_df = pd.DataFrame(filtered)
            filtered_df['expiry'] = filtered_df['expiry'].astype(str)
            unique_expiry = filtered_df['expiry'].dropna().unique()
            # filter by expiry date
            filtered_df = filtered_df[filtered_df['expiry'] == expiry_date]


            filtered_df.sort_values(by=['strike'], inplace=True)
            filtered_df = pd.merge(
                                filtered_df,
                                prev_instrument_df[['strike', 'instrument_type', 'prev_oi']],
                                on=['strike', 'instrument_type'],
                                how='left',
                                suffixes=('', '_prev')
                            )
            filtered_df['prev_oi'] = filtered_df['prev_oi'].fillna(0)

            # Get trading symbols for LTP and OI query
            trading_symbols = filtered_df['tradingsymbol'].tolist()

            # Get LTP data
            ltp_data = self.kite.ltp([f"{exchange}:{symbol}" for symbol in trading_symbols])

            # Get quote data (for OI and volume)
            quote_data = self.kite.quote([f"{exchange}:{symbol}" for symbol in trading_symbols])

            # Extract LTP values and add to DataFrame
            filtered_df['ltp'] = filtered_df['tradingsymbol'].apply(
                lambda x: ltp_data.get(f"{exchange}:{x}", {}).get('last_price', None)
            )

            filtered_df['day_low'] = filtered_df['tradingsymbol'].apply(
                lambda x: quote_data[f"{exchange}:{x}"]["ohlc"]["low"])

            filtered_df['day_high'] = filtered_df['tradingsymbol'].apply(
                lambda x: quote_data[f"{exchange}:{x}"]["ohlc"]["high"])

            filtered_df['prev_close'] = filtered_df['tradingsymbol'].apply(
                lambda x: quote_data[f"{exchange}:{x}"]["ohlc"]["close"])

            # Extract OI values and add to DataFrame (normalized by lot size)
            filtered_df['oi'] = filtered_df['tradingsymbol'].apply(
                lambda x: quote_data.get(f"{exchange}:{x}", {}).get('oi', None))
            filtered_df['oi'] = (filtered_df['oi'] / filtered_df['lot_size']).astype(int)
            filtered_df['change_in_oi'] = filtered_df['oi'] - filtered_df['prev_oi']

            # Extract volume values and add to DataFrame (normalized by lot size)
            filtered_df['volume'] = filtered_df['tradingsymbol'].apply(
                lambda x: quote_data.get(f"{exchange}:{x}", {}).get('volume', None))
            filtered_df['volume'] = (filtered_df['volume'] / filtered_df['lot_size']).astype(int)

            # Pivot the table to get one row per strike with CE and PE columns
            pivot_df = filtered_df.pivot(
                index='strike',
                columns='instrument_type',
                values=['day_low','day_high','ltp', 'oi', 'prev_oi','change_in_oi','volume','tradingsymbol','instrument_token','lot_size']
            )

            # Flatten the multi-level columns
            pivot_df.columns = [f"{col[1]}_{col[0]}" for col in pivot_df.columns]

            # Reset index to make strike a column again
            pivot_df.reset_index(inplace=True)
            pivot_df = pivot_df.fillna(0)

            return {
                'df' : pivot_df,
                'unique_expiry':unique_expiry
            }
        except Exception as e:
            logger.error(f"Error get_all_strikes_with_ltp_and_oi: {str(e)}")
            return {
                
                'error': str(e)
            }
        
        
    

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# print(f"Script directory: {SCRIPT_DIR}")
if __name__ == "__main__":
    # Initialize the API (standalone mode)
    Zerodha = ZerodhaAPI()
    
    # First authenticate
    try:
        #zerodha.authenticate()
        
        strike_df = Zerodha.get_all_strikes_with_ltp_and_oi("MARUTI",expiry_date="2025-07-31")
        
        print(strike_df)
        
    except Exception as e:
        print(f"Error: {str(e)}")