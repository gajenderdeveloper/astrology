import os
import sys
import django
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings



# Add the Django project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astrology.settings')
django.setup()

from KOTAK_NEO_API.kotak_integration import KotakNeoAPI
from KOTAK_NEO_API.models import (
    KotakNeoUserToken, KotakNeoInstrument, KotakNeoMarketData,
    KotakNeoHolding, KotakNeoAlert, KotakNeoOptionChain
)

logger = logging.getLogger(__name__)


def sync_kotak_market_data():
    """
    Cron job to sync market data from Kotak Neo API
    Runs every 5 minutes during market hours
    """
    try:
        logger.info("Starting Kotak Neo market data sync")
        
        # Get all active instruments
        instruments = KotakNeoInstrument.objects.filter(is_active=True)
        
        if not instruments.exists():
            logger.warning("No active instruments found for market data sync")
            return
        
        # Get instrument tokens
        instrument_tokens = list(instruments.values_list('instrument_token', flat=True))
        
        # Process in batches of 100
        batch_size = 100
        for i in range(0, len(instrument_tokens), batch_size):
            batch = instrument_tokens[i:i + batch_size]
            
            try:
                # Initialize API
                api = KotakNeoAPI()
                
                # Get quotes for batch
                quotes = api.get_quote(batch)
                
                # Save market data
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
                        logger.warning(f"Instrument {instrument_token} not found")
                    except Exception as e:
                        logger.error(f"Error saving market data for {instrument_token}: {str(e)}")
                
                logger.info(f"Processed batch {i//batch_size + 1} of {(len(instrument_tokens) + batch_size - 1)//batch_size}")
                
            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {str(e)}")
        
        logger.info("Kotak Neo market data sync completed")
        
    except Exception as e:
        logger.error(f"Kotak Neo market data sync failed: {str(e)}")


def sync_kotak_holdings():
    """
    Cron job to sync holdings from Kotak Neo API
    Runs every 30 minutes during market hours
    """
    try:
        logger.info("Starting Kotak Neo holdings sync")
        
        # Get all active user tokens
        user_tokens = KotakNeoUserToken.objects.filter(status='active')
        
        if not user_tokens.exists():
            logger.warning("No active user tokens found for holdings sync")
            return
        
        for user_token in user_tokens:
            try:
                # Initialize API with user token
                api = KotakNeoAPI(user_id=user_token.user_id)
                
                # Sync holdings
                api.sync_holdings()
                
                logger.info(f"Synced holdings for user {user_token.user_id}")
                
            except Exception as e:
                logger.error(f"Error syncing holdings for user {user_token.user_id}: {str(e)}")
        
        logger.info("Kotak Neo holdings sync completed")
        
    except Exception as e:
        logger.error(f"Kotak Neo holdings sync failed: {str(e)}")


def monitor_kotak_alerts():
    """
    Cron job to monitor and trigger alerts
    Runs every 2 minutes during market hours
    """
    try:
        logger.info("Starting Kotak Neo alert monitoring")
        
        # Get all active alerts
        active_alerts = KotakNeoAlert.objects.filter(status='ACTIVE')
        
        if not active_alerts.exists():
            logger.info("No active alerts to monitor")
            return
        
        # Initialize API
        api = KotakNeoAPI()
        
        for alert in active_alerts:
            try:
                # Get current market data for alert instrument
                quotes = api.get_quote([alert.instrument.instrument_token])
                
                if not quotes:
                    continue
                
                quote_data = quotes.get(alert.instrument.instrument_token, {})
                current_value = None
                
                # Get current value based on alert type
                if alert.alert_type == 'PRICE':
                    current_value = quote_data.get('last_price')
                elif alert.alert_type == 'VOLUME':
                    current_value = quote_data.get('volume')
                elif alert.alert_type == 'OI':
                    current_value = quote_data.get('open_interest')
                
                if current_value is None:
                    continue
                
                # Check if alert should be triggered
                should_trigger = False
                
                if alert.condition == 'ABOVE' and current_value > alert.target_value:
                    should_trigger = True
                elif alert.condition == 'BELOW' and current_value < alert.target_value:
                    should_trigger = True
                elif alert.condition == 'EQUALS' and current_value == alert.target_value:
                    should_trigger = True
                elif alert.condition == 'CROSSES_ABOVE':
                    # Get previous value from market data
                    prev_data = KotakNeoMarketData.objects.filter(
                        instrument=alert.instrument
                    ).order_by('-timestamp').first()
                    
                    if prev_data and prev_data.last_price <= alert.target_value and current_value > alert.target_value:
                        should_trigger = True
                elif alert.condition == 'CROSSES_BELOW':
                    # Get previous value from market data
                    prev_data = KotakNeoMarketData.objects.filter(
                        instrument=alert.instrument
                    ).order_by('-timestamp').first()
                    
                    if prev_data and prev_data.last_price >= alert.target_value and current_value < alert.target_value:
                        should_trigger = True
                
                if should_trigger:
                    # Trigger alert
                    alert.status = 'TRIGGERED'
                    alert.triggered_at = timezone.now()
                    alert.triggered_value = current_value
                    alert.save()
                    
                    # Send notification (implement as needed)
                    logger.info(f"Alert triggered: {alert.name} - {alert.instrument.tradingsymbol} "
                              f"{alert.condition} {alert.target_value} (Current: {current_value})")
                    
                    # If not repeatable, mark as expired
                    if not alert.is_repeatable:
                        alert.status = 'EXPIRED'
                        alert.save()
                
            except Exception as e:
                logger.error(f"Error monitoring alert {alert.name}: {str(e)}")
        
        logger.info("Kotak Neo alert monitoring completed")
        
    except Exception as e:
        logger.error(f"Kotak Neo alert monitoring failed: {str(e)}")


