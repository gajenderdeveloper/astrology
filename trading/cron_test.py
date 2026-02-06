import os
import sys
import django
from django.conf import settings

# Add the Django project root to the Python path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astrology.settings')
django.setup()

import logging
from django.utils import timezone
#from .models import CronJob, CronJobExecution

import pandas as pd 
import numpy as np  
import talib
#import pandas_ta as ta
import time 
from time import sleep
from datetime import datetime, timedelta
# Configure logging 
logger = logging.getLogger(__name__)
from trading.utils import *
from trading.strategy import *
from trading.indicator import *
from ZERODHA_API.zerodha_integration import ZerodhaAPI
from trading.models import Change_IN_OI_Increasing,ScaningStockOI,Orders,Scanner_ema

from concurrent.futures import ThreadPoolExecutor
from asyncio import create_task, sleep

PROJECT_PATH = os.path.dirname(settings.BASE_DIR)
instrument_file = os.path.join(PROJECT_PATH,'astrology','DATA','instruments.csv')
instruments_df = pd.read_csv(instrument_file)

symbol_list_df = pd.read_csv(os.path.join(PROJECT_PATH,'astrology','DATA','symbol_list.csv'))
   
Zerodha = ZerodhaAPI()
def find_rsi_divergence(data,  lookback=5):
    # Calculate RSI
    
    if len(data) < lookback + 1:
        logger.warning("Data length is less than lookback period, cannot calculate divergence")
        return None
    
    # Initialize divergence columns
    data['regular_bullish_div'] = 0
    data['regular_bearish_div'] = 0
    data['hidden_bullish_div'] = 0
    data['hidden_bearish_div'] = 0
    
    for i in range(lookback, len(data)):
        # Get recent price and RSI data
        prices = data['close'].iloc[i-lookback:i+1]
        rsis = data['RSI'].iloc[i-lookback:i+1]
        
        # Find peaks and troughs in price and RSI
        price_peaks = prices[(prices.shift(1) < prices) & (prices.shift(-1) < prices)]
        price_troughs = prices[(prices.shift(1) > prices) & (prices.shift(-1) > prices)]
        rsi_peaks = rsis[(rsis.shift(1) < rsis) & (rsis.shift(-1) < rsis)]
        rsi_troughs = rsis[(rsis.shift(1) > rsis) & (rsis.shift(-1) > rsis)]
        
        # Regular Bullish Divergence (Price makes lower low, RSI makes higher low)
        if len(price_troughs) >= 2 and len(rsi_troughs) >= 2:
            if (price_troughs[-1] < price_troughs[-2]) and (rsi_troughs[-1] > rsi_troughs[-2]):
                data.at[data.index[i], 'regular_bullish_div'] = 1
        
        # Regular Bearish Divergence (Price makes higher high, RSI makes lower high)
        if len(price_peaks) >= 2 and len(rsi_peaks) >= 2:
            if (price_peaks[-1] > price_peaks[-2]) and (rsi_peaks[-1] < rsi_peaks[-2]):
                data.at[data.index[i], 'regular_bearish_div'] = 1
                
        # Hidden Bullish Divergence (Price makes higher low, RSI makes lower low)
        if len(price_troughs) >= 2 and len(rsi_troughs) >= 2:
            if (price_troughs[-1] > price_troughs[-2]) and (rsi_troughs[-1] < rsi_troughs[-2]):
                data.at[data.index[i], 'hidden_bullish_div'] = 1
                
        # Hidden Bearish Divergence (Price makes lower high, RSI makes higher high)
        if len(price_peaks) >= 2 and len(rsi_peaks) >= 2:
            if (price_peaks[-1] < price_peaks[-2]) and (rsi_peaks[-1] > rsi_peaks[-2]):
                data.at[data.index[i], 'hidden_bearish_div'] = 1
                
    return data

def detect_divergence(df):
    """
    Detect divergence in the given DataFrame.
    This is a placeholder function; implement your logic here.
    """
    # Example logic: Check if the last two rows have different trends
    # Initialize lists to store price and RSI values
    logger.info("Detecting divergence in DataFrame")
    # Filter for RSI greater than 30
    df = df.copy()
    
    df['divergence'] = np.nan  # Initialize a new column for divergence
    df_diversion = pd.DataFrame()      
    for i ,data in df.iterrows():
        df_diversion = pd.concat([df_diversion, pd.DataFrame({
                'date': [data['date']],
                'open': [data['open']],
                'high': [data['high']], 
                'low': [data['low']],
                'close': [data['close']],
                'ema_200': [data['ema_200']],
                'RSI': [data['RSI']]
            })])
        if df_diversion['RSI'].iloc[-1] > df_diversion['RSI'].iloc[-2] < df_diversion['RSI'].iloc[-3]:
            pass
        
    
    return df
        
    
    
    
    # if len(df) < 3:
    #     logger.warning("DataFrame has less than 2 rows, cannot detect divergence")
    #     return df   
    # print("Detecting divergence in DataFrame")
    # if df['RSI'].iloc[-1] > df['RSI'].iloc[-2] < df['RSI'].iloc[-3]:
        
    #     df['divergence'].iloc[-2] = 'low'
    #     logger.info("Bullish Divergence detected")
    #     return df
    
    
   

