import requests
import json
import time
import logging
from datetime import datetime, timedelta
import django


# Try to import Django components, fall back to standalone mode if not available
try:
    from django.utils import timezone
    from django.conf import settings
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    # Mock timezone for standalone usage
    class MockTimezone:
        def now(self):
            return datetime.now()
    timezone = MockTimezone()
    
    # Mock settings for standalone usage
    class MockSettings:
        KOTAK_NEO_USER_ID = None
        KOTAK_NEO_API_KEY = None
        KOTAK_NEO_API_SECRET = None
    settings = MockSettings()

# Try to import models, fall back to mock if not available
try:
    from KOTAK_NEO_API.models import (
        KotakNeoUserToken, KotakNeoInstrument, KotakNeoOrder,
        KotakNeoMarketData, KotakNeoHolding, KotakNeoAlert,
        KotakNeoOptionChain, KotakNeoAPILog
    )
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    # Create mock classes for standalone usage
    class MockKotakNeoUserToken:
        def __init__(self, user_id, access_token, refresh_token, expires_at, status):
            self.user_id = user_id
            self.access_token = access_token
            self.refresh_token = refresh_token
            self.expires_at = expires_at
            self.status = status
            
        @property
        def is_valid(self):
            if self.expires_at is None:
                return False
            return self.status == 'active' and datetime.now() < self.expires_at
            
        @property
        def is_expired(self):
            if self.expires_at is None:
                return True
            return datetime.now() > self.expires_at
    
    KotakNeoUserToken = MockKotakNeoUserToken
    KotakNeoInstrument = type('MockKotakNeoInstrument', (), {})
    KotakNeoOrder = type('MockKotakNeoOrder', (), {})
    KotakNeoMarketData = type('MockKotakNeoMarketData', (), {})
    KotakNeoHolding = type('MockKotakNeoHolding', (), {})
    KotakNeoAlert = type('MockKotakNeoAlert', (), {})
    KotakNeoOptionChain = type('MockKotakNeoOptionChain', (), {})
    KotakNeoAPILog = type('MockKotakNeoAPILog', (), {})

logger = logging.getLogger(__name__)