def sync_kotak_option_chains():
    """
    Cron job to sync option chain data
    Runs every 15 minutes during market hours
    """
    try:
        logger.info("Starting Kotak Neo option chain sync")
        
        # Get list of symbols to sync (you can customize this)
        symbols_to_sync = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']  # Add more as needed
        
        api = KotakNeoAPI()
        
        for symbol in symbols_to_sync:
            try:
                # Get option chain data
                option_chain_data = api.get_option_chain(symbol)
                
                if not option_chain_data:
                    continue
                
                # Process option chain data
                for option_data in option_chain_data.get('options', []):
                    try:
                        # Create or update option chain record
                        KotakNeoOptionChain.objects.update_or_create(
                            symbol=symbol,
                            expiry_date=option_data.get('expiry_date'),
                            strike_price=option_data.get('strike_price'),
                            option_type=option_data.get('option_type'),
                            defaults={
                                'last_price': option_data.get('last_price'),
                                'change': option_data.get('change'),
                                'change_percentage': option_data.get('change_percentage'),
                                'volume': option_data.get('volume'),
                                'open_interest': option_data.get('open_interest'),
                                'change_in_oi': option_data.get('change_in_oi'),
                                'implied_volatility': option_data.get('implied_volatility'),
                                'delta': option_data.get('delta'),
                                'gamma': option_data.get('gamma'),
                                'theta': option_data.get('theta'),
                                'vega': option_data.get('vega'),
                                'bid_price': option_data.get('bid_price'),
                                'bid_quantity': option_data.get('bid_quantity'),
                                'ask_price': option_data.get('ask_price'),
                                'ask_quantity': option_data.get('ask_quantity'),
                            }
                        )
                        
                    except Exception as e:
                        logger.error(f"Error processing option data for {symbol}: {str(e)}")
                
                logger.info(f"Synced option chain for {symbol}")
                
            except Exception as e:
                logger.error(f"Error syncing option chain for {symbol}: {str(e)}")
        
        logger.info("Kotak Neo option chain sync completed")
        
    except Exception as e:
        logger.error(f"Kotak Neo option chain sync failed: {str(e)}")


def manage_kotak_tokens():
    """
    Cron job to manage and refresh tokens
    Runs every hour
    """
    try:
        logger.info("Starting Kotak Neo token management")
        
        # Get all active tokens
        active_tokens = KotakNeoUserToken.objects.filter(status='active')
        
        for token in active_tokens:
            try:
                # Check if token is expired or about to expire (within 1 hour)
                if token.expires_at is None:
                    logger.warning(f"Token for user {token.user_id} has no expiry date, marking as invalid")
                    token.status = 'invalid'
                    token.save()
                    continue
                
                if token.is_expired or token.expires_at <= timezone.now() + timedelta(hours=1):
                    logger.info(f"Token for user {token.user_id} is expired or expiring soon, attempting refresh")
                    
                    # Try to refresh token
                    api = KotakNeoAPI(user_id=token.user_id)
                    
                    # The API will automatically handle token refresh
                    # If refresh fails, token will be marked as invalid
                    
            except Exception as e:
                logger.error(f"Error managing token for user {token.user_id}: {str(e)}")
        
        # Clean up old invalid tokens (older than 7 days)
        old_tokens = KotakNeoUserToken.objects.filter(
            status='invalid',
            updated_at__lte=timezone.now() - timedelta(days=7)
        )
        
        if old_tokens.exists():
            count = old_tokens.count()
            old_tokens.delete()
            logger.info(f"Cleaned up {count} old invalid tokens")
        
        logger.info("Kotak Neo token management completed")
        
    except Exception as e:
        logger.error(f"Kotak Neo token management failed: {str(e)}")


