import os
import sys
import django
from django.conf import settings
import traceback  # Add this import

# Add the Django project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astrology.settings')
#django.setup()
try:
    django.setup()
except Exception as e:
    print(f"Warning: Django setup failed: {e}")
    print("\nFull traceback:")
    traceback.print_exc()  # This will show the complete error

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
from trading.models import Change_IN_OI_Increasing,ScaningStockOI,Orders,Scanner_ema,COI
from trading.nse_options import MostActiveContracts
import requests
from trading.function import generate_stock_chart


PROJECT_PATH = os.path.dirname(settings.BASE_DIR)
instrument_file = os.path.join(PROJECT_PATH,'astrology','DATA','instruments.csv')
instruments_df = pd.read_csv(instrument_file)

symbol_list_df = pd.read_csv(os.path.join(PROJECT_PATH,'astrology','DATA','symbol_list.csv'))
   
Zerodha = ZerodhaAPI()


def check_totla_time(func):
    def wrapper():
        try:
            start = time()
            logger.info(f"decorator find start time of function{func.__name__}",start)
            func()
            end = time()
            logger.info(f"decorator find total time of function{func.__name__}",end-start)
        except Exception as e:
            logger.error(f"Error in decorator find total time of function{func.__name__}",e)
    return wrapper

def my_scheduled_job():
    """
    This function will be executed by the cron job.
    """
    # Create execution record
    try:
        dic = {'name':'gajender','age':25}
        
        # Log the start of the job
        logger.info("Starting scheduled job at %s", timezone.now())

        logger.info("my data is %s", dic)
       
        
    except Exception as e:
        # Log any errors that occur
        logger.error("Error in scheduled job: %s", str(e), exc_info=True)
       
        raise

def signal_200ma():
    """
    This function will be executed by the cron job to calculate 200-day moving average.
    """
    try:
        logger.info("̦ Starting signal_200ma job at %s", timezone.now())
        symbols = ['RELIANCE', 'TATASTEEL']  # Add your symbols here
        
        Zerodha = ZerodhaAPI()
        
        # Example historical data (replace with actual data retrieval)
        for symbol in symbols:
            # Get historical data for 200 days
            to_date = datetime.now()
            from_date = to_date - timedelta(days=250)  # Extra days to ensure 200 data points
            
            historical_data = Zerodha.kite.historical_data(
                instrument_token=Zerodha.kite.instruments('NSE')[0]['instrument_token'],  # You need to map symbols to tokens
                from_date=from_date.date(),
                to_date=to_date.date(),
                interval='day',
                continuous=False,
                oi=False
            )
            
            # Calculate 200 MA
            ma_200 = calculate_200ma(historical_data)
            
            # Get current price
            ltp = Zerodha.kite.ltp([symbol])[symbol]['last_price']
            
            # Generate signal
            if ltp > ma_200 * 1.01:  # Price is above MA with 1% buffer
                signal = 'BUY'
            elif ltp < ma_200 * 0.99:  # Price is below MA with 1% buffer
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            # Save signal to database
            # TradingSignal.objects.create(
            #     symbol=symbol,
            #     price=ltp,
            #     moving_average=ma_200,
            #     signal=signal
            # )
        # historical_data = [
        #     {'date': '2023-01-01', 'close': 100},
        #     {'date': '2023-01-02', 'close': 102},
        #     # Add more data points...
        # ]
        
        # Calculate 200-day moving average
        #ma_200 = calculate_200ma(historical_data)
        
        #logger.info("200-day moving average: %s", ma_200)
        
        logger.info("Completed signal_200ma job at %s", timezone.now())
        
    except Exception as e:
        # Log any errors that occur
        logger.error("Error in signal_200ma job: %s", str(e), exc_info=True)
       
        raise