class KotakNeoAPI:
    """
    Kotak Neo API integration class with auto-authentication
    """
    
    # API Base URLs
    BASE_URL = "https://tradeapi.kotaksecurities.com"
    API_VERSION = "v1"
    
    # API Endpoints
    ENDPOINTS = {
        'login': '/auth/login',
        'refresh_token': '/auth/refresh',
        'logout': '/auth/logout',
        'profile': '/user/profile',
        'holdings': '/portfolio/holdings',
        'positions': '/portfolio/positions',
        'orders': '/orders',
        'place_order': '/orders/regular',
        'modify_order': '/orders/regular',
        'cancel_order': '/orders/regular',
        'order_history': '/orders/history',
        'instruments': '/instruments',
        'quote': '/market/quotes',
        'historical_data': '/market/history',
        'option_chain': '/market/option-chain',
        'market_status': '/market/status',
    }
    
    def __init__(self, user_id=None, api_key=None, api_secret=None):
        """
        Initialize Kotak Neo API client
        
        Args:
            user_id (str): Kotak Neo user ID
            api_key (str): API key from Kotak Neo
            api_secret (str): API secret from Kotak Neo
        """
        #KOTAK_NEO_USER_ID = 'client26349'
        KOTAK_NEO_API_KEY = 'L3oHgffw2uTUcyIvAiPhvjJlVWUa'
        KOTAK_NEO_API_SECRET = 'VOmGP3ofzWSBzmeAOFSgJXL1SVYa'

        
        #user_id = KOTAK_NEO_USER_ID
        api_key = KOTAK_NEO_API_KEY
        api_secret = KOTAK_NEO_API_SECRET
        self.user_id = user_id or getattr(settings, 'KOTAK_NEO_USER_ID', None)
        self.api_key = api_key or getattr(settings, 'KOTAK_NEO_API_KEY', None)
        self.api_secret = api_secret or getattr(settings, 'KOTAK_NEO_API_SECRET', None)
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'KotakNeoAPI/1.0'
        })
        
        # Initialize user_token as None
        self.user_token = None
        
        # Get or create user token (only if user_id is provided)
        if self.user_id:
            try:
                self.user_token = self._get_user_token()
            except Exception as e:
                logger.warning(f"Failed to get user token: {str(e)}")
                # Create a dummy token for testing purposes
                self.user_token = None
    
    def _get_user_token(self):
        """Get or create user token from database"""
        if not self.user_id:
            raise ValueError("User ID is required")
        
        if not MODELS_AVAILABLE:
            # In standalone mode, create a mock token
            return KotakNeoUserToken(
                user_id=self.user_id,
                access_token='mock_access_token',
                refresh_token='mock_refresh_token',
                expires_at=datetime.now() + timedelta(hours=24),
                status='active'
            )
            
        try:
            token = KotakNeoUserToken.objects.get(user_id=self.user_id)
            
            # Check if token is valid
            if token.is_valid:
                return token
            else:
                # Try to refresh token
                if self._refresh_token(token):
                    return token
                else:
                    # Token refresh failed, need to re-authenticate
                    return self._authenticate()
                    
        except KotakNeoUserToken.DoesNotExist:
            # No token exists, need to authenticate
            return self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Kotak Neo API and create user token"""
        try:
            # This is a placeholder for actual authentication
            # In real implementation, you would use Kotak Neo's authentication flow
            auth_data = {
                'user_id': self.user_id,
                'api_key': self.api_key,
                'api_secret': self.api_secret
            }
            
            response = self._make_request('POST', self.ENDPOINTS['login'], auth_data)
            
            if response.get('status') == 'success':
                token_data = response.get('data', {})
                
                # Ensure expires_at is set
                expires_at = timezone.now() + timedelta(hours=24)  # Adjust based on actual expiry
                
                # Create or update user token
                token, created = KotakNeoUserToken.objects.update_or_create(
                    user_id=self.user_id,
                    defaults={
                        'access_token': token_data.get('access_token'),
                        'refresh_token': token_data.get('refresh_token'),
                        'token_type': token_data.get('token_type', 'Bearer'),
                        'expires_at': expires_at,
                        'status': 'active'
                    }
                )
                
                # Log API call
                self._log_api_call('POST', self.ENDPOINTS['login'], auth_data, response)
                
                return token
            else:
                raise Exception(f"Authentication failed: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise
    
    def _refresh_token(self, token):
        """Refresh the access token using refresh token"""
        try:
            refresh_data = {
                'refresh_token': token.refresh_token
            }
            
            response = self._make_request('POST', self.ENDPOINTS['refresh_token'], refresh_data)
            
            if response.get('status') == 'success':
                token_data = response.get('data', {})
                
                # Ensure expires_at is set
                expires_at = timezone.now() + timedelta(hours=24)  # Adjust based on actual expiry
                
                # Update token
                token.access_token = token_data.get('access_token')
                token.refresh_token = token_data.get('refresh_token', token.refresh_token)
                token.expires_at = expires_at
                token.status = 'active'
                token.save()
                
                # Log API call
                self._log_api_call('POST', self.ENDPOINTS['refresh_token'], refresh_data, response)
                
                return True
            else:
                # Refresh failed, mark token as invalid
                token.status = 'invalid'
                token.save()
                return False
                
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            token.status = 'invalid'
            token.save()
            return False
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request to Kotak Neo API"""
        url = f"{self.BASE_URL}{endpoint}"
        
        # Add authorization header if token exists and is valid
        if self.user_token and hasattr(self.user_token, 'is_valid') and self.user_token.is_valid:
            self.session.headers['Authorization'] = f"{self.user_token.token_type} {self.user_token.access_token}"
        
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time = time.time() - start_time
            
            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {'error': 'Invalid JSON response'}
            
            # Log API call
            self._log_api_call(
                method, endpoint, data or params, response_data,
                status_code=response.status_code,
                response_time=response_time
            )
            
            # Check for authentication errors
            if response.status_code == 401:
                # Token expired, try to refresh
                if self.user_token and self._refresh_token(self.user_token):
                    # Retry the request
                    return self._make_request(method, endpoint, data, params)
                else:
                    # Re-authenticate
                    if self.user_id:
                        self.user_token = self._authenticate()
                        return self._make_request(method, endpoint, data, params)
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            self._log_api_call(
                method, endpoint, data or params, {'error': str(e)},
                log_level='ERROR'
            )
            raise
    
    def _log_api_call(self, method, endpoint, request_data, response_data, 
                     status_code=None, response_time=None, log_level='INFO'):
        """Log API call to database"""
        if not MODELS_AVAILABLE:
            # In standalone mode, just log to console
            logger.info(f"API Call: {method} {endpoint} - Status: {status_code} - Time: {response_time}s")
            return
            
        try:
            KotakNeoAPILog.objects.create(
                user_token=self.user_token,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=timedelta(seconds=response_time) if response_time else None,
                request_data=request_data or {},
                response_data=response_data or {},
                log_level=log_level,
                message=f"{method} {endpoint}"
            )
        except Exception as e:
            logger.error(f"Failed to log API call: {str(e)}")
    
    # Market Data Methods
    
    def get_quote(self, instruments):
        """
        Get quote for instruments
        
        Args:
            instruments (list): List of instrument tokens or symbols
            
        Returns:
            dict: Quote data
        """
        try:
            data = {
                'instruments': instruments
            }
            
            response = self._make_request('POST', self.ENDPOINTS['quote'], data)
            
            if response.get('status') == 'success':
                return response.get('data', {})
            else:
                raise Exception(f"Failed to get quote: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Get quote failed: {str(e)}")
            raise
    
    def get_historical_data(self, instrument_token, from_date, to_date, interval='1D'):
        """
        Get historical data for instrument
        
        Args:
            instrument_token (str): Instrument token
            from_date (str): Start date (YYYY-MM-DD)
            to_date (str): End date (YYYY-MM-DD)
            interval (str): Data interval (1D, 1H, 15M, etc.)
            
        Returns:
            dict: Historical data
        """
        try:
            params = {
                'instrument_token': instrument_token,
                'from_date': from_date,
                'to_date': to_date,
                'interval': interval
            }
            
            response = self._make_request('GET', self.ENDPOINTS['historical_data'], params=params)
            
            if response.get('status') == 'success':
                return response.get('data', {})
            else:
                raise Exception(f"Failed to get historical data: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Get historical data failed: {str(e)}")
            raise
    
    def get_option_chain(self, symbol, expiry_date=None):
        """
        Get option chain for symbol
        
        Args:
            symbol (str): Underlying symbol
            expiry_date (str): Expiry date (YYYY-MM-DD), if None gets all expiries
            
        Returns:
            dict: Option chain data
        """
        try:
            params = {'symbol': symbol}
            if expiry_date:
                params['expiry_date'] = expiry_date
            
            response = self._make_request('GET', self.ENDPOINTS['option_chain'], params=params)
            
            if response.get('status') == 'success':
                return response.get('data', {})
            else:
                raise Exception(f"Failed to get option chain: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Get option chain failed: {str(e)}")
            raise
    
    # Order Management Methods
    
    def place_order(self, tradingsymbol, transaction_type, quantity, product='NRML',
                   order_type='LIMIT', price=None, trigger_price=None, **kwargs):
        """
        Place a new order
        
        Args:
            tradingsymbol (str): Trading symbol
            transaction_type (str): BUY or SELL
            quantity (int): Order quantity
            product (str): Product type (NRML, MIS, CNC)
            order_type (str): Order type (MARKET, LIMIT, SL, SL-M)
            price (float): Order price for limit orders
            trigger_price (float): Trigger price for stop loss orders
            **kwargs: Additional order parameters
            
        Returns:
            dict: Order response
        """
        try:
            order_data = {
                'tradingsymbol': tradingsymbol,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'product': product,
                'order_type': order_type
            }
            
            if price:
                order_data['price'] = price
            if trigger_price:
                order_data['trigger_price'] = trigger_price
            
            # Add additional parameters
            order_data.update(kwargs)
            
            response = self._make_request('POST', self.ENDPOINTS['place_order'], order_data)
            
            if response.get('status') == 'success':
                # Save order to database
                self._save_order(response.get('data', {}), order_data)
                return response.get('data', {})
            else:
                raise Exception(f"Failed to place order: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Place order failed: {str(e)}")
            raise
    
    def modify_order(self, order_id, **kwargs):
        """
        Modify an existing order
        
        Args:
            order_id (str): Order ID to modify
            **kwargs: Parameters to modify
            
        Returns:
            dict: Modification response
        """
        try:
            modify_data = {'order_id': order_id}
            modify_data.update(kwargs)
            
            response = self._make_request('PUT', self.ENDPOINTS['modify_order'], modify_data)
            
            if response.get('status') == 'success':
                return response.get('data', {})
            else:
                raise Exception(f"Failed to modify order: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Modify order failed: {str(e)}")
            raise
    
    def cancel_order(self, order_id):
        """
        Cancel an order
        
        Args:
            order_id (str): Order ID to cancel
            
        Returns:
            dict: Cancellation response
        """
        try:
            cancel_data = {'order_id': order_id}
            
            response = self._make_request('DELETE', self.ENDPOINTS['cancel_order'], cancel_data)
            
            if response.get('status') == 'success':
                return response.get('data', {})
            else:
                raise Exception(f"Failed to cancel order: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Cancel order failed: {str(e)}")
            raise
    
    def get_orders(self, order_id=None, **filters):
        """
        Get orders
        
        Args:
            order_id (str): Specific order ID
            **filters: Additional filters
            
        Returns:
            dict: Orders data
        """
        try:
            params = filters
            if order_id:
                params['order_id'] = order_id
            
            response = self._make_request('GET', self.ENDPOINTS['orders'], params=params)
            
            if response.get('status') == 'success':
                return response.get('data', {})
            else:
                raise Exception(f"Failed to get orders: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Get orders failed: {str(e)}")
            raise
    
    # Portfolio Methods
    
    def get_holdings(self):
        """
        Get user holdings
        
        Returns:
            dict: Holdings data
        """
        try:
            response = self._make_request('GET', self.ENDPOINTS['holdings'])
            
            if response.get('status') == 'success':
                return response.get('data', {})
            else:
                raise Exception(f"Failed to get holdings: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Get holdings failed: {str(e)}")
            raise
    
    def get_positions(self):
        """
        Get user positions
        
        Returns:
            dict: Positions data
        """
        try:
            response = self._make_request('GET', self.ENDPOINTS['positions'])
            
            if response.get('status') == 'success':
                return response.get('data', {})
            else:
                raise Exception(f"Failed to get positions: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Get positions failed: {str(e)}")
            raise
    
    # Instrument Methods
    
    def get_instruments(self, exchange=None, instrument_type=None):
        """
        Get instruments
        
        Args:
            exchange (str): Exchange filter
            instrument_type (str): Instrument type filter
            
        Returns:
            dict: Instruments data
        """
        try:
            params = {}
            if exchange:
                params['exchange'] = exchange
            if instrument_type:
                params['instrument_type'] = instrument_type
            
            response = self._make_request('GET', self.ENDPOINTS['instruments'], params=params)
            
            if response.get('status') == 'success':
                return response.get('data', {})
            else:
                raise Exception(f"Failed to get instruments: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Get instruments failed: {str(e)}")
            raise
    
    # Utility Methods
    
    def get_market_status(self):
        """
        Get market status
        
        Returns:
            dict: Market status data
        """
        try:
            response = self._make_request('GET', self.ENDPOINTS['market_status'])
            
            if response.get('status') == 'success':
                return response.get('data', {})
            else:
                raise Exception(f"Failed to get market status: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Get market status failed: {str(e)}")
            raise
    
    def logout(self):
        """Logout and invalidate token"""
        try:
            response = self._make_request('POST', self.ENDPOINTS['logout'])
            
            if response.get('status') == 'success':
                # Mark token as invalid
                if self.user_token:
                    self.user_token.status = 'invalid'
                    self.user_token.save()
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return False
    
    # Database Helper Methods
    
    def _save_order(self, order_response, order_data):
        """Save order to database"""
        if not MODELS_AVAILABLE:
            # In standalone mode, just log the order
            logger.info(f"Order placed: {order_response.get('order_id')} - {order_data['tradingsymbol']}")
            return
            
        try:
            # Get or create instrument
            instrument, _ = KotakNeoInstrument.objects.get_or_create(
                tradingsymbol=order_data['tradingsymbol'],
                defaults={
                    'instrument_token': order_response.get('instrument_token', ''),
                    'name': order_data['tradingsymbol'],
                    'exchange': order_response.get('exchange', 'NSE'),
                    'instrument_type': 'EQ'  # Default, adjust as needed
                }
            )
            
            # Create order record
            KotakNeoOrder.objects.create(
                order_id=order_response.get('order_id'),
                user_token=self.user_token,
                instrument=instrument,
                transaction_type=order_data['transaction_type'],
                quantity=order_data['quantity'],
                product=order_data['product'],
                order_type=order_data['order_type'],
                price=order_data.get('price'),
                trigger_price=order_data.get('trigger_price'),
                order_timestamp=timezone.now(),
                response_data=order_response
            )
            
        except Exception as e:
            logger.error(f"Failed to save order to database: {str(e)}")
    
    def sync_holdings(self):
        """Sync holdings from API to database"""
        if not MODELS_AVAILABLE:
            # In standalone mode, just log the sync attempt
            logger.info("Holdings sync attempted in standalone mode")
            return
            
        try:
            holdings_data = self.get_holdings()
            
            for holding in holdings_data.get('holdings', []):
                # Get or create instrument
                instrument, _ = KotakNeoInstrument.objects.get_or_create(
                    tradingsymbol=holding.get('tradingsymbol'),
                    defaults={
                        'instrument_token': holding.get('instrument_token', ''),
                        'name': holding.get('tradingsymbol'),
                        'exchange': holding.get('exchange', 'NSE'),
                        'instrument_type': 'EQ'
                    }
                )
                
                # Update or create holding
                KotakNeoHolding.objects.update_or_create(
                    user_token=self.user_token,
                    instrument=instrument,
                    product=holding.get('product', 'NRML'),
                    defaults={
                        'quantity': holding.get('quantity', 0),
                        'average_price': holding.get('average_price', 0),
                        'last_price': holding.get('last_price'),
                        'market_value': holding.get('market_value'),
                        'pnl': holding.get('pnl'),
                        'pnl_percentage': holding.get('pnl_percentage'),
                        'exchange': holding.get('exchange', 'NSE')
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to sync holdings: {str(e)}")
            raise
    
    def sync_market_data(self, instruments):
        """Sync market data for instruments"""
        if not MODELS_AVAILABLE:
            # In standalone mode, just log the sync attempt
            logger.info(f"Market data sync attempted for {len(instruments)} instruments in standalone mode")
            return
            
        try:
            quotes = self.get_quote(instruments)
            
            for instrument_token, quote_data in quotes.items():
                try:
                    instrument = KotakNeoInstrument.objects.get(instrument_token=instrument_token)
                    
                    KotakNeoMarketData.objects.create(
                        instrument=instrument,
                        last_price=quote_data.get('last_price'),
                        change=quote_data.get('change'),
                        change_percentage=quote_data.get('change_percentage'),
                        volume=quote_data.get('volume'),
                        open_interest=quote_data.get('open_interest'),
                        implied_volatility=quote_data.get('implied_volatility'),
                        raw_data=quote_data
                    )
                    
                except KotakNeoInstrument.DoesNotExist:
                    logger.warning(f"Instrument {instrument_token} not found in database")
                    
        except Exception as e:
            logger.error(f"Failed to sync market data: {str(e)}")
            raise 


# Example usage
if __name__ == "__main__":
    # Test the standalone API
    api = KotakNeoAPI()
    print(f"API initialized with user: {api.user_id}")
    print(f"Token valid: {api.user_token.is_valid}")
    
    # Test market status (will fail due to no real API, but won't crash)
    try:
        status = api.get_market_status()
        print(f"Market status: {status}")
    except Exception as e:
        print(f"Market status failed (expected): {e}")
    
    print("Standalone KotakNeoAPI is working!") 