import os
import logging
from django.utils import timezone
#from .models import CronJob, CronJobExecution

import pandas as pd 
import numpy as np  
import time 
from datetime import datetime, timedelta
# Configure logging 
logger = logging.getLogger(__name__)
# import ZERODHA_API
from trading.models import *
from concurrent.futures import ThreadPoolExecutor
from django.db import transaction



def calculate_coi(Zerodha,symbol,filtered_df, exchange="NFO", expiry_date="2025-06-26"):
    """
    Calculate Change in OI (Open Interest) for the given symbol and DataFrame.
    """
    try:
        pre_oi_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'astrology/' 'zerodha_prev_option_chain.csv')
        prev_instrument_df = pd.read_csv(pre_oi_file)
        prev_instrument_df = prev_instrument_df[(prev_instrument_df['expiry'] == expiry_date) &
                                                (prev_instrument_df['name'] == symbol)]
        if prev_instrument_df.empty:
            logger.warning(f"No previous OI data found for {symbol} on {expiry_date}.")
            return {
            'df': pd.DataFrame() ,
            'filtered_df' : pd.DataFrame()
            }
        
        filtered_df = pd.merge(
            filtered_df,
            prev_instrument_df[['strike', 'instrument_type', 'prev_oi']],
            on=['strike', 'instrument_type'],
            how='left',
            suffixes=('', '_prev')
        )
        
        # Fill NaN values with 0 (if no previous data available)
        filtered_df['prev_oi'] = filtered_df['prev_oi'].fillna(0)

        # Get trading symbols for LTP and OI query
        trading_symbols = filtered_df['tradingsymbol'].tolist()

        # Get LTP data
        ltp_data = Zerodha.kite.ltp([f"{exchange}:{symbol}" for symbol in trading_symbols])

        # Get quote data (for OI and volume)
        quote_data = Zerodha.kite.quote([f"{exchange}:{symbol}" for symbol in trading_symbols])


        filtered_df['prev_close'] = filtered_df['tradingsymbol'].apply(
            lambda x: quote_data[f"{exchange}:{x}"]["ohlc"]["close"])
        # Extract LTP values and add to DataFrame
        filtered_df['current_price'] = filtered_df['tradingsymbol'].apply(
            lambda x: ltp_data.get(f"{exchange}:{x}", {}).get('last_price', None)
        )

        filtered_df['day_low'] = filtered_df['tradingsymbol'].apply(
                lambda x: quote_data[f"{exchange}:{x}"]["ohlc"]["low"])

        filtered_df['day_high'] = filtered_df['tradingsymbol'].apply(
                lambda x: quote_data[f"{exchange}:{x}"]["ohlc"]["high"])
        
        filtered_df['day_open'] = filtered_df['tradingsymbol'].apply(
                lambda x: quote_data[f"{exchange}:{x}"]["ohlc"]["open"])

        filtered_df['change_in_price'] = filtered_df['current_price'] - filtered_df['prev_close']
        filtered_df['change_in_price_percentage'] = (filtered_df['change_in_price'] / filtered_df['prev_close']) * 100

        # Extract OI values and add to DataFrame (normalized by lot size)
        filtered_df['oi'] = filtered_df['tradingsymbol'].apply(
            lambda x: quote_data.get(f"{exchange}:{x}", {}).get('oi', None))
        filtered_df['oi'] = (filtered_df['oi'] / filtered_df['lot_size']).astype(int)
        filtered_df['change_in_oi'] = filtered_df['oi'] - filtered_df['prev_oi']
        filtered_df['change_in_oi_percentage'] = filtered_df['change_in_oi'] / filtered_df['prev_oi'].replace(0, float(
            'nan')) * 100



        # Extract volume values and add to DataFrame (normalized by lot size)
        filtered_df['volume'] = filtered_df['tradingsymbol'].apply(
            lambda x: quote_data.get(f"{exchange}:{x}", {}).get('volume', None))
        filtered_df['volume'] = (filtered_df['volume'] / filtered_df['lot_size']).astype(int)

        # Pivot the table to get one row per strike with CE and PE columns
        column_list = filtered_df.columns.tolist()
        column_list.remove('instrument_type')
        column_list.remove('strike')
        pivot_df = filtered_df.pivot(
            index='strike',
            columns='instrument_type',
            #values=['current_price', 'oi', 'change_in_oi', 'volume', 'tradingsymbol', 'instrument_token', 'lot_size','name','day_low','day_high',day_open]
            values=column_list
        )

        # Flatten the multi-level columns
        pivot_df.columns = [f"{col[1]}_{col[0]}" for col in pivot_df.columns]

        # Reset index to make strike a column again
        pivot_df.reset_index(inplace=True)
        pivot_df = pivot_df.fillna(0)

        return {
            'df': pivot_df,

            'filtered_df' : filtered_df
        }
    except Exception as e:
        logger.error(f"Error calculating Change in OI for {symbol}: {str(e)}", exc_info=True)
        return {
            'df': pd.DataFrame(),
            'filtered_df': pd.DataFrame()
        }