def zerodha_save_changein_oi():
    try:
        logger.info("Starting zerodha_save_changein_oi job at %s", timezone.now())

        # Check if current time is between 9:00 AM and 3:30 PM
        current_hours = datetime.now().hour
        # market_start = time(9, 0)  # 9:00 AM
        # market_end = time(15, 30)  # 3:30 PM

        # Import time from datetime instead of directly
        # if not (market_start <= current_time <= market_end):
        #     logger.info("Market is closed. Skipping zerodha_save_changein_oi job.")
        #     return
        
        if current_hours > 9 and  current_hours < 15:
            logger.info("Market is running. ")
            return


        file_csv = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'astrology/' 'zerodha_prev_option_chain.csv')
        
        Zerodha = ZerodhaAPI()


        exchange="NFO"
        instruments = Zerodha.kite.instruments(exchange)
        filtered = [
            inst for inst in instruments
            if inst["instrument_type"] in ["CE", "PE"]
        ]
        filtered_df = pd.DataFrame(filtered)
        #filtered_df = filtered_df.head(150)
        filtered_df['expiry'] = filtered_df['expiry'].astype(str)
        trading_symbols = filtered_df['tradingsymbol'].tolist()
        
        quote_data = {}
        # Process symbols in batches of 50
        batch_size = 100
        for i in range(0, len(trading_symbols), batch_size):
            batch = trading_symbols[i:i + batch_size]
            # Prepare the batch request format (exchange:symbol)
            batch_request = [f"{exchange}:{symbol}" for symbol in batch]

            try:
                # Get quote data for the batch
                batch_response = Zerodha.get_quote(batch_request)
                # Merge the batch response into the main quote_data
                quote_data.update(batch_response)

                #print(f"Processed {min(i + batch_size, len(trading_symbols))}/{len(trading_symbols)} symbols")
                logger.info(f"Processed {min(i + batch_size, len(trading_symbols))}/{len(trading_symbols)} symbols")

            except Exception as e:
                logger.error(f"Error processing batch {i // batch_size + 1}: {str(e)}")
                #return JsonResponse({'error': str(e)}, status=400)
        
        
        filtered_df['prev_oi'] = filtered_df['tradingsymbol'].apply(
                                    lambda x: quote_data.get(f"{exchange}:{x}", {}).get('oi', None))
        

        filtered_df['prev_oi'] = filtered_df['prev_oi'].fillna(0)
        filtered_df['prev_oi'] = np.where(
                                filtered_df['prev_oi'] == 0,0,
                                (filtered_df['prev_oi'] / filtered_df['lot_size']).astype(int))
        
        
        # add column current date and time
        filtered_df['current_date_time'] = datetime.now()
        filtered_df.sort_values(by=['tradingsymbol','strike'], inplace=True)

        # save to csv
        filtered_df.to_csv(file_csv, index=False)
        logger.info(filtered_df.head(10))
        logger.info("Completed zerodha_save_changein_oi job at %s", timezone.now())
        

      
    except Exception as e:
        # Log any errors that occur
        logger.error("Error in zerodha_save_changein_oi job: %s", str(e), exc_info=True)
       
        raise


def zerodha_place_order_example():
    """
    Example function demonstrating how to place different types of orders using ZERODHA_API
    """
    try:
        logger.info("Starting zerodha_place_order_example job at %s", timezone.now())
        Zerodha = ZerodhaAPI()

        # Example 1: Place a MARKET BUY order for NIFTY options
        try:
            # Market order example - NIFTY 22000 CE
            market_order_id = Zerodha.place_order(
                variety=Zerodha.VARIETY_REGULAR,
                exchange=Zerodha.EXCHANGE_NFO,
                tradingsymbol="NIFTY24JUN22000CE",  # Replace with actual symbol
                transaction_type="BUY",
                quantity=50,  # Lot size for NIFTY options
                product="NRML",  # Normal product
                order_type="MARKET"  # Market order
            )
            logger.info(f"Market order placed successfully. Order ID: {market_order_id}")
        except Exception as e:
            logger.error(f"Error placing market order: {str(e)}")

        # Example 2: Place a LIMIT BUY order for BANKNIFTY options
        try:
            # Limit order example - BANKNIFTY 48000 CE
            limit_order_id = Zerodha.place_order(
                variety=Zerodha.VARIETY_REGULAR,
                exchange=Zerodha.EXCHANGE_NFO,
                tradingsymbol="BANKNIFTY24JUN48000CE",  # Replace with actual symbol
                transaction_type="BUY",
                quantity=15,  # Lot size for BANKNIFTY options
                product="NRML",
                order_type="LIMIT",
                price=150.50  # Limit price
            )
            logger.info(f"Limit order placed successfully. Order ID: {limit_order_id}")
        except Exception as e:
            logger.error(f"Error placing limit order: {str(e)}")

        # Example 3: Place a STOP LOSS order for equity
        try:
            # Stop loss order example - RELIANCE
            sl_order_id = Zerodha.place_order(
                variety=Zerodha.VARIETY_REGULAR,
                exchange=Zerodha.EXCHANGE_NSE,
                tradingsymbol="RELIANCE",
                transaction_type="SELL",
                quantity=100,
                product="CNC",  # Cash and Carry
                order_type="SL",
                price=2400.00,  # Stop loss price
                trigger_price=2450.00  # Trigger price
            )
            logger.info(f"Stop loss order placed successfully. Order ID: {sl_order_id}")
        except Exception as e:
            logger.error(f"Error placing stop loss order: {str(e)}")

        # Example 4: Place a STOP LOSS MARKET order
        try:
            # Stop loss market order example - INFY
            slm_order_id = Zerodha.place_order(
                variety=Zerodha.VARIETY_REGULAR,
                exchange=Zerodha.EXCHANGE_NSE,
                tradingsymbol="INFY",
                transaction_type="SELL",
                quantity=200,
                product="CNC",
                order_type="SL-M",  # Stop Loss Market
                trigger_price=1400.00  # Trigger price
            )
            logger.info(f"Stop loss market order placed successfully. Order ID: {slm_order_id}")
        except Exception as e:
            logger.error(f"Error placing stop loss market order: {str(e)}")

        # Example 5: Get current positions
        try:
            positions = Zerodha.get_positions()
            logger.info(f"Current positions: {positions}")
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")

        # Example 6: Get order history
        try:
            orders = Zerodha.get_orders()
            logger.info(f"Order history: {orders}")
        except Exception as e:
            logger.error(f"Error getting orders: {str(e)}")

        logger.info("Completed zerodha_place_order_example job at %s", timezone.now())

    except Exception as e:
        logger.error("Error in zerodha_place_order_example job: %s", str(e), exc_info=True)
        raise



