from django.shortcuts import render, redirect
from datetime import datetime, time, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string
import pandas as pd 
import matplotlib.pyplot as plt
from io import BytesIO
import base64
#import plotly.graph_objects as go
import plotly.graph_objects as go

import os
import sys
import django
from django.conf import settings
# Add the Django project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astrology.settings')
django.setup()

from trading.models import Change_IN_OI_Increasing,ScaningStockOI,Scanner_ema,PreMarketStock,COI,MostActiveSymbol
from trading.color_coi import *
from trading.function import *
from asyncio import create_task, sleep
from django.http import JsonResponse
from .nse_options import MostActiveContracts
import requests

from ZERODHA_API.zerodha_integration import ZerodhaAPI

PROJECT_PATH = os.path.dirname(settings.BASE_DIR)
# instrument_file = os.path.join(PROJECT_PATH,'astrology','DATA','instruments.csv')
# instruments_df = pd.read_csv(instrument_file)
# print("instruments_df columns=",instruments_df.columns)

symbol_list_df = pd.read_csv(os.path.join(PROJECT_PATH,'astrology','DATA','symbol_list.csv'))



def scanner_increase_coi(request):
    # Get today's date
    try :
        today = datetime.now().date()
        # Get tomorrow's date as string in the format stored in created_at
        # Convert today's date to timestamp for start of day
        today_start = datetime.combine(today, time.min)
        
        
        # Get yesterday's date and convert to timestamp
        yesterday = today_start - pd.Timedelta(days=3)
        yesterday_start = datetime.combine(yesterday.date(), time.min)
        print("yesterday_start=",yesterday_start)

        # Query records after yesterday's start time
        top_stocks = Change_IN_OI_Increasing.objects.filter(
            created_at__gte=yesterday_start
        ).order_by('-id')
        

        # top_stocks = pd.DataFrame.from_records(top_stocks.values())
        # print(top_stocks)


        # top_stocks = pd.DataFrame.from_records(future_records.values())
        # print(top_stocks)
    
        #top_stocks = Change_IN_OI_Increasing.objects.order_by('-change_in_oi_percentage')

        df = pd.DataFrame.from_records(top_stocks.values())
        print("DataFrame of top stocks:========")
        print(df)
        if df.empty:
            # If no records found, return an empty DataFrame
            return JsonResponse({'message': 'No records found for the last 24 hours.'})
        #print(df)
        date_unique = df['created_at'].unique()
        date_unique = date_unique.tolist()
        date_unique.sort(reverse=True)

        if request.GET.get('created_date'):
            created_last = request.GET.get('created_date')
            
        else:
            created_last = date_unique[0]
            
        
        # Find the index of the current date
        current_index = date_unique.index(created_last)

        # Get the previous date (next in the list since it's sorted newest to oldest)
        if current_index + 1 < len(date_unique):
            previous_date = date_unique[current_index + 1]
        else:
            previous_date = None  # No older dates available

        #print(f"=================Current date: {created_last}, Previous date: {previous_date}")

        #created_last = date_unique[0] if date_unique else None
        df_current = df[df['created_at'] == created_last]
        df_previous = df[df['created_at'] == previous_date]

        # print(df_current)
        # print(df_previous)

        # Get symbols from current and previous dataframes
        current_symbols = set(df_current['tradingsymbol'])
        previous_symbols = set(df_previous['tradingsymbol']) if not df_previous.empty else set()

        # Find symbols that are in current but not in previous
        new_symbols = current_symbols - previous_symbols

        # Filter df_current to only show new symbols
        df_current_new = df_current[df_current['tradingsymbol'].isin(new_symbols)]

        # print("New symbols in current data:")
        # print(df_current_new['tradingsymbol'].tolist())

        # Add new column 'is_new' based on whether symbol is in new_symbols set
        df_current['is_new'] = df_current['tradingsymbol'].isin(new_symbols)
        #df_current sort by change_in_oi_percentage descending

        #df_current = df_current.sort_values(by='change_in_oi_percentage', ascending=False)
        df_current = df_current.sort_values(by='change_in_oi_percentage_quantity', ascending=False)

        df_test = df_current.head(10)
        df_test = df_test[['tradingsymbol','change_in_oi_percentage_quantity']]
        print(df_test)

        max_coi_quantity = df_current.sort_values(by='change_in_oi_quantity', ascending=False).head(3)
        max_coi_quantity = max_coi_quantity['change_in_oi_quantity'].tolist()
        # print("Max COI Quantity:")
        # print(max_coi_quantity)

        #print(df_current)
        # Handle CSV download if requested
        if request.GET.get('d') == '1':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="scanner_data_{created_last}.csv"'
            df_download = df_current[['tradingsymbol','prev_oi_quantity','oi_quantity','change_in_oi_quantity','change_in_oi_percentage_quantity','oi','change_in_oi','change_in_oi_percentage','current_price','previous_close','change_in_price','change_in_price_percentage']]
            df_download.to_csv(path_or_buf=response, index=False)
            return response

        context = {
            'df': df_current,
            'date_unique': date_unique,
            'created_date': created_last,
            'max_coi_quantity':max_coi_quantity
        }
        
        return render(request, 'trading/scanner_increase_coi.html', context)
    except Exception as e:
        print(f"Error in scanner_increase_coi: {e}")
        return JsonResponse({'error': str(e)})


