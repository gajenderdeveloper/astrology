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
from trading.models import Orders,OrdersDetail
#from trading.cron_test import OrdersDetailStatusUpdate
#from .models import CronJob, CronJobExecution

import pandas as pd 
import numpy as np  
import time 
from time import sleep
from datetime import datetime, timedelta
# Configure logging 
logger = logging.getLogger(__name__)
from trading.utils import *
from trading.function import generate_stock_chart

def ATH_Strategy(kite,ohlc_df,symbol_df,ltp_data_nfo,ltp_data_nse,ltp_data):

    for index,row in symbol_df.iterrows():
        id = row['id']
        tradingsymbol = row['symbol']
        quantity = row['quantity']
        price = row['price']
        exchange = row['exchange']
        strategy = row['strategy']

        parent_symbol = row['parent_symbol']
        parent_token = row['parent_token']
        use_parent_symbol = row['use_parent_symbol']
        symbol_price = row['symbol_price']
        product_type = kite.PRODUCT_MIS # Default product type

        if exchange == 'NSE':
            product_type = kite.PRODUCT_MIS
            # Get the last price from ltp_data_nse
            #last_price = ltp_data_nse[exchange:tradingsymbol]['last_price']
            last_price = ltp_data_nse[f"{exchange}:{tradingsymbol}"]['last_price']
        elif exchange == 'NFO':
            product_type = kite.PRODUCT_NRML
            last_price = ltp_data_nfo[f"{exchange}:{tradingsymbol}"]['last_price']

        # exchange = 'NSE'
        # last_price_symbol = ltp_data[f"NSE:{parent_symbol}"]['last_price']

        if use_parent_symbol == '1':
            #last_price = last_price_symbol
            filtered_df = ohlc_df[ohlc_df['trading_symbol'] == parent_symbol]
        else:   
            filtered_df = ohlc_df[ohlc_df['trading_symbol'] == tradingsymbol]

        #get the last row of filtered_df
        last_row = filtered_df.iloc[-1]
        try:
            # Check if the last close price is greater than the price
            #price = 1
            #check for call coi data
            data =generate_stock_chart({'symbol':parent_symbol})
            COI_DATA = data['time_grouped']
            call = COI_DATA.iloc[-1]['call_coi']
            put = COI_DATA.iloc[-1]['put_coi']
            # for call buy condition
            coi_confirm = False
            if call < put :
                coi_confirm = True

            order_confirmed = False
            if strategy == 'ATH' and last_row['close'] > symbol_price:
                order_confirmed = True
            elif strategy == 'ATL' and last_row['close'] < symbol_price:
                order_confirmed = True
            
            if order_confirmed and coi_confirm:
                logger.info(f"Placing order for {tradingsymbol} at price {last_price}")
                # Place order logic here
                # Example: kite.place_order(...)
                order_id = kite.place_order(
                    variety=kite.VARIETY_REGULAR,
                    exchange=exchange,
                    tradingsymbol=tradingsymbol,
                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                    quantity=quantity,
                    price=last_price,
                    product=product_type,
                    order_type=kite.ORDER_TYPE_LIMIT
                )

                #order_id = '251117151316667' # order id test
                
                order_details = kite.kite.order_history(order_id)
                order_details = order_details[-1]
                order_status = order_details['status']
                order_message = order_details['status_message']

                # update the order in the database
                order = Orders.objects.get(id=id)
                order.order_id = order_id
                order.status = order_status
                order.error_message = order_message
                order.filled_quantity = order_details['filled_quantity']
                order.pending_quantity = order_details['pending_quantity']
                order.average_price = order_details['average_price']
                order.updated_at = timezone.now()
                order.response = str(order_details)
                order.save()

                #insert into OrdersDetail
                if order_status != 'REJECTED':
                   
                    OrdersDetail.objects.create(
                        order=order,
                        broker_order_id=order_id,
                        status=order_status,
                        exchange=exchange,
                        symbol=tradingsymbol,
                        strategy=strategy,
                        product=product_type,
                        transaction_type=kite.TRANSACTION_TYPE_BUY,
                        instrument_token=last_row['instrument_token'],
                        price=last_price,

                        quantity=quantity,
                        filled_quantity=order_details['filled_quantity'],
                        pending_quantity=order_details['pending_quantity'],
                        average_price=order_details['average_price'],
                        stoploss = order.stoploss,
                        trigger_price = order.trigger_price,
                        parent_symbol = order.parent_symbol,
                        parent_token = order.parent_token,
                        symbol_price = order.symbol_price,
                        option_type = order.option_type,
                        response=str(order_details)
                    )
                else:
                    logger.error(f"Order for {tradingsymbol} was rejected: {order_message}")

                if order_status == 'OPEN':
                    logger.info(f"Order for {tradingsymbol} is OPEN, placing stoploss order")
                    sleep(5)  # Wait for a second before placing stoploss order
                    #OrdersDetailStatusUpdate(kite)




                
            else:
                logger.info(f"Skipping order for {tradingsymbol}-{parent_symbol} as last close price {last_row['close']} is not greater than {symbol_price}")
                logger.info(f" {coi_confirm } and put{put} > call{call}")
        except Exception as e:
            logger.error(f"Error placing order for {tradingsymbol}: {str(e)}")      
        
        
    #print(df)