def option_chain():
    """
    Function to save option chain data
    """
    try:
        expiry_date = settings.EXPIRY  # Use expiry date from settings
        start_time = datetime.now()
        logger.info("Starting option_chain job at %s", start_time)

        from datetime import time
        current_time = datetime.now().time()
        if time(9, 15) <= current_time <= time(15, 30):
            logger.info(f"Otion Chain job is running at {current_time}")
        else:
            logger.info(f"Otion Chain job is not running outside of trading hours {current_time}")
            return
        Zerodha = ZerodhaAPI()
        instruments = Zerodha.kite.instruments("NFO")
        instrument_df = pd.DataFrame(instruments)
        instrument_df = instrument_df[(instrument_df["segment"] == 'NFO-OPT')]
        symbol = instrument_df['name'].unique()
        symbols_list = symbol.tolist()
        #symbols_list = [item for item in symbols_list if item not in ['NIFTY','BANKNIFTY','360ONE']]
        symbols_list = [item for item in symbols_list if item not in ['BANKNIFTY','360ONE']]

        symbols_list = ['NIFTY 50' if x=='NIFTY' else x for x in symbols_list]
        
        #print(instruments_df.head(10))
        #symbols_list = ['AARTIIND','BAJAJFINSV']
        n = 0
        symbol_list_new = []
        df = pd.DataFrame()
        quote_data = Zerodha.kite.quote([f"NSE:{symbol}" for symbol in symbols_list])
        for symbol in symbols_list:
            #symbol = "DABUR"
            # if symbol == 'NIFTY':
            #     symbol = "NIFTY 50"
            # if symbol == 'BANKNIFTY':
            #     symbol = "NIFTY BANK"
            if symbol == 'NIFTY' or symbol == 'BANKNIFTY' or symbol == '360ONE' or symbol == 'PGEL':
                continue
            try:
                current_price = quote_data[f"NSE:{symbol}"]["last_price"]
                instrument_token = quote_data[f"NSE:{symbol}"]["instrument_token"]
                #day_low = quote_data[f"NSE:{symbol}"]["ohlc"]["low"]
                #day_high = quote_data[f"NSE:{symbol}"]["ohlc"]["high"]  
                symbol_quote_ddata = quote_data[f"NSE:{symbol}"]
            except KeyError:
                logger.error(f"KeyError: No data found for {symbol}. Skipping.")
                continue
            except Exception as e:
                logger.error(f"Error fetching current price for {symbol}: {str(e)}")
                continue

            n = n + 1
            symbol = 'NIFTY' if symbol == 'NIFTY 50' else symbol
            filtered = [
                inst for inst in instruments
                if inst["name"] == symbol and
                inst["instrument_type"] in ["CE", "PE"]
            ]
            filtered_df = pd.DataFrame(filtered)
            filtered_df['expiry'] = filtered_df['expiry'].astype(str)
            filtered_df = filtered_df[filtered_df['expiry'] == expiry_date]
            filtered_df.sort_values(by=['strike'], inplace=True)
            # add previous OI and LTP and change in OI
            data = calculate_coi(
                Zerodha,symbol,
                filtered_df,
                expiry_date=expiry_date
                )
                      
            instrument_df = data['df']
            if instrument_df.empty:
                logger.warning(f"No data found for {symbol} on {expiry_date}. Skipping.")
                continue
            if not instrument_df.empty:
                res = save_coi(instrument_df,symbol,instrument_token,current_price,expiry_date=expiry_date)
                #symbol_list_new.append(symbol)

        logger.info("start_time: %s", start_time)
        logger.info("Completed at %s", datetime.now())
        logger.info("Duration: %s seconds", (datetime.now() - start_time).total_seconds())  

    except Exception as e:
        logger.error("Error in option_chain job: %s", str(e), exc_info=True)
        raise   