def scanner_coi(request):
    try:
        top_stocks = ScaningStockOI.objects.order_by('-total_coi_call')

        df = pd.DataFrame.from_records(top_stocks.values())
        df['created_at'] = pd.to_datetime(df['created_at']).dt.date
        date_unique = df['created_at'].unique()
        date_unique = date_unique.tolist()
        date_unique.sort(reverse=True)

        if request.GET.get('created_date'):
            created_last = request.GET.get('created_date')
            
        else:
            created_last = date_unique[0]
            
        
        # Find the index of the current date
        current_index = date_unique.index(created_last)

        # Get the previous date (next in the list since it's sorted newest to oldest)
        if current_index + 1 < len(date_unique):
            previous_date = date_unique[current_index + 1]
        else:
            previous_date = None  # No older dates available

        print(f"=================Current date: {created_last}, Previous date: {previous_date}")

        #created_last = date_unique[0] if date_unique else None
        df_current = df[df['created_at'] == created_last]
        df_current = df_current.sort_values(by='total_coi_call', ascending=True)

        #df_current filter by type
        df_current_call = df_current[df_current['type'] == 'call']
        df_current_put = df_current[df_current['type'] == 'put']

        print(df_current)

        context = {
            'df': df_current_call,
            'df_put': df_current_put,
            'date_unique': date_unique,
            'created_date': created_last,
        }
        
        return render(request, 'trading/scanner_coi.html', context)
    except Exception as e:
        # print(f"Error in scanner_coi: {e}")
        # return JsonResponse({'error': str(e)})
        return render(request, 'trading/error_page.html', {'error': str(e)})


def scanner_200ma(request):
    data = Scanner_ema.objects.order_by('-id')
    today = datetime.now().date()
    df = pd.DataFrame.from_records(data.values())

    # Handle CSV download if requested
    if request.GET.get('d') == '1':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="scanner_rsi_{today}.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response
    context = {
        'df': df
       
    }
    return render(request, 'trading/scanner.html', context)


async def async_view(request):
    # Create a background task
    create_task(long_running_task(request.POST))
    return JsonResponse({"status": "task started"})

async def long_running_task(data):
    print("===Starting long-running task with data:", data)
    await sleep(1)  # Simulate long operation
    # Process data here
    print("Task completed with data:", data)


def pre_market(request):
    # Get today's date
    try :
        today = datetime.now().date()
        # Get tomorrow's date as string in the format stored in created_at
        # Convert today's date to timestamp for start of day
        today_start = datetime.combine(today, time.min)
        
        
        # Get yesterday's date and convert to timestamp
        yesterday = today_start - pd.Timedelta(days=5)
        yesterday_start = datetime.combine(yesterday.date(), time.min)
        print("yesterday_start=",yesterday_start)

        # Query records after yesterday's start time
        stock = PreMarketStock.objects.filter(
            created_at__gte=yesterday_start
        ).order_by('id')
        
        df = pd.DataFrame.from_records(stock.values())
        if df.empty:
            # If no records found, return an empty DataFrame
            return JsonResponse({'message': 'No records found for the last 24 hours.'})
        df = df.sort_values(by='change_percentage', ascending=False)
        print("DataFrame of top pre stocks:========")
        print(df)
        
        #print(df)
        # Convert created_at column to date format
        df['date'] = df['created_at']
        df['created_at'] = pd.to_datetime(df['created_at']).dt.date
        
        date_unique = df['created_at'].unique()
        date_unique = date_unique.tolist()
        date_unique.sort(reverse=True)
        

        if request.GET.get('created_date'):
            created_last = request.GET.get('created_date')
        else:
            created_last = date_unique[0]

        # convert created_last to date
        created_last = pd.to_datetime(created_last).date()
        print("==================Created last:", created_last)

        type_list = [('PRE-MARKET', 'pre-market'), ('POST-MARKET', 'post-market'),('MARKET', 'market') ]
        if request.GET.get('type'):
            type = request.GET.get('type')
        else:
            type = type_list[0][0]

        #created_last = date_unique[0] if date_unique else None
        df_current = df[df['created_at'] == created_last]
        #filter by created_at
        df_current = df[df['created_at'] == created_last]
        print("==================df_current:", df_current)
        df_current = df_current[df_current['type'] == type]
        current_symbols = set(df_current['symbol'])

        max_voulume = df_current['volume'].max()

        #df_current = df_current.sort_values(by='change_in_oi_percentage', ascending=False)
        df_current = df_current.sort_values(by='change_percentage', ascending=False)

        #print(df_current)
        # Handle CSV download if requested
        # if request.GET.get('d') == '1':
        #     response = HttpResponse(content_type='text/csv')
        #     response['Content-Disposition'] = f'attachment; filename="scanner_data_{created_last}.csv"'
        #     df_download = df_current[['symbol','prev_oi_quantity','oi_quantity','change_in_oi_quantity','change_in_oi_percentage_quantity','oi','change_in_oi','change_in_oi_percentage','current_price','previous_close','change_in_price','change_in_price_percentage']]
        #     df_download.to_csv(path_or_buf=response, index=False)
        #     return response

        context = {
            'df': df_current,
            'date_unique': date_unique,
            'created_date': created_last,
            #'max_coi_quantity':max_coi_quantity
            'type_list': type_list,
            'type': type,
            'max_voulume':max_voulume
        }
        
        return render(request, 'trading/pre_market.html', context)
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)})