def unpivoted_df(pivot_df):
    # First, melt the pivoted DataFrame to get back to a long format
    melted_df = pivot_df.melt(
        id_vars=['strike'],
        value_vars=[col for col in pivot_df.columns if col != 'strike'],
        var_name='temp',
        value_name='value'
    )

    # Split the combined column names back into original components
    melted_df[['instrument_type', 'metric']] = melted_df['temp'].str.split('_', n=1, expand=True)

    # Pivot again to separate the metrics into columns
    unpivoted_df = melted_df.pivot(
        index=['strike', 'instrument_type'],
        columns='metric',
        values='value'
    ).reset_index()

    # Rename columns if needed and reorder to match original
    # unpivoted_df.columns.name = None  # Remove the columns name
    # unpivoted_df = unpivoted_df[
    #     ['strike', 'instrument_type', 'current_price', 'oi', 'change_in_oi', 'volume', 'tradingsymbol',
    #      'instrument_token', 'lot_size']]

    # Replace any NaN values if needed
    unpivoted_df = unpivoted_df.fillna(0)

    # The result should now resemble the original filtered_df
    restored_df = unpivoted_df
    return restored_df

def place_order_15(Zerodha, df):

    data = df
    df = df.iloc[0]
    tradingsymbol = df.tradingsymbol
    length = len(tradingsymbol)
    type = tradingsymbol[-2:18]
    if type == 'CE':
        type_new = 'PE'
    else:
        type_new = 'CE'
    tradingsymbol = tradingsymbol[:length-2] + type_new
    logger.info("New trading symbol: %s", tradingsymbol)
    # get instrument token
    instruments = Zerodha.kite.instruments("NFO")
    instrument_df = pd.DataFrame(instruments)
    instrument_df = instrument_df[instrument_df['tradingsymbol'] == tradingsymbol]
    if not instrument_df.empty:
        instrument_token = instrument_df['instrument_token'].values[0]
        logger.info("Instrument token: %s", instrument_token)
    else:
        logger.error("Instrument token not found for trading symbol: %s", tradingsymbol)

    
    quote_data = Zerodha.kite.quote([f"NFO:{tradingsymbol}"]).get(f"NFO:{tradingsymbol}", {})
    price = quote_data.get('last_price', None)
    open = quote_data.get('ohlc', {}).get('open', None)
    low = quote_data.get('ohlc', {}).get('low', None)
    high = quote_data.get('ohlc', {}).get('high', None)
    quantity = quote_data.get('last_quantity',None)  # Assuming lot size is 25 for options
    order = Orders.objects.create(
                instrument_token=instrument_token,
                symbol=tradingsymbol,
                price=price,
                order_type=Zerodha.kite.ORDER_TYPE_LIMIT,
                quantity=quantity,
                product=Zerodha.PRODUCT_NRML,
                status='PENDING',
                exchange='NFO',  # Assuming NFO for this example
                strategy='ATH',
                stoploss=low,
                trigger_price=0
            )
    # if order:
    #     return order
    if order:
        from trading.cron_test import zerodha_place_order
        #result = sync_to_async(my_async_function)()
        executor = ThreadPoolExecutor(max_workers=4)
        executor.submit(zerodha_place_order)