#@check_totla_time
def Change_IN_OI_Increasing_Save():
    """
    Function to check if Change in OI is increasing
    """
    try:
        expiry_date = settings.EXPIRY  # Use expiry date from settings
        start_time = datetime.now()
        logger.info("Starting Change_IN_OI_Increasing_Save job at %s", start_time)

        Zerodha = ZerodhaAPI()

        

        instruments = Zerodha.kite.instruments("NFO")
        instrument_df = pd.DataFrame(instruments)
        instrument_df = instrument_df[(instrument_df["segment"] == 'NFO-OPT')]
        symbol = instrument_df['name'].unique()
        symbols_list = symbol.tolist()
        symbols_list = [item for item in symbols_list if item not in ['NIFTY','BANKNIFTY','360ONE']]

        
        #print(instruments_df.head(10))
        #symbols_list = ['AARTIIND','BAJAJFINSV']
        n = 0
        symbol_list_new = []
        df = pd.DataFrame()

        quote_data = Zerodha.kite.quote([f"NSE:{symbol}" for symbol in symbols_list])


        for symbol in symbols_list:
            

            #symbol = "DABUR"
            # if symbol == 'NIFTY':
            #     symbol = "NIFTY 50"
            # if symbol == 'BANKNIFTY':
            #     symbol = "NIFTY BANK"
            if symbol == 'NIFTY' or symbol == 'BANKNIFTY' or symbol == '360ONE' or symbol == 'PGEL':
                continue
            # try:
            #     #sleep(1)
            #     quote_data = Zerodha.kite.quote([f"NSE:{symbol}"])
            #     #print(quote_data)
            # except Exception as e:
            #     logger.error(f"Error fetching quote data for {symbol}: {str(e)}")
            #     continue
                
            # if not quote_data:
            #     logger.info("No data found for this symbol=",symbol)
            #     continue
            try:
                current_price = quote_data[f"NSE:{symbol}"]["last_price"]
                instrument_token = quote_data[f"NSE:{symbol}"]["instrument_token"]
            except KeyError:
                logger.error(f"KeyError: No data found for {symbol}. Skipping.")
                continue
            except Exception as e:
                logger.error(f"Error fetching current price for {symbol}: {str(e)}")
                continue

            n = n + 1
            filtered = [
                inst for inst in instruments
                if inst["name"] == symbol and
                inst["instrument_type"] in ["CE", "PE"]
            ]
            #logger.info(f"Processing symbol {n}: {symbol} with current price {current_price}")
            # Convert to DataFrame
            filtered_df = pd.DataFrame(filtered)

            filtered_df['expiry'] = filtered_df['expiry'].astype(str)

            filtered_df = filtered_df[filtered_df['expiry'] == expiry_date]

            filtered_df.sort_values(by=['strike'], inplace=True)

            # add previous OI and LTP and change in OI
            data = calculate_coi(Zerodha,symbol,filtered_df,expiry_date=expiry_date)
            
            instrument_df = data['df']
            if instrument_df.empty:
                logger.warning(f"No data found for {symbol} on {expiry_date}. Skipping.")
                continue
            if not instrument_df.empty:
                # Find the strike price closest to current price
                #res = save_coi(instrument_df,symbol,instrument_token,expiry_date=expiry_date)

                instrument_df['distance'] = abs(instrument_df['strike'] - current_price)
                closest_strike_idx = instrument_df['distance'].idxmin()

                # Get 10 rows above and below the closest strike
                start_idx = max(0, closest_strike_idx - 2)
                end_idx = min(len(instrument_df), closest_strike_idx + 2 + 1)  # +1 to include the row itself
                instrument_df = instrument_df.iloc[start_idx:end_idx]
                # Drop the temporary distance column
                instrument_df = instrument_df.drop(columns=['distance'])
                #print(instrument_df)
                # Concatenate with the main DataFrame
                instrument_df2 = unpivoted_df(instrument_df)
                #print(instrument_df2)
                df = pd.concat([df, instrument_df2], ignore_index=True)
                symbol_list_new.append(symbol)
                symbol_end_time = datetime.now()
                symbol_duration = symbol_end_time - start_time
                #logger.info(f"Processed symbol {n}: {symbol} in {symbol_duration.total_seconds()} seconds")
            
            #break
                

        df['oi_quantity'] = df['oi'] * df['lot_size']
        df['change_in_oi_quantity'] = df['change_in_oi'] * df['lot_size']
        df['prev_oi_quantity'] = df['prev_oi'] * df['lot_size']
        df['change_in_oi_percentage_quantity'] = df['change_in_oi_quantity'] / df['prev_oi_quantity'].replace(0, float(
        'nan')) * 100

        df = df[['tradingsymbol', 'name', 'last_price',
                 'prev_close', 'current_price', 
                'change_in_price','change_in_price_percentage','prev_oi', 'oi',
                 'change_in_oi', 'change_in_oi_percentage','lot_size',
                 'oi_quantity', 'change_in_oi_quantity', 'prev_oi_quantity',
                 'change_in_oi_percentage_quantity'
                 ]]

        #df.sort_values(by=['change_in_oi_percentage'],ascending=False, inplace=True)
        df.sort_values(by=['change_in_oi_percentage_quantity'],ascending=False, inplace=True)

        df = df.head(30)
        #place_order_15(Zerodha, df)
        # Save to database
        #Change_IN_OI_Increasing.objects.all().delete()
        for index, row in df.iterrows():
            try:
                #logger.info(f"Saving data for {row['tradingsymbol']}")
                
                Change_IN_OI_Increasing.objects.create(
                    tradingsymbol=row['tradingsymbol'],
                    name = row['name'],
                    previous_close=row['prev_close'],
                    current_price=row['current_price'],
                    change_in_price=row['change_in_price'],
                    change_in_price_percentage=row['change_in_price_percentage'],
                    prev_oi=row['prev_oi'],
                    oi=row['oi'],
                    change_in_oi=row['change_in_oi'],
                    change_in_oi_percentage=row['change_in_oi_percentage'],
                    oi_quantity=row['oi_quantity'],
                    change_in_oi_quantity=row['change_in_oi_quantity'],
                    prev_oi_quantity=row['prev_oi_quantity'],
                    change_in_oi_percentage_quantity=row['change_in_oi_percentage_quantity']
                    
                )
            except Exception as e:
                #print(f"Error saving data for {row['tradingsymbol']}: {str(e)}")
                logger.error(f"Error saving data for {row['tradingsymbol']}: {str(e)}")

        #print(df)   
        # place order 9:15 to 9:20
        from datetime import time
        current_time = datetime.now().time()
        # Check if current time is between 9:15 AM and 3:30 PM
        if time(9, 15) <= current_time <= time(23, 20):
            logger.info("Current time is within the trading hours. Proceeding with order placement.")
            #order = place_order_15(Zerodha, df)
            # if order:
            #     logger.info(f"Order placed successfully 9:15-9:20: {order}")
            #     executor = ThreadPoolExecutor(max_workers=4)
            #     executor.submit(zerodha_place_order)
            


        logger.info("Change in OI Increasing Data: %s", df.head(10))

        logger.info("start_time: %s", start_time)
        logger.info("Completed at %s", datetime.now())
        logger.info("Duration: %s seconds", (datetime.now() - start_time).total_seconds())  
        
    except Exception as e:
        logger.error("Error in Change_IN_OI_Increasing_Save job: %s", str(e), exc_info=True)
        raise