def cleanup_old_market_data():
    """
    Cron job to cleanup old market data
    Runs daily at 2 AM
    """
    try:
        logger.info("Starting Kotak Neo market data cleanup")
        
        # Keep only last 30 days of market data
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Delete old market data
        old_market_data = KotakNeoMarketData.objects.filter(timestamp__lt=cutoff_date)
        
        if old_market_data.exists():
            count = old_market_data.count()
            old_market_data.delete()
            logger.info(f"Cleaned up {count} old market data records")
        else:
            logger.info("No old market data to cleanup")
        
        # Keep only last 7 days of API logs
        log_cutoff_date = timezone.now() - timedelta(days=7)
        
        from KOTAK_NEO_API.models import KotakNeoAPILog
        old_api_logs = KotakNeoAPILog.objects.filter(created_at__lt=log_cutoff_date)
        
        if old_api_logs.exists():
            count = old_api_logs.count()
            old_api_logs.delete()
            logger.info(f"Cleaned up {count} old API log records")
        else:
            logger.info("No old API logs to cleanup")
        
        logger.info("Kotak Neo market data cleanup completed")
        
    except Exception as e:
        logger.error(f"Kotak Neo market data cleanup failed: {str(e)}")


def sync_kotak_instruments():
    """
    Cron job to sync instruments from Kotak Neo API
    Runs daily at 6 AM
    """
    try:
        logger.info("Starting Kotak Neo instruments sync")
        
        api = KotakNeoAPI()
        
        # Sync instruments for different exchanges
        exchanges = ['NSE', 'NFO', 'BSE']
        
        for exchange in exchanges:
            try:
                instruments_data = api.get_instruments(exchange=exchange)
                
                if not instruments_data:
                    continue
                
                for instrument_data in instruments_data.get('instruments', []):
                    try:
                        # Create or update instrument
                        KotakNeoInstrument.objects.update_or_create(
                            instrument_token=instrument_data.get('instrument_token'),
                            defaults={
                                'tradingsymbol': instrument_data.get('tradingsymbol'),
                                'name': instrument_data.get('name'),
                                'exchange': instrument_data.get('exchange'),
                                'instrument_type': instrument_data.get('instrument_type'),
                                'segment': instrument_data.get('segment'),
                                'expiry': instrument_data.get('expiry'),
                                'strike_price': instrument_data.get('strike_price'),
                                'lot_size': instrument_data.get('lot_size', 1),
                                'tick_size': instrument_data.get('tick_size', 0.05),
                                'is_active': True
                            }
                        )
                        
                    except Exception as e:
                        logger.error(f"Error processing instrument {instrument_data.get('tradingsymbol')}: {str(e)}")
                
                logger.info(f"Synced instruments for exchange {exchange}")
                
            except Exception as e:
                logger.error(f"Error syncing instruments for exchange {exchange}: {str(e)}")
        
        logger.info("Kotak Neo instruments sync completed")
        
    except Exception as e:
        logger.error(f"Kotak Neo instruments sync failed: {str(e)}")


# Market hours check function
def is_market_hours():
    """
    Check if current time is within market hours (9:15 AM to 3:30 PM, Monday to Friday)
    """
    now = timezone.now()
    
    # Check if it's a weekday (Monday = 1, Sunday = 7)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if it's within market hours
    market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return market_start <= now <= market_end


# Wrapper functions for cron jobs with market hours check
def kotak_market_data_sync():
    """Wrapper for market data sync with market hours check"""
    if is_market_hours():
        sync_kotak_market_data()
    else:
        logger.info("Market data sync skipped - outside market hours")


def kotak_holdings_sync():
    """Wrapper for holdings sync with market hours check"""
    if is_market_hours():
        sync_kotak_holdings()
    else:
        logger.info("Holdings sync skipped - outside market hours")


def kotak_alert_monitoring():
    """Wrapper for alert monitoring with market hours check"""
    if is_market_hours():
        monitor_kotak_alerts()
    else:
        logger.info("Alert monitoring skipped - outside market hours")


def kotak_option_chain_sync():
    """Wrapper for option chain sync with market hours check"""
    if is_market_hours():
        sync_kotak_option_chains()
    else:
        logger.info("Option chain sync skipped - outside market hours") 



if __name__ == "__main__":
    # Run all cron jobs for testing
    try:
        api = KotakNeoAPI(user_id='client26349')
        #kotak_market_data_sync()
        # kotak_holdings_sync()
        # kotak_alert_monitoring()
        # kotak_option_chain_sync()
        # manage_kotak_tokens()
        # cleanup_old_market_data()
        # sync_kotak_instruments()
    except Exception as e:
        logger.error(f"Error running cron jobs: {str(e)}")