def scanner_200ema_background(ohlc_df:pd.DataFrame, tradingsymbol:str):
    """
    Background task to calculate 200 EMA for a given DataFrame and symbol.
    """
    try :
        ohlc_df['date'] = pd.to_datetime(ohlc_df['date'])
        ohlc_df.set_index('date', inplace=True)

        df_5min = ohlc_df.resample('5T').agg({
                            'open': 'first',
                            'high': 'max',
                            'low': 'min',
                            'close': 'last',
                            'volume': 'sum'
                        }).dropna()
        # resample to 3 minutes
        df_5min['ema_200'] = talib.EMA(df_5min['close'], timeperiod=200)
        df_5min['RSI'] = talib.RSI(df_5min['close'], timeperiod=14)
        ohlc_df = df_5min

        #resample to day
        df_daily = ohlc_df.resample('1D').agg({
                        'open': 'first',      # First open price in the period
                        'high': 'max',        # Maximum high price in the period
                        'low': 'min',         # Minimum low price in the period
                        'close': 'last',      # Last close price in the period
                        'volume': 'sum'       # Sum of volume in the period (if you have volume)
                    }).dropna()
        df_daily['RSI'] = talib.RSI(df_daily['close'], timeperiod=14)


        
        
        ohlc_df['ema_200'] = talib.EMA(ohlc_df['close'], timeperiod=200)
        #ohlc_df['date'] = ohlc_df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        ohlc_df['RSI'] = talib.RSI(ohlc_df['close'], timeperiod=14)
        # Filter for today's data only
        # today = pd.Timestamp.now().date()
        # ohlc_df = ohlc_df[ohlc_df.index.date == today]


        today = pd.Timestamp.now().date()
        yesturday = today-timedelta(days=1)
        ohlc_df = ohlc_df[ohlc_df.index.date >= today]
        df_daily = df_daily[df_daily.index.date >= today]

        df2 = pd.DataFrame()            
        for i,data in ohlc_df.iterrows():
            df2 = pd.concat([df2, pd.DataFrame({
                'date': [i],
                'open': [data['open']],
                'high': [data['high']], 
                'low': [data['low']],
                'close': [data['close']],
                'ema_200': [data['ema_200']],
                'RSI': [data['RSI']]
            })])
            if len(df2) > 1:
                
                #if (df2['close'].iloc[-1] > df2['ema_200'].iloc[-1]) and (df2['close'].iloc[-2] < df2['ema_200'].iloc[-2]):

                #if (df2['ema_200'].iloc[-1] < df2['close'].iloc[-1])  and (df2['RSI'].iloc[-1] < 30):

                if (df2['RSI'].iloc[-1] < 30) and (df_daily['RSI'].iloc[-1] > 60):
                    
                
                    # logger.info(f"find 200ma crose for symbol {tradingsymbol}: {df2.tail(5)}")
                    # logger.info(f"Daily {tradingsymbol}: {df_daily.tail(5)}")

                    # if len(df2) > 3:
                    #     df_diversion = detect_divergence(df2)
                        
                    # if df_diversion is not None:
                    #     logger.info(f"diversion {tradingsymbol}: {df_diversion.tail(5)}")

                    Scanner_ema.objects.create(
                        symbol=tradingsymbol,
                        open=df2['open'].iloc[-1],
                        high=df2['high'].iloc[-1],
                        low=df2['low'].iloc[-1],
                        close=df2['close'].iloc[-1],
                        ema=df2['ema_200'].iloc[-1],
                        ema_type='ema_200_30',
                        date=df2['date'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S')
                    )  

                    logger.info(f"EMA saved for {tradingsymbol} : {df2['ema_200'].iloc[-1]} and date {df2['date'].iloc[-1]}")
        print("===")
    except Exception as e:
        logger.error("Error  job: %s", str(e), exc_info=True)
        raise



def scanner_200ma():
    executor = ThreadPoolExecutor(max_workers=4)

    
    exchange = "NSE"
    expiry_date = settings.EXPIRY
    start_time = datetime.now()
    logger.info("**************************Starting scanner_200ma job at %s", start_time)


    try :
        filtered_instrument = instruments_df[
                        (instruments_df['exchange'] == exchange) &
                        (instruments_df['instrument_type'] == 'EQ') &
                        (instruments_df['segment'] == 'NSE')
                        ]
        #print(filtered_instrument.head(10))
        # Filter tradingsymbols that exist in symbol_list_df
        symbol_list = symbol_list_df['symbol'].tolist()
        filtered_instrument = filtered_instrument[filtered_instrument['tradingsymbol'].isin(symbol_list)]
        filtered_instrument.sort_values(by='name', inplace=True)

        #### for exchange NFO-FUT########
        # filtered_instrument = instruments_df[
        #                 (instruments_df['exchange'] == 'NFO') &
        #                 (instruments_df['segment'] == 'NFO-FUT') &
        #                 (instruments_df['expiry'] == expiry_date) 
        #                 ]
        # symbol_list = filtered_instrument['name'].unique()
        # symbol_list = symbol_list.tolist()
        # filtered_instrument = filtered_instrument[filtered_instrument['name'].isin(symbol_list)]


        
        to_date = datetime.now()
        #from_date = to_date - timedelta(days=310) # for interval day
        from_date = to_date - timedelta(days=60) # for max day 60 for 1 min
        #from_date = to_date - timedelta(days=50) 
        interval = 'minute'  #minute,60minute
        scanner_symbol = []
        #filtered_instrument = filtered_instrument.head(5)
        for index,row in filtered_instrument.iterrows():
            tradingsymbol = row['tradingsymbol']
            #if tradingsymbol != ''
            name = row['name']
            # if tradingsymbol !='ULTRACEMCO':
            #     continue
            instrument_token = row['instrument_token']
            try:
                
                historical_data = Zerodha.kite.historical_data(
                            instrument_token=instrument_token,
                            from_date=from_date,
                            to_date=to_date,
                            interval=interval,
                            continuous=False,
                            oi=False
                        )
                
                ohlc_df = pd.DataFrame(historical_data)
                logger.info("%s*************Start background time %s",tradingsymbol, datetime.now())
                executor.submit(scanner_200ema_background, ohlc_df, tradingsymbol)
                logger.info("*************End background time %s", datetime.now())
                
                
            except Exception as e:
                logger.error("Error  job: %s", str(e), exc_info=True)
                raise
        #print(scanner_symbol)
        logger.info("**************************start_time: %s", start_time)
        logger.info("**************************End time %s", datetime.now())
        
    except Exception as e:
        logger.error("Error  job: %s", str(e), exc_info=True)
        raise
    
def background_task(data):
# Your long-running task here
    import time
    time.sleep(5)
    print("Task completed with data:", data)


def zerodha_place_order():
    """
    Function to place order
    """
    try:
        start_time = datetime.now()
        logger.info("Starting zerodha_place_order job at %s", start_time)
        Zerodha = ZerodhaAPI()
        # df = instrumners[instrumners['tradingsymbol'] == 'HAL']
        # token = df[(df.tradingsymbol == "HAL") & (df.exchange == "NSE")].instrument_token.values[0]
        

        orders = Orders.objects.filter(status='PENDING')
        # orders get the instrument token from orders and place the order
        symbol_df =  pd.DataFrame.from_records(orders.values())

        if symbol_df.empty:
            logger.info("No pending orders found")
            OrdersDetailsExit(Zerodha)
            return

        exchange_nfo = 'NFO'
        trading_symbols = symbol_df['symbol'].tolist()
        parent_symbols = symbol_df['parent_symbol'].tolist()
        ltp_data_nfo = Zerodha.kite.ltp([f"{exchange_nfo}:{symbol}" for symbol in trading_symbols])

        exchange_nse = 'NSE'
        ltp_data_nse = Zerodha.kite.ltp([f"{exchange_nse}:{symbol}" for symbol in trading_symbols])
        ltp_data = Zerodha.kite.ltp([f"{exchange_nse}:{symbol}" for symbol in parent_symbols])

        symbol_and_token = {}
        for index,row in symbol_df.iterrows():
            if row['use_parent_symbol'] == '1':
                tradingsymbol = row['parent_symbol']
                instrument_token = row['parent_token']
            else:
                tradingsymbol = row['symbol']
                instrument_token = row['instrument_token']

            symbol_and_token[tradingsymbol] = instrument_token
        print(symbol_and_token)

        ohlc_df = Zerodha.get_ohlc_data(symbol_and_token,interval='minute')

        #for ATH Stetegy
        ath_df = symbol_df[symbol_df['strategy'].isin(['ATH','ATL'])]
        # Filter OHLC data for ATH strategy symbols
        
        ath_symbols = ath_df['parent_symbol'].tolist()

        ath_ohlc_df = ohlc_df[ohlc_df['trading_symbol'].isin(ath_symbols)]
        #logger.info(f"ATH strategy OHLC data: {ath_ohlc_df}")
        
        result = ATH_Strategy(Zerodha,ath_ohlc_df,ath_df,ltp_data_nfo,ltp_data_nse,ltp_data)

        # for index,row in symbol_df.iterrows():
        #     if row['strategy'] == 'ATH':
        #         #ath_strategy()
        #         order_df = ohlc_df[ohlc_df['trading_symbol'] == row['symbol']]
        #         print(order_df)

        OrdersDetailsExit(Zerodha)
    except Exception as e:
        logger.error("Error in zerodha_place_order job: %s", str(e), exc_info=True)
        raise

def OrdersDetailUpdate(Zerodha=None):
    """
    Function to update order details
    """
    try:
        start_time = datetime.now()
        logger.info("Starting OrdersDetailUpdate job at %s", start_time)
        orders = Orders.objects.filter(status='OPEN')
        if orders.exists():
            if Zerodha is None:
                Zerodha = ZerodhaAPI()

            for order in orders:
                order_details = Zerodha.kite.order_history(order.order_id)
                if order_details:
                    latest_order_detail = order_details[-1]
                    # Update the order details
                    OrdersDetail.objects.update_or_create(
                        order=order,
                        broker_order_id=latest_order_detail['order_id'],
                        defaults={
                            #'status': latest_order_detail['status'],
                            'exchange': latest_order_detail['exchange'],
                            'symbol': latest_order_detail['tradingsymbol'],
                            'transaction_type': latest_order_detail['transaction_type'],
                            'quantity': latest_order_detail['quantity'],
                            'product': latest_order_detail['product'],
                            'order_type': latest_order_detail['order_type'],
                            'trigger_price': latest_order_detail.get('trigger_price', None),
                            'price': latest_order_detail.get('price', None),
                            'filled_quantity': latest_order_detail.get('filled_quantity', 0),
                            'pending_quantity': latest_order_detail.get('pending_quantity', 0),
                            'average_price': latest_order_detail.get('average_price', 0.0),
                            'error_message': latest_order_detail.get('status_message', ''),
                            'response': str(latest_order_detail)
                        }
                    )
                logger.info(f"Order details updated for {order.order_id}")
                order.status = latest_order_detail['status']
                order.updated_at = timezone.now()
                order.save()
                logger.info(f"Order {order.order_id} status updated to {order.status}")
        else:
            logger.info("No open orders found")
    except Exception as e:
        logger.error("Error in OrdersDetailUpdate job: %s", str(e), exc_info=True)
        raise


def OrdersDetailsExit(Zerodha=None):
    """
    Function to exit orders
    """
    if Zerodha is None:
        Zerodha = ZerodhaAPI()

    try:
        start_time = datetime.now()
        logger.info("Starting OrdersDetailsExit job at %s", start_time)
        orders = OrdersDetail.objects.filter(status='COMPLETE')
        symbol_df =  pd.DataFrame.from_records(orders.values())

        if symbol_df.empty:
            logger.info("No open or complted orders found 1  ")
            return

        exchange_nfo = 'NFO'
        trading_symbols = symbol_df['symbol'].tolist()
        ltp_data_nfo = Zerodha.kite.ltp([f"{exchange_nfo}:{symbol}" for symbol in trading_symbols])

        # exchange_nse = 'NSE'
        # ltp_data_nse = Zerodha.kite.ltp([f"{exchange_nse}:{symbol}" for symbol in trading_symbols])

        exchange_nse = 'NSE'
        symbol_list = symbol_df['parent_symbol'].tolist()
        ltp_data = Zerodha.kite.ltp([f"{exchange_nse}:{symbol}" for symbol in symbol_list])

        # symbol_and_token = {}
        # for index,row in symbol_df.iterrows():
        #     tradingsymbol = row['symbol']
        #     instrument_token = row['instrument_token']
        #     symbol_and_token[tradingsymbol] = instrument_token
        # print(symbol_and_token)

        # ohlc_df = Zerodha.get_ohlc_data(symbol_and_token,interval='minute')
        # final_df = pd.DataFrame()
        # for index,row in symbol_df.iterrows():
        #     df = ohlc_df[ohlc_df['trading_symbol'] == row['symbol']]
        #     if ohlc_df.empty:
        #         logger.info(f"No OHLC data found for {row['symbol']}")
        #         continue
        #     #df['RSI'] = talib.RSI(df['close'], timeperiod=14)
        #     df = supertrend(df, period=7, multiplier=3)
        #     final_df = pd.concat([final_df, df])

        if orders.exists():
            for ord in orders:
                # Check if the order is still pending
                if ord.status == 'COMPLETE':
                    try:
                        # Place exit order
                        trading_symbols = ord.symbol
                        strategy = ord.strategy
                        #symbol_df = final_df[final_df['trading_symbol'] == trading_symbols]
                        # if ord.exchange == 'NSE':
                        #     product_type = ord.product
                        #     last_price = ltp_data[f"{ord.exchange}:{trading_symbols}"]['last_price']
                        # elif ord.exchange == 'NFO':
                        #     product_type = ord.product
                        #     last_price = ltp_data_nfo[f"{ord.exchange}:{trading_symbols}"]['last_price']   
                        exit_price = ltp_data_nfo[f"{ord.exchange}:{trading_symbols}"]['last_price'] 

                        product_type = ord.product
                        #ltp  = ltp_data[f"NSE:{ord.parent_symbol}"]
                        ltp  = ltp_data[f"NSE:{ord.parent_symbol}"]['last_price']
                        
                        confirmexit = False
                        if strategy == 'ATH':
                            if ltp < ord.stoploss or (ltp > ord.trigger_price and ord.trigger_price >ord.symbol_price):
                                confirmexit = True
                       
                      
                        if confirmexit:
                            #ord.stoploss = ltp
                            exit_order_id = Zerodha.kite.place_order(
                                variety=Zerodha.VARIETY_REGULAR,
                                exchange=ord.exchange,
                                tradingsymbol=trading_symbols,
                                transaction_type=Zerodha.TRANSACTION_TYPE_SELL,
                                quantity=ord.quantity,
                                price=exit_price,
                                product=product_type,
                                order_type=Zerodha.ORDER_TYPE_LIMIT
                            )
                            
                            
                            logger.info(f"Exit order placed for {ord.symbol} with ID {exit_order_id}")
                            
                            # Update the order status to EXITED
                            ord.status = 'CLOSE'
                            ord.save()
                        else:
                            logger.info(f"Exit order not placed for {ord.symbol} as last price {ltp} is not below stoploss {ord.stoploss} or above trigger price {ord.trigger_price}")   
                    except Exception as e:
                        logger.error(f"Error placing exit order for {ord.symbol}: {str(e)}")
        else:
            logger.info("No pending orders found for exit")

    except Exception as e:
        logger.error("Error in OrdersDetailsExit job: %s", str(e), exc_info=True)
        raise

def OrdersDetailStatusUpdate(Zerodha=None):
    """
    Function to update order status
    """
    try:
        start_time = datetime.now()
        logger.info("Starting OrdersDetailStatusUpdate job at %s", start_time)
        orders = OrdersDetail.objects.filter(status='OPEN')
        if Zerodha is None:
            Zerodha = ZerodhaAPI()
        if orders.exists():
            for order in orders:
                order_details = Zerodha.kite.order_history(order.broker_order_id)
                if order_details:
                    latest_order_detail = order_details[-1]
                    # Update the order status
                    status = latest_order_detail['status']
                    # if status == 'COMPLETE':    
                    #     status = 'PENDING'
                    order.status = status
                    order.filled_quantity = latest_order_detail.get('filled_quantity', 0)
                    order.pending_quantity = latest_order_detail.get('pending_quantity', 0)
                    order.average_price = latest_order_detail.get('average_price', 0.0)
                    order.error_message = latest_order_detail.get('status_message', '')
                    order.response = str(latest_order_detail)
                    order.updated_at = timezone.now()
                    order.save()
                    logger.info(f"Order {order.broker_order_id} status updated to {order.status}")
        else:
            logger.info("No open orders found")
    except Exception as e:
        logger.error("Error in OrdersDetailStatusUpdate job: %s", str(e), exc_info=True)
        raise

def RSI_DIVESION(df_5min:pd.DataFrame,
                 df_15min_today:pd.DataFrame,
                 df_day:pd.DataFrame,
                tradingsymbol:str,instrument_token:int,Zerodha=None):
    """
    Function to find RSI diversion
    """
    try:
        from datetime import time
        start_time = datetime.now()
        current_time = datetime.now().time()
        to_date=datetime.now()
        from_date=datetime.now() - timedelta(days=1)
        #df_5min = resample_ohlc(df_1min, '5T')

        #df_5min_today = df_5min[df_5min['date'].dt.date == datetime.now().date()]

        df_5min['RSI'] = talib.RSI(df_5min['close'], timeperiod=14)
        df_15min_today['RSI'] = talib.RSI(df_15min_today['close'], timeperiod=14)
        df_day['RSI'] = talib.RSI(df_day['close'], timeperiod=14)

        # for hours data
        ohlc_data_1hrs = Zerodha.kite.historical_data(
                        instrument_token=instrument_token,
                        to_date=datetime.now(),
                        from_date=datetime.now() - timedelta(days=30),
                        interval='hour',
                        continuous=False,
                        oi=False
                    )
        
        if df_5min['RSI'].iloc[-1] < 30:
            logger.info(f"RSI Divergence not possible for {tradingsymbol} as daily RSI is above 70")
            return tradingsymbol

        return ''
        df_1hrs = pd.DataFrame(ohlc_data_1hrs)
        df_1hrs['date'] = pd.to_datetime(df_1hrs['date'])
        df_1hrs['RSI'] = talib.RSI(df_1hrs['close'], timeperiod=14)

        print("Finding RSI diversion for ", tradingsymbol)

        df_row = pd.DataFrame()
        df_today = df_5min.tail(75)
        df_today['RSI'] = df_today['RSI'].astype(int)
        df_diversion = pd.DataFrame()
        for i ,data in df_today.iterrows():
            df_row = pd.concat([df_row, pd.DataFrame({
                'date': [data['date']],
                'open': [data['open']],
                'high': [data['high']],
                'low': [data['low']],
                'close': [data['close']],
                'RSI': [data['RSI']]
            })])
            print(df_row)
            if len(df_row) > 2:
                rsi = df_row['RSI'].iloc[-1] > df_row['RSI'].iloc[-2] < df_row['RSI'].iloc[-3]
                
                if rsi and df_row['RSI'].iloc[-2] < 30:
                    
                    logger.info(f"RSI Diversion found for {tradingsymbol} at {data['date']} with RSI {data['RSI']}")
                    df_diversion = pd.concat([df_diversion, pd.DataFrame({
                        'symbol': [tradingsymbol],
                        'date': df_row['date'].iloc[-2],
                        'price': df_row['close'].iloc[-2],
                        'RSI': df_row['RSI'].iloc[-2]
                    })])
           
            if len(df_diversion)==2 and df_diversion['RSI'].iloc[-1] > df_diversion['RSI'].iloc[-2] and df_diversion['price'].iloc[-1] < df_diversion['price'].iloc[-2]:
                logger.info(f"RSI Bullish Diversion confirmed for {tradingsymbol} between {df_diversion['date'].iloc[-2]} and {df_diversion['date'].iloc[-1]}") 
                df_diversion = pd.DataFrame()  # reset after confirmation

                    
                    
                print("----")

        print(df_diversion)


        


        
        
    except Exception as e:
        logger.error("Error  job: %s", str(e), exc_info=True)
        raise

def crose_high_low(Zerodha=None):
    """
    Function to cross high and low
    """
    try:
        from datetime import time
        start_time = datetime.now()
        current_time = datetime.now().time()
        # if time(9, 16) <= current_time <= time(9, 30):
        #     logger.info(f"Crose high low job is running at {current_time}")
            
        # else:
        #     logger.info(f"Crose high low job is not running outside of trading hours {current_time}")
        #     return
        if Zerodha is None:
            Zerodha = ZerodhaAPI()
        
        # order in database
        orders = Orders.objects.filter(status__in=['PENDING','CANCELLED'])
        token_exist = []
        if orders.exists():
            #all token in orders
            token_exist = orders.values_list('parent_token', flat=True)
            token_exist = list(token_exist)
        
            
        expiry_date = settings.EXPIRY
        instruments = Zerodha.kite.instruments("NFO")
        instrument_df = pd.DataFrame(instruments)
        instrument_df = instrument_df[(instrument_df["segment"] == 'NFO-OPT')]
        symbol = instrument_df['name'].unique()
        symbols_list = symbol.tolist()
        symbols_list = [item for item in symbols_list if item not in ['NIFTY','BANKNIFTY','360ONE','FINNIFTY','MIDCPNIFTY','NIFTYNXT50']]

        #df = pd.DataFrame()

        quote_data = Zerodha.kite.quote([f"NSE:{symbol}" for symbol in symbols_list])
        #ltp_data = Zerodha.kite.ltp([f"NSE:{symbol}" for symbol in symbol])
        symbol_and_token = {}
        for symbol in symbols_list:
            instrument_token = quote_data[f"NSE:{symbol}"]["instrument_token"]
            symbol_and_token[symbol] = instrument_token
        # print(symbol_and_token)
        to_date=datetime.now()
        from_date=datetime.now() - timedelta(days=1),
        #ohlc_df = Zerodha.get_ohlc_data(symbol_and_token,interval='day', from_date=from_date, to_date=to_date)
        symbol_option_list = []
        rsi_symbol_option_list = []
        for symbol in symbols_list:
            symbol = 'MUTHOOTFIN'
            if symbol == 'NIFTY' or symbol == 'BANKNIFTY' or symbol == '360ONE' or symbol == 'PGEL':
                continue
            try:
                current_price = quote_data[f"NSE:{symbol}"]["last_price"]
            except KeyError:
                logger.error(f"KeyError: No data found for {symbol}. Skipping.")
                continue
            except Exception as e:
                logger.error(f"Error fetching current price for {symbol}: {str(e)}")
                continue
            
            instrument_token = quote_data[f"NSE:{symbol}"]["instrument_token"]
            if str(instrument_token) in token_exist:
                logger.info(f"Instrument token {instrument_token} for {symbol} already exists in orders. Skipping.")
                continue
            

            quote_data_symbol = quote_data[f"NSE:{symbol}"]
            logger.info(f"Processing symbol ======: {symbol}, Current Price: {current_price}, Instrument Token: {instrument_token}")
            #sleep(0.1)  # To avoid hitting rate limits
            logger.info(f"sleep time {symbol}")
           
            ohlc_data_day = Zerodha.kite.historical_data(
                        instrument_token=instrument_token,
                        to_date=datetime.now(),
                        from_date=datetime.now() - timedelta(days=30),
                        interval='day',
                        continuous=False,
                        oi=False
                    )
            df_symbol_day = pd.DataFrame(ohlc_data_day)
            logger.info(f"time one day candle {symbol}")

            ohlc_data_5min = Zerodha.kite.historical_data(
                        instrument_token=instrument_token,
                        to_date=datetime.now(),
                        from_date=datetime.now() - timedelta(days=30),
                        interval='5minute',
                        continuous=False,
                        oi=False
                    )
            df_symbol_5min = pd.DataFrame(ohlc_data_5min)
            logger.info(f"time 5 min candle {symbol}")

            df_symbol_5min.set_index('date', inplace=True)
            df_15min = resample_ohlc(df_symbol_5min, '15min')
            logger.info(f"time 15 min candle {symbol}")

  
            # previous_day = (datetime.now() - timedelta(days=1)).date()
            # # Filter for today day's data
            df_15min_today = df_15min[df_15min['date'].dt.date == datetime.now().date()]
            # #df_15min_today = df_15min[df_15min['date'].dt.date == previous_day]
            logger.info(f"time df_15min_today today {symbol}")


            rsi_symbol = RSI_DIVESION(df_symbol_5min,df_15min_today,df_symbol_day,symbol,instrument_token,Zerodha)
            if rsi_symbol != '':
                rsi_symbol_option_list.append(rsi_symbol)
                logger.info(f"RSI Diversion symbol list: {rsi_symbol_option_list}")
            continue
           

            if len(df_symbol_day) < 2:
                logger.warning(f"Not enough data for {symbol} to determine high/low crossover.")
                continue
            # if current_price > df_symbol['high'].iloc[-2] and df_symbol['close'].iloc[-1] > df_symbol['open'].iloc[-1]:
           
            
            open_low = df_symbol_day['open'].iloc[-1] == df_symbol_day['low'].iloc[-1]
            if open_low:
                symbol_option_list.append(symbol)
            
            #crose 15min close
            
            min15_close_crose =   current_price > df_15min_today['close'].iloc[0]  
            
            # if current_price > df_symbol['high'].iloc[-2] and df_symbol['open'].iloc[-1] < df_symbol['high'].iloc[-2] and current_price > df_symbol['open'].iloc[-1]:
            #min15_close_crose = True # true for testing
            if open_low and min15_close_crose:
                """ open equal to low """
                logger.info(f"BUY call for {symbol} at {current_price}")
                logger.info(f"df_symbol: {df_symbol_day.tail(3)}")
                
                instrument_symbol = instrument_df[(instrument_df['name']==symbol) & (instrument_df['instrument_type']=='CE') & (instrument_df['strike']>current_price) ]

                symbol_option = instrument_symbol.iloc[0]
                instrument_token_option = symbol_option['instrument_token']
                if str(instrument_token_option) not in token_exist:
                    
                    
                    tradingsymbol = symbol_option['tradingsymbol']
                    quantity = symbol_option['lot_size']
                    

                    quote_data_option = Zerodha.kite.quote([f"NFO:{tradingsymbol}"])
                    stoploss = df_15min_today['low'].iloc[0]
                    current_price_option = quote_data_option[f"NFO:{tradingsymbol}"]['last_price']
                    logger.info(f"Placing BUY order for {tradingsymbol} at {current_price_option}")

                    order = Orders.objects.create(
                        instrument_token=instrument_token_option,
                        symbol=tradingsymbol,
                        price=current_price_option,
                        order_type=Zerodha.kite.ORDER_TYPE_LIMIT,
                        quantity=quantity,
                        product=Zerodha.PRODUCT_NRML,
                        status='CANCELLED',
                        exchange='NFO',  
                        strategy='ATH',
                        stoploss=stoploss,
                        trigger_price=0,
                        parent_symbol = symbol,
                        parent_token = instrument_token,
                        option_type = 'CE',
                        symbol_price = current_price

                    )
                    # if order:
                    #     executor = ThreadPoolExecutor(max_workers=4)
                    #     executor.submit(zerodha_place_order)
                        
            else:
                logger.info(f"SELL signal for {symbol} at {current_price}")
            
            
            #break        

        symbol_option_list_str = ', '.join(symbol_option_list)
        logger.info(f"Symbols with open equal to low today: {symbol_option_list_str}")
        
    except Exception as e:
        logger.error("Error in crose_high_low job: %s", str(e), exc_info=True)
        raise
    finally:
        end_time = datetime.now()
        # Log the start and end time of the job
        logger.info("Crose high low job started at %s", start_time)
        logger.info("Crose high low job ended at %s", end_time)
        # Calculate and log the total time taken for the job
        logger.info("Total time taken for crose_high_low job: %s seconds", (end_time - start_time).total_seconds())
    
def pre_post_market_stock():
    """
    Function to get pre market stock
    """
    try:
        start_time = datetime.now()
        Pre_Market_stock_df = Zerodha.pre_market_stock()
        #print(pre_karker_stock)
        print(Pre_Market_stock_df.head(10))
        from django.db import transaction
        from datetime import time
        #from trading.models import PreMarketStock  # Import your Django model here
        current_time = datetime.now().time()
        if time(9, 7) <= current_time <= time(9, 15):
            type = 'PRE-MARKET'
        elif time(9, 15) <= current_time <= time(15, 30):
            type = 'MARKET'
        else:
            type = 'POST-MARKET'
        instances = []
        for _, row in Pre_Market_stock_df.iterrows():
            instance = PreMarketStock(
                symbol=row['symbol'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                last_price=row['last_price'],
                change=row['change'],
                change_percentage=row['change_percentage'],
                
                volume=row['volume'],
                oi = row['oi'],
                buy_quantity=row['buy_quantity'],
                sell_quantity=row['sell_quantity'],
                type = type
                
            )
            instances.append(instance)
        
        # Use transaction for better performance
        with transaction.atomic():
            PreMarketStock.objects.bulk_create(instances)
    except Exception as e:
        logger.error("Error in pre_post_market_stock job: %s", str(e), exc_info=True)
        raise

if __name__ == "__main__":
    Zerodha = ZerodhaAPI()
    # This block is for testing the functions locally
    #my_scheduled_job()

    #scanner_200ma()
    #zerodha_place_order()
    
    #OrdersDetailUpdate(Zerodha)
    #OrdersDetailsExit(Zerodha)

    #orderdetsil check open order
    #OrdersDetailStatusUpdate(Zerodha)

    #crose_high_low(Zerodha)
    #pre_post_market_stock()
    # watchlists = Zerodha.kite.get_watchlists()
    # print(watchlists)

    # new test
    symbols_list = symbol_list_df['symbol'].unique().tolist()
    symbols_list = [item for item in symbols_list if item not in ['NIFTY','BANKNIFTY','360ONE','PGEL']]

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    date_str = '2025-09-10'
    
    created_date = pd.to_datetime(date_str).date()
    print("====================created_date",date_str)
    data_list = []
    for symbol_name in symbols_list:
        #symbol_name = "INDUSTOWER"
        symbol_name = symbol_name.upper()
        print("symbol_name",symbol_name)
        result = COI.objects.filter(created_at__date=created_date,symbol=symbol_name).order_by('-id')
        if result.exists():
            
            df_chart = pd.DataFrame.from_records(result.values())
            df_chart = df_chart.sort_values(by='id', ascending=True)
            # dataframe date format
            df_chart['created_at'] = pd.to_datetime(df_chart['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            #add column date and time
            df_chart['date'] = pd.to_datetime(df_chart['created_at']).dt.date
            df_chart['time'] = pd.to_datetime(df_chart['created_at']).dt.strftime('%H:%M')
            
            print(df_chart.columns)
            print(df_chart[['symbol','strike','call_trading_symbol','put_trading_symbol','created_at','date','time','current_price']].head(10))

            time_grouped = df_chart.groupby('time').agg({
                'call_coi': lambda x: df_chart.loc[x.index, 'call_coi'][df_chart.loc[x.index, 'strike'] > df_chart.loc[x.index, 'current_price']].sum(),
                'put_coi': lambda x: df_chart.loc[x.index, 'put_coi'][df_chart.loc[x.index, 'strike'] < df_chart.loc[x.index, 'current_price']].sum(),
                
                'current_price': 'first',  # Assuming price_time is same for all entries at a given time
                'call_volume': 'sum' 
            }).reset_index()


            # Create the bar chart using Plotly
            
            # data_row = time_grouped.tail(1)
            # print("data_last",data_row)
            # call_percentage = data_row.call_coi.values[0] / (data_row.call_coi.values[0] + data_row.put_coi.values[0]) * 100 if (data_row.call_coi.values[0] + data_row.put_coi.values[0]) > 0 else 0
            # put_percentage = data_row.put_coi.values[0] / (data_row.call_coi.values[0] + data_row.put_coi.values[0]) * 100 if (data_row.call_coi.values[0] + data_row.put_coi.values[0]) > 0 else 0
            
            time_grouped['call_percentage'] = time_grouped['call_coi'] / (time_grouped['call_coi'] + time_grouped['put_coi']) * 100
            time_grouped['put_percentage'] = time_grouped['put_coi'] / (time_grouped['call_coi'] + time_grouped['put_coi']) * 100

            time_grouped['call_cio_difference'] = (time_grouped['call_coi'] - time_grouped['put_coi'])/((time_grouped['call_coi'] + time_grouped['put_coi'])/2) * 100
            time_grouped.fillna(0, inplace=True)
            # print the dataframe
           

            print(time_grouped)
            # print(f"Call Percentage: {call_percentage:.2f}%")
            # print(f"Put Percentage: {put_percentage:.2f}%")
            dict_data = {
                'symbol': symbol_name,
                
                'call_put_difference': time_grouped['call_cio_difference'].iloc[-1],
                
                'current_price': time_grouped['current_price'].iloc[-1],
                'call_volume': time_grouped['call_volume'].iloc[-1],
                'time': time_grouped['time'].iloc[-1],
            }
            data_list.append(dict_data)
        
    #print(data_list)
    df_new = pd.DataFrame.from_records(data_list)
    df_call = df_new.sort_values(by='call_put_difference', ascending=False)
    #df_put = df_new.sort_values(by='put_percentage', ascending=False)
    print(df_call.head(20))
    print("end")

    pass

    #instrument_token = 877057  # Replace with your instrument token
  
    #ohlc_data = get_ohlc_data(instrument_token, "minute", 1)
    # ohlc_data = Zerodha.kite.historical_data(
    #                 instrument_token=instrument_token,
    #                 to_date=datetime.now(),
    #                 from_date=datetime.now() - timedelta(days=3),
    #                 interval='5minute',
    #                 continuous=False,
    #                 oi=False
    #             )
    # ohlc_data = pd.DataFrame(ohlc_data)
    
    # # Calculate Supertrend
    # ohlc_with_supertrend = supertrend(ohlc_data, period=7, multiplier=3)
    # print(ohlc_with_supertrend)
    
    # Print last few rows
    #print(ohlc_with_supertrend.tail())
    
    # Save to CSV if needed

    # executor = ThreadPoolExecutor(max_workers=4)

    # executor.submit(background_task, {"tes": "11"})
    

    # def my_view(request):
    #     executor.submit(background_task, request.POST)
    #     return HttpResponse("Task started in background")
    
    #pre market stock
    

    