def Change_IN_OI_scanner():
    """
    Function to check if Change in OI is increasing
    """
    try:
        expiry_date = settings.EXPIRY  # Use expiry date from settings
        start_time = datetime.now()
        logger.info("Starting Change_IN_OI_scanner job at %s", start_time)

        Zerodha = ZerodhaAPI()
        instruments = Zerodha.kite.instruments("NFO")
        instrument_df = pd.DataFrame(instruments)
        instrument_df = instrument_df[(instrument_df["segment"] == 'NFO-OPT')]
        symbol = instrument_df['name'].unique()
        symbols_list = symbol.tolist()
        #symbols_list = [item for item in symbols_list if item not in ['NIFTY','BANKNIFTY','360ONE']]
        symbols_list = [item for item in symbols_list if item not in ['BANKNIFTY','360ONE']]

        #symbols_list = ['NIFTY 50' if x=='NIFTY' else x for x in symbols_list]
        
        #print(instruments_df.head(10))
        #symbols_list = ['AARTIIND','BAJAJFINSV']
        n = 0
        symbol_list_new = []
        df = pd.DataFrame()
        #quote_data = Zerodha.kite.quote([f"NSE:{symbol}" for symbol in symbols_list])
        #today = (datetime.now()-timedelta(1)).strftime("%Y-%m-%d")
        today = (datetime.now()).strftime("%Y-%m-%d")
        #result = COI.objects.filter(created_at__date=today)
        #df = pd.DataFrame.from_records(result.values())
        
        for symbol in symbols_list: 
            #symbol = 'LT'
            df_final = pd.DataFrame()
            print("==============tradingsymbol=",symbol)
            result = COI.objects.filter(created_at__date=today,symbol=symbol).order_by('-id')
            if result.count() == 0:
                continue
            df = pd.DataFrame.from_records(result.values())
            df = df.sort_values(by='id', ascending=True)
            current_price = df['current_price'].iloc[-1]
            
            # dataframe date format
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            #add column date and time
            df['date'] = pd.to_datetime(df['created_at']).dt.date
            df['time'] = pd.to_datetime(df['created_at']).dt.strftime('%H:%M')
            #df = df[['symbol','current_price','strike','created_at']]

            current_price = df['current_price'].iloc[-1]
            current_datetime = df['created_at'].iloc[-1]

            df_call = df[(df['strike'] >= current_price) & (df['created_at'] == current_datetime)]
            df_put = df[(df['strike'] <= current_price) & (df['created_at'] == current_datetime)] 

            df_call = df_call.head(2)
            df_put = df_put.tail(2)
            call_total = df_call['call_coi'].sum()
            put_total = df_put['put_coi'].sum()

            call_max = df_call['call_coi'].max()
            put_max = df_put['put_coi'].max()
            if call_total > put_total*2 and call_total>200: 
                    obj, created = ScaningStockOI.objects.update_or_create(
                        symbol= symbol, 
                        created_at__date = today,
                        defaults={
                                'type' : 'call',
                                'total_volume_call' : 0,
                                "total_volume_put" : 0,
                                'total_coi_call' : call_total,
                                'total_coi_put' : put_total,
                                'created_at' : timezone.now()

                        }
                    )
            if put_total > call_total*2 and put_total>200: 
                    obj, created = ScaningStockOI.objects.update_or_create(
                        symbol= symbol, 
                        created_at = today,
                        defaults={
                                'type' : 'put',
                                'total_volume_call' : 0,
                                "total_volume_put" : 0,
                                'total_coi_call' : call_total,
                                'total_coi_put' : put_total,
                                'created_at' : today

                        }
                    )
            

       

        logger.info("**********start_time: %s", start_time)
        logger.info("*************End time %s", datetime.now())
        
    except Exception as e:
        logger.error("Error in Change_IN_OI_scanner job: %s", str(e), exc_info=True)
        raise