@login_required(login_url='/loginpage')
def option_chain_coi(request, symbol_name):
    symbol_name_original = symbol_name
    # instruments_df = instruments_df[(instruments_df["segment"] == 'NFO-OPT')]
    # symbol = instruments_df['name'].unique()
    # symbols_list = symbol.tolist()
    # symbols_list = [item for item in symbols_list if item not in ['NIFTY','BANKNIFTY','360ONE']]
    # print("===================symbols_list=",symbols_list)
    symbols_list = symbol_list_df['symbol'].unique().tolist()
    symbols_list = [item for item in symbols_list if item not in ['NIFTY','BANKNIFTY','360ONE','PGEL']]
    
    if request.GET.get('expiry'):
        expiry_date = request.GET.get('expiry')
    else:
        expiry_date = settings.EXPIRY

    print("===================gajender")
    try:
        now = datetime.now()
        if request.GET.get('date'):
            date_str = request.GET.get('date')
        else:
            date_str = now.strftime("%Y-%m-%d")
        
        if symbol_name:
                symbol_name = symbol_name.upper()
        else:
            symbol_name = 'ABB'
        
        created_date = pd.to_datetime(date_str).date()
        print("====================created_date",date_str)
        result = COI.objects.filter(created_at__date=created_date,symbol=symbol_name).order_by('-id')
        # if result.count() == 0:
        #     created_date = pd.to_datetime(now - timedelta(days=1)).date()
        #     result = COI.objects.filter(created_at__date=created_date,symbol=symbol_name).order_by('-id')


        df = pd.DataFrame.from_records(result.values())
        if df.empty:
            return render(request, 'trading/error_page.html', {'error': f'No COI data found for {symbol_name} on {date_str}'})
            # df = pd.DataFrame(columns=['symbol','strike','call_trading_symbol','put_trading_symbol','created_at','current_price','call_oi','call_prev_oi','call_change_in_oi','call_change_in_oi_percentage','call_volume','call_iv','call_ltp','call_net_change','call_bid_qty','call_ask_qty','call_open_interest_value','call_day_high','call_day_low','call_day_open'])
        
        df = df.sort_values(by='id', ascending=True)
        # dataframe date format
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        #add column date and time
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        df['time'] = pd.to_datetime(df['created_at']).dt.strftime('%H:%M')
       

        #date_unique = df['date'].unique()
        time_unique = df['time'].unique()
        time_unique = time_unique.tolist()
        time_unique.sort( reverse=True)
        #print(date_unique)
        #print(time_unique)
        if request.GET.get('time'):
            time_selected = request.GET.get('time')
        else:
            time_selected = time_unique[0]
        # list date for last 7 days
        # Get the current date
        today = datetime.now().date()
        # date_list = []
        # for i in range(7):
        #     # Calculate the date by subtracting 'i' days from today
        #     past_date = today - timedelta(days=i)
        #     date_list.append(past_date)
        # print(date_list)
        date_range = pd.date_range(start=(today - timedelta(days=7)), end=today, freq='D')
        date_list = [date.date() for date in date_range]
        date_list = [d.strftime('%Y-%m-%d') for d in date_list]
        date_list.reverse()  # Reverse the list to have the most recent date first
        print(date_list)
            
        
        
        df = df[df['time'] == time_selected]
        #print(df[['symbol','strike','call_trading_symbol','put_trading_symbol','created_at','date','time','current_price']].head(10))
        last_price = df['current_price'].values[0]
        #print("last_price=",last_price)
       

        # df2 = result['df']
        # print(df2.columns)
        # print(df2[['strike','CE_oi','CE_prev_oi','CE_change_in_oi','CE_instrument_token']])
        
        

        max_volume_CE = df['call_volume'].max()
        second_largest_volume_CE = df['call_volume'].sort_values(ascending=False).iloc[1]

        max_volume_PE  = df['put_volume'].max()
        second_largest_volume_PE = df['put_volume'].sort_values(ascending=False).iloc[1]

        # # for change in oi
        max_coi_CE = df['call_coi'].max()
        second_largest_coi_CE = df['call_coi'].sort_values(ascending=False).iloc[1]
        min_coi_CE = df['call_coi'].min()
       

        max_coi_PE  = df['put_coi'].max()
        second_largest_coi_PE = df['put_coi'].sort_values(ascending=False).iloc[1]
        min_coi_PE = df['put_coi'].min()


        max_CE_oi = df['call_oi'].max()
        second_largest_CE_oi = df['call_oi'].sort_values(ascending=False).iloc[1]
        min_CE_oi = df['call_oi'].min()

        max_PE_oi = df['put_oi'].max()
        second_largest_PE_oi = df['put_oi'].sort_values(ascending=False).iloc[1]
        min_PE_oi = df['put_oi'].min()
        
        
        
        #print(df)
        # get current price
        
       
        df['CE_color'] = df.apply(CE_color,axis=1,args=(last_price,))
        df['PE_color'] = df.apply(PE_color,axis=1,args=(last_price,)) 

        df['CE_color_volume'] = df.apply(CE_color_volume,axis=1,args=(max_volume_CE, second_largest_volume_CE,last_price))
        df['PE_color_volume'] = df.apply(PE_color_volume,axis=1,args=(max_volume_PE, second_largest_volume_PE,last_price)) 

        df['CE_color_change_in_oi'] = df.apply(CE_color_change_in_oi,axis=1,args=(max_coi_CE, second_largest_coi_CE, min_coi_CE,last_price))
        df['PE_color_change_in_oi'] = df.apply(PE_color_change_in_oi,axis=1,args=(max_coi_PE, second_largest_coi_PE, min_coi_PE,last_price)) 

        df['CE_color_total_oi'] = df.apply(CE_color_total_oi, axis=1, args=(
            max_CE_oi, second_largest_CE_oi, min_CE_oi, last_price))
        df['PE_color_total_oi'] = df.apply(PE_color_total_oi, axis=1, args=(
            max_PE_oi, second_largest_PE_oi, min_PE_oi, last_price))
       
        
        #print(df[['strike','CE_color_total_oi','PE_color_total_oi']])
        
        #print(dict)
        #expiry_list = result['unique_expiry']
        context = {
                'expiry_date':expiry_date,
                'date_str':date_str,
                'symbol_name' : symbol_name_original,
                'symbol_list' : symbols_list,
                'current_price' : last_price,
                'df': df,
                'max_volume_CE':max_volume_CE,
                'second_largest_volume_CE' : second_largest_volume_CE,
                # 'max_volume_PE':max_volume_PE,
                # 'second_largest_volume_PE' : second_largest_volume_PE,

                # 'max_coi_CE':max_coi_CE,
                # 'second_largest_coi_CE' : second_largest_coi_CE,
                # 'max_coi_PE':max_coi_PE,
                # 'second_largest_coi_PE' : second_largest_coi_PE,
                # 'expiry_list' : expiry_list
                'time':time_unique,
                'time_selected':time_selected,
                'date_list':date_list,
                
            }
        return render(request, 'trading/coi_data.html',context )

        
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'Error': {str(e)}})

