from django.shortcuts import render
import os
import sys
import django

import datetime, time
import pandas as pd 
from trading.models import *
from ZERODHA_API.zerodha_integration import *
from django.http import JsonResponse
from django.conf import settings
from trading.cron_test import zerodha_place_order
from asgiref.sync import sync_to_async
from concurrent.futures import ThreadPoolExecutor
def get_quote(request):
    instrument = request.GET.get('instrument')
    kite = ZerodhaAPI()
    try:
        quote = kite.get_quote(instrument)
        print("=========api for quote=========")
        # Extract instrument data from quote
        #print(quote)
        instrument_data = quote[str(instrument)]
        # print(instrument_data)

        margins = kite.get_margins()
        equity_margins = margins["equity"]
       
        #print(data)

        return JsonResponse({'success': True, 'instrument': instrument,
                             'instrument_data':instrument_data,
                             'equity_margins':equity_margins
                             })
    except Exception as e:  
        return JsonResponse({'error': str(e)}, status=400)

# async def my_async_function():
#     # Your async code here
#     zerodha_place_order()
    return "result"    
def place_order(request):
    
    if request.method == 'POST':
        try:
            # Initialize KiteConnect with your API key and access token
            kite = ZerodhaAPI()

            # Get order parameters from request
            instrument_token = request.POST.get('instrument_token')
            tradingsymbol = request.POST.get('tradingsymbol')
            price = float(request.POST.get('price'))
            order_type = request.POST.get('order_type')
            quantity = int(request.POST.get('quantity'))
            product_type = request.POST.get('product_type')
            strategy = request.POST.get('strategy_type')

            parent_symbol = request.POST.get('parent_symbol')
            parent_token = request.POST.get('symbol_instrument')
            use_parent_symbol = request.POST.get('use_parent_symbol')
            symbol_price = float(request.POST.get('symbol_price'))
            option_type = request.POST.get('option_type')

            
            # Place order
            # order_id = kite.place_order(
            #     variety=kite.VARIETY_REGULAR,
            #     exchange=kite.EXCHANGE_NFO,
            #     tradingsymbol=tradingsymbol,
            #     transaction_type=order_type,
            #     quantity=quantity,
            #     price=price,
            #     product=product_type,
            #     order_type=kite.ORDER_TYPE_LIMIT
               
            # )
            if request.POST.get('stoploss'):
                stoploss = float(request.POST.get('stoploss'))
            else:
                stoploss = symbol_price - symbol_price * 0.05

            if request.POST.get('trigger_price'):
                trigger_price = float(request.POST.get('trigger_price'))
            else:
                trigger_price = symbol_price + symbol_price * 0.30


            #order_id = 'sasad'
            
            order = Orders.objects.create(
                instrument_token=instrument_token,
                symbol=tradingsymbol,
                price=price,
                order_type=order_type,
                quantity=quantity,
                product=product_type,
                status='PENDING',
                exchange='NFO',  # Assuming NFO for this example
                strategy=strategy,
                stoploss=stoploss,
                trigger_price=trigger_price,

                parent_symbol = parent_symbol,
                parent_token = parent_token,
                use_parent_symbol = use_parent_symbol,
                symbol_price = symbol_price,
                option_type = option_type
                
            )
            if order:
               #result = sync_to_async(my_async_function)()
               executor = ThreadPoolExecutor(max_workers=4)
               executor.submit(zerodha_place_order)
                
            return JsonResponse({'success': True, 'order_id': order.id})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_instrment(request):
    try:
        kite = ZerodhaAPI()
        # Initialize KiteConnect with your API key and access token
        instrument_file = os.path.join(settings.PROJECT_DIR,'astrology','ZERODHA_API','instruments.csv')
        instruments_df = pd.read_csv(instrument_file)
        
        if request.GET.get('exchange'):
            exchange = request.GET.get('exchange')
            if exchange == 'NFO':
                segment = 'NFO-OPT'
            if exchange == 'NSE':
                segment = 'NSE'

            filtered_instruments = instruments_df[
                (instruments_df['exchange'] == exchange) & 
                (instruments_df['segment'] == segment)
            ]
        if request.GET.get('symbol'):
            symbol = request.GET.get('symbol')
            filtered_instruments = filtered_instruments[
                filtered_instruments['tradingsymbol'] == symbol
            ]
        

        #print(filtered_instruments.head())
        # Convert DataFrame to a list of dictionaries
        filtered_instruments = filtered_instruments.fillna('')
        instruments_list = filtered_instruments.to_dict(orient='records')       
        symbols_details = instruments_list[0]
        
        
        quote = kite.get_quote(symbols_details['instrument_token'])

        last_price = quote.get(str(symbols_details['instrument_token']), {}).get('last_price', 0)
        # stoplose 5 percentage of last price
        #last_price = 100
        stoploss = last_price - last_price * 0.05
        target = last_price + last_price * 0.10
        
        

        data = {
            
            'instruments': instruments_list,
            'symbols_details': symbols_details,
            'quote': quote.get(str(symbols_details['instrument_token']), {}),
            'last_price': last_price,
            'stoploss': stoploss,
            'target': target
            }
       
       
        
        return JsonResponse({'success': True,'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