def scanner_200ma():
    exchange = "NSE"
    expiry_date = settings.EXPIRY
    start_time = datetime.now()
    logger.info("**************Starting scanner_200ma job at %s", start_time)
    # now = datetime.now().time()
    # # Only execute between 9:15 and 15:30
    # if not (time(9, 15) <= now <= time(15, 30)):
    #     logger.info("return start at %s", start_time)
    #     return


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
        interval = '3minute'  #minute,60minute
        scanner_symbol = []
        #filtered_instrument = filtered_instrument.head(5)
        for index,row in filtered_instrument.iterrows():
            tradingsymbol = row['tradingsymbol']
            #if tradingsymbol != ''
            name = row['name']
            print("==============tradingsymbol=============",tradingsymbol,'===',name)
            logger.info("Processing symbol: %s", tradingsymbol)
            # if tradingsymbol !='INDIGO':
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
                #ohlc_df = ohlc_df.tail(200)
                #ohlc_df['date_time'] =ohlc_df['date']
                #ohlc_df = calculate_ema(ohlc_df, 200)
                ohlc_df['ema_200'] = talib.EMA(ohlc_df['close'], timeperiod=200)
               
                ohlc_df['date'] = pd.to_datetime(ohlc_df['date'])
                ohlc_df.set_index('date', inplace=True)

                ohlc_df['RSI'] = talib.RSI(ohlc_df['close'], timeperiod=14)
                # Filter for today's data only
                # today = pd.Timestamp.now().date()
                # ohlc_df = ohlc_df[ohlc_df.index.date == today]
                # Resample data to 1 hour intervals

              
                

                if (ohlc_df['close'].iloc[-1] > ohlc_df['ema_200'].iloc[-1]) and (ohlc_df['close'].iloc[-2] < ohlc_df['ema_200'].iloc[-2]) :
                    scanner_symbol.append(tradingsymbol)
                    #print(ohlc_df.tail(10))
                    logger.info("ohlc_df: \n%s", ohlc_df.tail(5))
                    Scanner_ema.objects.create(
                        symbol=tradingsymbol,
                        open=ohlc_df['open'].iloc[-1],
                        high=ohlc_df['high'].iloc[-1],
                        low=ohlc_df['low'].iloc[-1],
                        close=ohlc_df['close'].iloc[-1],
                        ema=ohlc_df['ema_200'].iloc[-1],
                        ema_type='ema_200',
                        date=ohlc_df.index[-1].strftime('%Y-%m-%d %H:%M:%S')
                    )  
                    #logger.info(f"EMA saved for {tradingsymbol} : {ohlc_df['200ma'].iloc[-1]} and date {ohlc_df['date'].iloc[-1]}")

            except Exception as e:
                logger.error("****************Error job: %s", str(e))
                raise

    except Exception as e:
        logger.error("Error =================================== job: %s", str(e))
        raise

    logger.info("********************End time %s", datetime.now())
    