@login_required(login_url='/loginpage')
def option_chain_coi_chart(request, symbol_name):
    symbol_name_original = symbol_name

    Zerodha = ZerodhaAPI()
    quote_data = Zerodha.kite.quote([f"NSE:{symbol_name}"])
    symbol_instrument = quote_data[f"NSE:{symbol_name}"].get('instrument_token')
    symbol_lastprice = quote_data[f"NSE:{symbol_name}"].get('last_price')
    print("quote_data++++++++++++++++",quote_data)

    # instruments_df = instruments_df[(instruments_df["segment"] == 'NFO-OPT')]
    # symbol = instruments_df['name'].unique()
    # symbols_list = symbol.tolist()
    # symbols_list = [item for item in symbols_list if item not in ['NIFTY','BANKNIFTY','360ONE']]
    # print("===================symbols_list=",symbols_list)
    symbols_list = symbol_list_df['symbol'].unique().tolist()
    symbols_list = [item for item in symbols_list if item not in ['NIFTY','BANKNIFTY','360ONE','PGEL']]
    
    if request.GET.get('expiry'):
        expiry_date = request.GET.get('expiry')
    else:
        expiry_date = settings.EXPIRY

    print("===================option_chain_coi_chart gajender")
    try:
        now = datetime.now()
        if request.GET.get('date'):
            date_str = request.GET.get('date')
        else:
            date_str = now.strftime("%Y-%m-%d")
            #date_str = '2025-08-29'
        
        if symbol_name:
                symbol_name = symbol_name.upper()
        else:
            symbol_name = 'ABB'
        
        
        
        holiday_list = ['2025-11-05','2025-12-25']
        current_time = datetime.now().time()
        # print("Current time-------------------:option_chain_coi_chart", current_time)
        # print("Today's date for chart data:", time(1,7))
        # print("Today's date for chart data:", time(9,14))
        if time(1, 7) <= current_time <= time(9, 14):
            today = datetime.now().date()-timedelta(days=1)
        else:
            today = datetime.now().date()
            
        if today.strftime('%Y-%m-%d') in holiday_list:
            today = today - timedelta(days=1)
        

        if request.GET.get('date'):
            date_str = request.GET.get('date')
            created_date = pd.to_datetime(date_str).date()
        else:
            created_date = today
        
        date_range = pd.date_range(start=(today - timedelta(days=7)), end=today, freq='D')
        date_list = [date.date() for date in date_range]
        date_list = [d.strftime('%Y-%m-%d') for d in date_list]
        date_list.reverse()  # Reverse the list to have the most recent date first
        print(date_list)

        result = COI.objects.filter(created_at__date=created_date,symbol=symbol_name).order_by('-id')



        df = pd.DataFrame.from_records(result.values())
        if df.empty:
            context = {
                'expiry_date':'',
                'date_str':date_str,
                'symbol_name' : symbol_name_original,
                'symbol_list' : symbols_list,
                'current_price' : '',
                'df': df,
                'max_volume_CE':'',
                'second_largest_volume_CE' : '',

                'time':'',
                'time_selected':'',
                'date_list':date_list,
                
            }
            context['chart'] = ''
            context['total_call_coi'] = ''
            return render(request, 'trading/coi_data_chart.html',context )
          
        
        df = df.sort_values(by='id', ascending=True)
        # dataframe date format
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        #add column date and time
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        df['time'] = pd.to_datetime(df['created_at']).dt.strftime('%H:%M')
       

        #date_unique = df['date'].unique()
        time_unique = df['time'].unique()
        time_unique = time_unique.tolist()
        time_unique.sort( reverse=True)
        #print(date_unique)
        #print(time_unique)
        if request.GET.get('time'):
            time_selected = request.GET.get('time')
        else:
            time_selected = time_unique[0]
        # list date for last 7 days
        # Get the current date
        
            
        
        
        df = df[df['time'] == time_selected]
        print(df[['symbol','strike','call_trading_symbol','put_trading_symbol','created_at','date','time','current_price']].head(10))
        last_price = df['current_price'].values[0]
        print("last_price=",last_price)
       

        # df2 = result['df']
        # print(df2.columns)
        # print(df2[['strike','CE_oi','CE_prev_oi','CE_change_in_oi','CE_instrument_token']])
        
        

        max_volume_CE = df['call_volume'].max()
        second_largest_volume_CE = df['call_volume'].sort_values(ascending=False).iloc[1]

        max_volume_PE  = df['put_volume'].max()
        second_largest_volume_PE = df['put_volume'].sort_values(ascending=False).iloc[1]

        # # for change in oi
        max_coi_CE = df['call_coi'].max()
        second_largest_coi_CE = df['call_coi'].sort_values(ascending=False).iloc[1]
        min_coi_CE = df['call_coi'].min()
       

        max_coi_PE  = df['put_coi'].max()
        second_largest_coi_PE = df['put_coi'].sort_values(ascending=False).iloc[1]
        min_coi_PE = df['put_coi'].min()


        max_CE_oi = df['call_oi'].max()
        second_largest_CE_oi = df['call_oi'].sort_values(ascending=False).iloc[1]
        min_CE_oi = df['call_oi'].min()

        max_PE_oi = df['put_oi'].max()
        second_largest_PE_oi = df['put_oi'].sort_values(ascending=False).iloc[1]
        min_PE_oi = df['put_oi'].min()
        
        
        
        #print(df)
        # get current price
        
       
        df['CE_color'] = df.apply(CE_color,axis=1,args=(last_price,))
        df['PE_color'] = df.apply(PE_color,axis=1,args=(last_price,)) 

        df['CE_color_volume'] = df.apply(CE_color_volume,axis=1,args=(max_volume_CE, second_largest_volume_CE,last_price))
        df['PE_color_volume'] = df.apply(PE_color_volume,axis=1,args=(max_volume_PE, second_largest_volume_PE,last_price)) 

        df['CE_color_change_in_oi'] = df.apply(CE_color_change_in_oi,axis=1,args=(max_coi_CE, second_largest_coi_CE, min_coi_CE,last_price))
        df['PE_color_change_in_oi'] = df.apply(PE_color_change_in_oi,axis=1,args=(max_coi_PE, second_largest_coi_PE, min_coi_PE,last_price)) 

        df['CE_color_total_oi'] = df.apply(CE_color_total_oi, axis=1, args=(
            max_CE_oi, second_largest_CE_oi, min_CE_oi, last_price))
        df['PE_color_total_oi'] = df.apply(PE_color_total_oi, axis=1, args=(
            max_PE_oi, second_largest_PE_oi, min_PE_oi, last_price))
        
        #total_call_coi = df['call_coi'].sum()
        #total_put_coi = df['put_coi'].sum()

        total_call_coi = df.loc[df['call_coi'] > df['current_price'], 'call_coi'].sum()
        total_put_coi = df.loc[df['put_coi'] < df['current_price'], 'put_coi'].sum()
        
        #print(df[['strike','CE_color_total_oi','PE_color_total_oi']])
        
        #print(dict)
        #expiry_list = result['unique_expiry']
        #######################################################
        ############# Plotly Chart ############################
        #######################################################
        print("=================chart start==================")
        df_chart = pd.DataFrame.from_records(result.values())
        df_chart = df_chart.sort_values(by='id', ascending=True)
        # dataframe date format
        df_chart['created_at'] = pd.to_datetime(df_chart['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        #add column date and time
        df_chart['date'] = pd.to_datetime(df_chart['created_at']).dt.date
        df_chart['time'] = pd.to_datetime(df_chart['created_at']).dt.strftime('%H:%M')
        
        print(df_chart.columns)
        print(df_chart[['symbol','strike','call_trading_symbol','put_trading_symbol','created_at','date','time','current_price']].head(10))

        # creted date unique values
        df_final = pd.DataFrame()
        created_date = df_chart['created_at'].unique()
        for date in created_date:
            #print("Created Date:", date)
            df_date = df_chart[df_chart['created_at'] == date]
            current_price = df_date['current_price'].iloc[-1]
            df_call = df_date[(df_date['strike'] >= current_price)]
            df_put = df_date[(df_date['strike'] <= current_price)]    
            df_call_put = pd.concat([df_put.tail(3),df_call.head(3)])
            df_final = pd.concat([df_final, df_call_put])
        try:
            # Create bar chart data for call and put COI by time
            # Group by time and calculate mean COI values
            df_chart = df_final.copy()
            time_grouped = df_chart.groupby('time').agg({
                'call_coi': lambda x: df_chart.loc[x.index, 'call_coi'][df_chart.loc[x.index, 'strike'] > df_chart.loc[x.index, 'current_price']].sum(),
                'put_coi': lambda x: df_chart.loc[x.index, 'put_coi'][df_chart.loc[x.index, 'strike'] < df_chart.loc[x.index, 'current_price']].sum(),
                
                'current_price': 'first',  # Assuming price_time is same for all entries at a given time
                'call_volume': 'sum' 
            }).reset_index()
            # Create the bar chart using Plotly
            print(time_grouped)

            fig = go.Figure()

            
            # Add line for call COI
            fig.add_trace(go.Scatter(
                x=time_grouped['time'],
                y=time_grouped['call_coi'],
                name='Call COI',
                line=dict(color='green', width=2),
                mode='lines+markers'  # You can change this to just 'lines' if you prefer no markers
            ))
            # Add line for put COI 
            fig.add_trace(go.Scatter(
                x=time_grouped['time'],
                y=time_grouped['put_coi'],
                name='Put COI',
                line=dict(color='red', width=2),
                mode='lines+markers'  # You can change this to just 'lines' if you prefer no markers
            ))
            # Add line for current price (assuming you have a 'current_price' column)
            fig.add_trace(go.Scatter(
                x=time_grouped['time'],
                y=time_grouped['current_price'],  # Replace with your actual column name
                name='Current Price',
                line=dict(color='blue', width=2),
                mode='lines+markers',
                yaxis='y2'  # Use secondary y-axis for price
            ))

            # Add volume bar chart (row 2, col 1)
            # fig.add_trace(go.Bar(
            #     x=time_grouped['time'],
            #     y=time_grouped['call_volume'],
            #     name='Call Volume',
            #     marker_color='rgba(100, 100, 100, 0.6)',  # Gray color with transparency
            #     opacity=0.7
            # ), row=2, col=1)

            fig.update_layout(
                height=600,
                title='Call vs Put COI and Current Price by Time',
                xaxis_title='Time',
                yaxis_title='Change in Open Interest',
                yaxis2=dict(
                    title='Price',
                    # titlefont=dict(color='blue'),
                    tickfont=dict(color='blue'),
                    overlaying='y',
                    side='right'
                ),
                showlegend=True,
                
            )
            chart_html = fig.to_html(full_html=False)
        except Exception as e:
            print(f"Error in plotting chart: {e}")
            chart_html = f"Error in plotting chart: {e}"
        print("=================chart end==================")
        #######################################################
        ############# End Plotly Chart ########################
        df['call_lots'] = df['call_lots'].astype(int)
        #print(df[['symbol','call_lots','CE_color_total_oi','PE_color_total_oi']])
        context = {
                'expiry_date':expiry_date,
                'date_str':date_str,
                'symbol_name' : symbol_name_original,
                'symbol_list' : symbols_list,
                'current_price' : last_price,
                'df': df,
                'max_volume_CE':max_volume_CE,
                'second_largest_volume_CE' : second_largest_volume_CE,
                # 'max_volume_PE':max_volume_PE,
                # 'second_largest_volume_PE' : second_largest_volume_PE,
                # 'max_coi_CE':max_coi_CE,
                # 'second_largest_coi_CE' : second_largest_coi_CE,
                # 'max_coi_PE':max_coi_PE,
                # 'second_largest_coi_PE' : second_largest_coi_PE,
                # 'expiry_list' : expiry_list
                'time':time_unique,
                'time_selected':time_selected,
                'date_list':date_list,
                'symbol_lastprice':symbol_lastprice,
                'symbol_instrument':symbol_instrument
            }
        context['chart'] = chart_html
        context['total_call_coi'] = total_call_coi
        context['total_put_coi'] = total_put_coi
       
        return render(request, 'trading/coi_data_chart.html',context )

        
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'Error': {str(e)}})