# ndex(['strike', 'CE_instrument_token', 'PE_instrument_token',
#        'CE_exchange_token', 'PE_exchange_token', 'CE_tradingsymbol',
#        'PE_tradingsymbol', 'CE_name', 'PE_name', 'CE_last_price',
#        'PE_last_price', 'CE_expiry', 'PE_expiry', 'CE_tick_size',
#        'PE_tick_size', 'CE_lot_size', 'PE_lot_size', 'CE_segment',
#        'PE_segment', 'CE_exchange', 'PE_exchange', 'CE_prev_oi', 'PE_prev_oi',
#        'CE_prev_close', 'PE_prev_close', 'CE_current_price',
#        'PE_current_price', 'CE_change_in_price', 'PE_change_in_price',
#        'CE_change_in_price_percentage', 'PE_change_in_price_percentage',
#        'CE_oi', 'PE_oi', 'CE_change_in_oi', 'PE_change_in_oi',
#        'CE_change_in_oi_percentage', 'PE_change_in_oi_percentage', 'CE_volume',
#        'PE_volume'],
#       dtype='object')

def save_coi_background(instrument_df,symbol,instrument_token,current_price,expiry_date):
    try:
        instances = []
        now = timezone.now()
        for _, row in instrument_df.iterrows():
            instance = COI(
                symbol=symbol,
                instrument_token = instrument_token,
                strike=row['strike'],
                expiry_date=expiry_date,
                current_price=current_price,
                call_trading_symbol = row['CE_tradingsymbol'],
                call_instrument_token = row['CE_instrument_token'],
                call_oi = row['CE_oi'],
                call_coi = row['CE_change_in_oi'],
                call_coi_percentage = row['CE_change_in_oi_percentage'],
                call_volume = row['CE_volume'],
                call_last_price = row['CE_last_price'],
                call_lots = row['CE_lot_size'],
                call_pre_oi = row['CE_prev_oi'],
                call_current_price = row['CE_current_price'],
                call_day_low = row['CE_day_low'],
                call_day_high = row['CE_day_high'],
                call_day_open = row['CE_day_open'],

                put_trading_symbol = row['PE_tradingsymbol'],
                put_instrument_token = row['PE_instrument_token'],
                put_oi = row['PE_oi'],
                put_coi = row['PE_change_in_oi'],
                put_coi_percentage = row['PE_change_in_oi_percentage'],
                put_volume = row['PE_volume'],
                put_last_price = row['PE_last_price'],
                put_lots = row['PE_lot_size'],
                put_pre_oi = row['PE_prev_oi'],
                put_current_price = row['PE_current_price'],
                put_day_low = row['PE_day_low'],
                put_day_high = row['PE_day_high'],
                put_day_open = row['PE_day_open'],
                
                created_at=now,
                
            )
            instances.append(instance)
        
        # Use transaction for better performance
        with transaction.atomic():
            COI.objects.bulk_create(instances)
        
        #logger.info(f"Successfully saved {len(instances)} ChangeInOI records.")
    except Exception as e:
        logger.error(f"Error saving ChangeInOI records: {str(e)}", exc_info=True)

def save_coi(instrument_df,symbol,instrument_token,current_price,expiry_date):
    executor = ThreadPoolExecutor(max_workers=4)
    executor.submit(save_coi_background,instrument_df,symbol,instrument_token,current_price,expiry_date)


    return "Submitted to background task"