def zerodha_place_order_example():
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


        exchange_nfo = 'NFO'
        trading_symbols = symbol_df['symbol'].tolist()
        ltp_data_nfo = Zerodha.kite.ltp([f"{exchange_nfo}:{symbol}" for symbol in trading_symbols])

        exchange_nse = 'NSE'
        ltp_data_nse = Zerodha.kite.ltp([f"{exchange_nse}:{symbol}" for symbol in trading_symbols])

        symbol_and_token = {}
        for index,row in symbol_df.iterrows():
            tradingsymbol = row['symbol']
            instrument_token = row['instrument_token']
            symbol_and_token[tradingsymbol] = instrument_token
        print(symbol_and_token)

        ohlc_df = Zerodha.get_ohlc_data(symbol_and_token,interval='minute')

        #for ATH Stetegy
        ath_df = symbol_df[symbol_df['strategy'] == 'ATH']
        # Filter OHLC data for ATH strategy symbols
        ath_symbols = ath_df['symbol'].tolist()
        ath_ohlc_df = ohlc_df[ohlc_df['trading_symbol'].isin(ath_symbols)]
        #logger.info(f"ATH strategy OHLC data: {ath_ohlc_df}")
        
        result = ATH_Strategy(Zerodha,ath_ohlc_df,ath_df)

        # for index,row in symbol_df.iterrows():
        #     if row['strategy'] == 'ATH':
        #         #ath_strategy()
        #         order_df = ohlc_df[ohlc_df['trading_symbol'] == row['symbol']]
        #         print(order_df)


        
      

    except Exception as e:
        logger.error("Error in zerodha_place_order job: %s", str(e), exc_info=True)
        raise

def get_nse_derivatives_data(index='calls-stocks-vol'):
    """
    Fetch derivatives data from NSE India API
    """
    # URL for the API endpoint
    try:
        url = f"https://www.nseindia.com/api/snapshot-derivatives-equity?index={index}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/",
            "Connection": "keep-alive",
        }

        # Create a session
        session = requests.Session()

        # Step 1: Hit homepage to get cookies
        home_resp = session.get("https://www.nseindia.com", headers=headers)
        if home_resp.status_code != 200:
            logger.error(f"Error fetching homepage: {home_resp.status_code}")
        else:
            logger.info("Homepage cookies set successfully.")

        # Step 2: Add cookies manually if needed
        # (Optional - usually not needed since session already has them)
        cookies = session.cookies.get_dict()
        logger.info(f"Cookies received: {cookies}")
        # Step 3: Fetch the NSE API
        logger.info(f"Fetching data from NSE cookies: {cookies}")
        resp = session.get(url, headers=headers, cookies=cookies)
        # Step 4: Handle response
        if resp.status_code == 200:
            data = resp.json()
            data = data['OPTSTK']
            df = pd.json_normalize(data['data'])
            return df
            
        else:
            logger.error(f"Error fetching data from NSE API: {resp.status_code}")
            sleep(3)
            get_nse_derivatives_data(index=index)

            
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
def SaveMostActiveContracts(Zerodha):
    logger.info("Fetching most active contracts...")
    index_call = 'calls-stocks-vol'
    # active_call = MostActiveContracts(index_call)
    # data_call = active_call.fetch_data()
    #print(data_call)
    df = get_nse_derivatives_data()
    for index, row in df.head(10).iterrows():
        try:
            symbol = row['symbol']
            logger.info(f"Saved most active contract: {symbol}")
        except Exception as e:
            logger.error(f"Error saving contract {symbol}: {str(e)}")
    