def most_active_contracts(request):
    #print(f"Fetching most active contracts for index: {index}")
    try :
        if request.GET.get('index'):
            index = request.GET.get('index')
        else:
            index = 'calls-stocks-vol'
        print("index=========",index)
        

        # index_call = 'calls-stocks-vol'
        # active_call = MostActiveContracts(index_call)
        # data_call = active_call.fetch_data()
        # print("data_call==================",data_call)

        # index_put = 'puts-stocks-vol'
        # active_put = MostActiveContracts(index_put)
        # data_put = active_put.fetch_data()
        # print("data_put==================",data_put)

        # # if data_call is not None and data_put is not None:
        # #     data = data_call.append(data_put, ignore_index=True)
        # # elif data_call is None and data_put is None:
        # #     data = pd.DataFrame()  # Both are None, return empty DataFrame
        # # elif data_call is not None and data_put is None:
        # #     data = data_call
        # # elif data_call is None and data_put is not None:
        # #     data = data_put
        # # print("Combined data=",data)
        # data = data_call


        
        # expiry = settings.EXPIRY
        # date_obj = datetime.strptime(expiry, "%Y-%m-%d")
        # formatted_date = date_obj.strftime("%d-%m-%Y")
        # # str = "OPTSTKTATAMOTORS28-10-2025CE680.00"
        # # my_list = str.split(formatted_date)[0].replace('OPTSTK','')
        # # print(my_list)
        
        # #print("=======",formatted_date)
        # if data is None or data.empty:
           
        #    print("======***********************************")
        #    data = pd.DataFrame()
        #    unique_symbols = []
        #    #return render(request, 'trading/most_active_contracts.html', {'df': data,'index':index})
        # else:
        #     print(f"Data fetched successfully ..............")
        #     print(data)
        #     print(data.columns)

        #     data['symbol'] = data['identifier'].apply(lambda x: x.split(formatted_date)[0].replace('OPTSTK',''))
        #     #unique symbols
        #     unique_symbols = data['symbol'].unique()
        #     print("unique_symbols=",unique_symbols)

        
        #return JsonResponse({'message': f"Most active contracts for {index} fetched successfully."})
        return render(request, 'trading/most_active_contracts.html',
                       {
                    #     'df': data,
                    #    'unique_symbols':unique_symbols,
                         'index':index,
                        
                         })
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)})
    