def ThreadExecutor():
    Zerodha = ZerodhaAPI()
    # executor = ThreadPoolExecutor(max_workers=4)
    # ex1 = executor.submit(SaveMostActiveContracts,Zerodha)
    # print("ex1",ex1)
    SaveMostActiveContracts(Zerodha)


def save_instrument():
    instruments_df = Zerodha.get_instruments()
    instruments_df['expiry'] = pd.DatetimeIndex(instruments_df['expiry'])
    instruments_df.to_csv(instrument_file, index=False)

# from django_cron import CronJobBase, Schedule

# class MyScheduledTask(CronJobBase):
#     code = 'my_app.my_scheduled_task'  # A unique code for your cron job

#     # Define the schedule to run at 9:30, 10:00, and 10:30
#     schedule = Schedule(
#         run_at_times=['09:30', '10:00', '10:30']
#     )

#     def do(self):
#         # Your task logic goes here
#         print("Running MyScheduledTask at specified times!")
#         # Example: Perform database operations, send emails, etc.

def test_code():
    documents ={
    "home":[
        {
            "documents":[
                "file1.txt",
                {
                "office":[
                    "data.txt"
                ]
                },
                "official.txt",
                "Official.pdf"
            ]
        },
        "troops.txt"
    ]
    }
    # find the output like path home/documents/office/data.txt
    output = []
    def find_path(documents, path):
        for key, value in documents.items():
            if isinstance(value, list):
                find_path(value, path + [key])
            elif isinstance(value, dict):
                find_path(value, path + [key])
            else:
                output.append('/'.join(path + [value]))
    find_path(documents, [])
    print(output)




if __name__ == "__main__":
    # This block is for testing the functions locally
    #test_code()
    #my_scheduled_job()
    #save_instrument()
    #zerodha_save_changein_oi() # save previous OI data
    #Change_IN_OI_Increasing_Save()
    Change_IN_OI_scanner() # save current OI check 
    #scanner_200ma()
    #option_chain()


    #ThreadExecutor()

    # data =generate_stock_chart({'symbol':'ABB'})
    # COI_DATA = data['time_grouped']
    # call = COI_DATA.iloc[-1]['call_coi']
    # put = COI_DATA.iloc[-1]['put_coi']

    today = datetime.now().date()-timedelta(days=1)
    created_date = today
    symbol_name = 'ABB'

    result = COI.objects.filter(created_at__date=created_date,symbol=symbol_name).order_by('id')
    df_chart = pd.DataFrame.from_records(result.values())
    columns = ['symbol',  'strike', 'call_coi', 'current_price','put_coi','created_at','date','time']
    df_chart['created_at'] = pd.to_datetime(df_chart['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    df_chart['date'] = pd.to_datetime(df_chart['created_at']).dt.date
    df_chart['time'] = pd.to_datetime(df_chart['created_at']).dt.strftime('%H:%M')

    # creted date unique values
    df_final = pd.DataFrame()
    created_date = df_chart['created_at'].unique()
    for date in created_date:
        print("Created Date:", date)
        df_date = df_chart[df_chart['created_at'] == date]
        current_price = df_date['current_price'].iloc[-1]
        df_call = df_date[(df_date['strike'] >= current_price)]
        df_put = df_date[(df_date['strike'] <= current_price)]    
        df = pd.concat([df_put.tail(3),df_call.head(3)])
        df_final = pd.concat([df_final, df])
        
    
    current_price = df_chart['current_price'].iloc[-1]
    # filter df_chart for strike 5 above and below current price
    
    # df_chart = df_chart[columns] 
    # # df filter for strike price within 5 above and below current price
    # df_call = df_chart[(df_chart['strike'] >= current_price)]
    # df_put = df_chart[(df_chart['strike'] <= current_price)]    
    # df_chart = pd.concat([df_put.tail(5),df_call.head(5)])

    print(df_chart)


    
    # Test order placement (uncomment to test)

    # Zerodha = ZerodhaAPI()
    # position = Zerodha.get_positions()
    # logger.info(f"Current positions: {position}")


    
    # for symbol in symbols_list:
    #     try:
    #         current_price = quote_data[f"NSE:{symbol}"]["last_price"]
    #         previous_close = quote_data[f"NSE:{symbol}"]["ohlc"]["close"]
    #         instrument_token = quote_data[f"NSE:{symbol}"]["instrument_token"]
    #         print(symbol,current_price,previous_close)
    #     except KeyError:
    #         logger.error(f"KeyError: No data found for {symbol}. Skipping.")
    #         continue
    #     except Exception as e:
    #         logger.error(f"Error fetching current price for {symbol}: {str(e)}")
    #         continue

    
    
        

    


    print("Cron jobs executed successfully.")