def topGainer(request):
    instrument_file = os.path.join(PROJECT_PATH,'astrology','DATA','instruments.csv')
    instruments_df = pd.read_csv(instrument_file)
    #print(instruments_df)
    expiry_date = settings.EXPIRY
    filtered_instrument = instruments_df[
                    (instruments_df['exchange'] == 'NFO') &
                    (instruments_df['segment'] == 'NFO-FUT') &
                    (instruments_df['expiry'] == expiry_date) 
                    ]

    symbol = filtered_instrument['name'].unique()
    symbols_list = symbol.tolist()
    symbols_list = [item for item in symbols_list if item not in ['NIFTY','BANKNIFTY','360ONE','FINNIFTY','MIDCPNIFTY','NIFTYNXT50']]
    from ZERODHA_API.zerodha_integration import ZerodhaAPI
    Zerodha = ZerodhaAPI()
    quote_data = Zerodha.kite.quote([f"NSE:{symbol}" for symbol in symbols_list])
    #ltp_data = Zerodha.kite.ltp([f"NSE:{symbol}" for symbol in symbols_list])
    # previous close price
    df_gainer_loser = pd.DataFrame()
    df_gainer_loser['symbol'] = symbols_list
    df_gainer_loser['previous_close'] = df_gainer_loser['symbol'].apply(lambda x: quote_data[f"NSE:{x}"]["ohlc"]["close"] if f"NSE:{x}" in quote_data else None)
    df_gainer_loser['current_price'] = df_gainer_loser['symbol'].apply(lambda x: quote_data[f"NSE:{x}"]["last_price"] if f"NSE:{x}" in quote_data else None)
    df_gainer_loser['change_in_price'] = (df_gainer_loser['current_price'] - df_gainer_loser['previous_close']).round(2)
    df_gainer_loser['change_in_price_percentage'] = ((df_gainer_loser['change_in_price'] / df_gainer_loser['previous_close'].replace(0, float('nan'))) * 100).round(2)

    #print(df_gainer_loser)

    top_gainers = df_gainer_loser.sort_values(by='change_in_price_percentage', ascending=False).head(10)
    top_losers = df_gainer_loser.sort_values(by='change_in_price_percentage', ascending=True).head(10)
    
    most_active_contracts_symbol = MostActiveSymbol.objects.filter(type='CALL').values('symbol')
    symbol_list = [item['symbol'] for item in most_active_contracts_symbol]
    #print("symbol_list========================",symbol_list)
    top_gainers['most_atractive'] = top_gainers['symbol'].isin(symbol_list)
    top_losers['most_atractive'] = top_losers['symbol'].isin(symbol_list)
    # print("Top 10 Gainers:")
    
    #print(top_gainers)  
    # print("Top 10 Losers:")
    # print(top_losers)
    data = {
        'top_gainers': top_gainers,
        'top_losers': top_losers
    }
    

    return data

def ajax_topGainers(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        
        print("AJAX request received") 
        try:
            # Call the most_active_contracts function to fetch data
            data = topGainer(request)
            # print("AJAX response data:========================topGainer")
            # print(data)


            html_content = render_to_string('trading/ajax_top_gainner.html', data, request=request)
            return HttpResponse(html_content)
            #return JsonResponse({'data': data})
        except Exception as e:
            print(f"Error in AJAX handler: {e}")
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request method or not an AJAX request.'})
    
def snapshotDerivativesEquity(index='calls-stocks-vol'):
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
        session.headers.update(headers)

        # Step 1: Hit homepage to get cookies
        home_resp = session.get("https://www.nseindia.com", headers=headers,timeout=10)
        if home_resp.status_code != 200:
            print("Error fetching homepage:", home_resp.status_code)
        else:
            print("Homepage cookies set successfully.")

        # Step 2: Add cookies manually if needed
        # (Optional - usually not needed since session already has them)
        sleep(3)  # Sleep for a second to mimic human behavior
        cookies = session.cookies.get_dict()
        print("Cookies received:", cookies)

        # Step 3: Fetch the NSE API

        resp = session.get(url, headers=headers, cookies=cookies)

        # Step 4: Handle response
        if resp.status_code == 200:
            data = resp.json()
            data = data['OPTSTK']
            df = pd.json_normalize(data['data'])
            return df
            
        else:
            print("Error:", resp.status_code)
            print(resp.text)    
def ajax_most_active_contracts(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        
        print("AJAX request received from ajax_most_active_contracts=====================") 
        

        try:
            expiry = settings.EXPIRY
            date_obj = datetime.strptime(expiry, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d-%m-%Y")

            index_call = 'calls-stocks-vol'
            #active_call = MostActiveContracts(index_call)
            
            data_call = snapshotDerivativesEquity('calls-stocks-vol')
            print("=========Fetching most active contracts for index: calls-stocks-vol")
            #print(data_call)
           
            if data_call is None or data_call.empty:
                data_call = pd.DataFrame()
                print("data_call==================empty")
                print("data_call==================empty")
                # save to MostActiveSymbol
                
            else:
                data_call['symbol'] = data_call['identifier'].apply(lambda x: x.split(formatted_date)[0].replace('OPTSTK',''))
                print("data_call==================2222")
                print("data_call==================22")

                #print(data_call)
            
            # index_put = 'puts-stocks-vol'
            # active_put = MostActiveContracts(index_put)
            # data_put = active_put.fetch_data()
            # if data_put not in None and not data_put.empty:
            #     data_put = pd.DataFrame()
            # else:
            #     data_put['symbol'] = data_put['identifier'].apply(lambda x: x.split(formatted_date)[0].replace('OPTSTK',''))


            favorite  = ['MCX','MARUTI','PERSISTENT','HEROMOTOCO','KAYNES','NIFTY']
            favorite_df = pd.DataFrame(favorite, columns=["symbol"])

            hate_df = pd.DataFrame(['HAL','ICICBANK','HDFCBANK','LT'], columns=["symbol"])

            lovely_df = pd.DataFrame(['HAL','ICICBANK','HDFCBANK','LT','HDFCBANK'], columns=["symbol"])
            #lovely_df = lovely_df.drop_duplicates()
            

            data_call = data_call.drop_duplicates(subset=['symbol'])
            if not data_call.empty:
                # truncate MostActiveSymbol table before inserting new data
                MostActiveSymbol.objects.filter(type='CALL').delete()
                for index, row in data_call.iterrows():
                        MostActiveSymbol.objects.update_or_create(
                            symbol = row['symbol'],
                            type = 'CALL',
                        )
            data_call_db = MostActiveSymbol.objects.filter(type='CALL').values().order_by('-updated_at')
            data_call_db = pd.DataFrame.from_records(data_call_db)
            #print("data_call_db==================",data_call_db)

            #data_call = pd.DataFrame(['HAL','ICICBANK','HDFCBANK','LT'], columns=["symbol"])
            most_active_contracts = render_to_string('trading/ajax_most_active_contracts.html', 
                                            {
                                                'df_call': data_call_db,
                                                #'df_put': data_put,
                                                'index':'calls-stocks-vol'
                                            }, 
                                            request=request)
            favorite = render_to_string('trading/ajax_favorite_symbol.html', {'favorite':favorite_df, },request=request)

            hate = render_to_string('trading/ajax_hate_symbol.html', {'hate_df':hate_df, },request=request)

            lovely = render_to_string('trading/ajax_lovely_symbol.html', {'lovely_df':lovely_df, },request=request)

            data= {
                'most_active_contact': most_active_contracts,
                'hate': hate,
                'favorite': favorite,
                'lovely': lovely,
            }
            return JsonResponse(data)
            #return JsonResponse({'data': data})
        except Exception as e:
            print(f"Error in AJAX handler: {e}")
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request method or not an AJAX request.'})
    
def ajax_chart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print("AJAX request received from ajax_chart=================================") 
        try:
            symbol = request.GET.get('symbol')
            request_params = request.GET.dict()
            data = generate_stock_chart(request_params)
            df_oi = data['df_oi']
            today = data['today']
            print("AJAX response data:========================ajax_chart===============22")
            print(df_oi)

            time_grouped = data['time_grouped']
            fig = go.Figure()
            # Add line for call COI
            fig.add_trace(go.Scatter(
                x=time_grouped['time'],
                y=time_grouped['call_coi'],
                name='Call COI',
                line=dict(color='green', width=2),
                mode='lines+markers'  # You can change this to just 'lines' if you prefer no markers
            ))

            # Add line for put COI 
            fig.add_trace(go.Scatter(
                x=time_grouped['time'],
                y=time_grouped['put_coi'],
                name='Put COI',
                line=dict(color='red', width=2),
                mode='lines+markers'  # You can change this to just 'lines' if you prefer no markers
            ))

            # Add line for current price (assuming you have a 'current_price' column)
            fig.add_trace(go.Scatter(
                x=time_grouped['time'],
                y=time_grouped['current_price'],  # Replace with your actual column name
                name='Current Price',
                line=dict(color='blue', width=2),
                mode='lines+markers',
                yaxis='y2'  # Use secondary y-axis for price
            ))
            title = '<b>' + symbol + ':</b> Call vs Put COI and Current Price by Time..'
            title += f' (Date: {today})'
            fig.update_layout(
                height=600,

                title= title ,
                xaxis_title='Time',
                yaxis_title='Change in Open Interest',
                yaxis2=dict(
                    title='Price',
                    # titlefont=dict(color='blue'),
                    tickfont=dict(color='blue'),
                    overlaying='y',
                    side='right'
                ),
                showlegend=True,
                
            )
            chart_html = fig.to_html(full_html=False)
            last_price = df_oi['current_price'].values[0]
            context = {
                'df_oi': df_oi,
                'current_price' : last_price,
                'today': today,
            }
            html_content = render_to_string('trading/ajax_coi_data.html', context, request=request)
            #return HttpResponse(html_content)
            return JsonResponse({'chart_html': chart_html,'html_content': html_content})
        except Exception as e:
            print(f"Error in AJAX handler: {e}")
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request method or not an AJAX request.'})


def api_get_oi_data(request):
    try:
        symbol_name = request.GET.get('symbol', None)
        symbol_name = symbol_name.upper()
        strike = request.GET.get('strike', None)
        strike = float(strike)
        print("strike=============",strike)
        now = datetime.now()
        date_str = request.GET.get('date', None)
        created_date = pd.to_datetime(date_str).date()

        result = COI.objects.filter(created_at__date=created_date,symbol=symbol_name).order_by('-id')

        df = pd.DataFrame.from_records(result.values())
        
        if df.empty:
            return JsonResponse({'message': 'No data found for the given symbol and date.'})
        
        df = df.sort_values(by='id', ascending=True)
        # dataframe date format
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        #add column date and time
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        df['time'] = pd.to_datetime(df['created_at']).dt.strftime('%H:%M')
        df = df[df['strike'] == strike]

        df = df[['symbol','strike','call_coi','put_coi','created_at','date','time','current_price','call_current_price']]
        data = df.to_dict(orient='records')
        print("data===================",data)
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'Error': {str(e)}})
if __name__ == "__main__":
    # This block is for testing the functions locally
    #my_scheduled_job()
    option_chain_coi()  # Pass None for request in standalone mode