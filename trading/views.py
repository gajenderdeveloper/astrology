from django.shortcuts import render, redirect
from .nse_options import NSEOptionChain
from datetime import datetime, time
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import pandas as pd 
from .models import *
from .color import *
from ZERODHA_API.zerodha_integration import ZerodhaAPI
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import importlib
import traceback
from dal import autocomplete
from django.conf import settings
# Create your views here.
symbol_list_new = [
        #"NIFTY",
        "AARTIIND",
        "ABB",
        "ABBOTINDIA",
        "ABCAPITAL",
        "ABFRL",
        "ACC",
        "ADANIENT",
        "ADANIPORTS",
        "ALKEM",
        "AMBUJACEM",
        "APOLLOHOSP",
        "APOLLOTYRE",
        "ASHOKLEY",
        "ASIANPAINT",
        "ASTRAL",
        "ATUL",
        "AUBANK",
        "AUROPHARMA",
        "AXISBANK",
        #"BAJAJ-AUTO",
        "BAJAJFINSV",
        "BAJFINANCE",
        "BALKRISIND",
        #"BALRAMCHIN",
        "BANDHANBNK",
        "BANKBARODA",
        "BATAINDIA",
        "BEL",
        "BERGEPAINT",
        "BHARATFORG",
        "BHARTIARTL",
        "BHEL",
        "BIOCON",
        "BOSCHLTD",
        "BPCL",
        "BRITANNIA",
        "BSOFT",
        "CANBK",
        "CANFINHOME",
        "CHAMBLFERT",
        "CHOLAFIN",
        "CIPLA",
        "COALINDIA",
        "COFORGE",
        "COLPAL",
        "CONCOR",
        "COROMANDEL",
        "CROMPTON",
        "CUB",
        "CUMMINSIND",
        "DABUR",
        "DALBHARAT",
        "DEEPAKNTR",
        "DIVISLAB",
        "DIXON",
        "DLF",
        "DRREDDY",
        "EICHERMOT",
        "ESCORTS",
        "EXIDEIND",
        "FEDERALBNK",
        "GAIL",
        "GLENMARK",
        #"GMRINFRA",
        "GNFC",
        "GODREJCP",
        "GODREJPROP",
        "GRANULES",
        "GRASIM",
        "GUJGASLTD",
        "HAL",
        "HAVELLS",
        "HCLTECH",
        "HDFCAMC",
        "HDFCBANK",
        "HDFCLIFE",
        "HEROMOTOCO",
        "HINDALCO",
        "HINDCOPPER",
        "HINDPETRO",
        "HINDUNILVR",
        "ICICIBANK",
        "ICICIGI",
        "ICICIPRULI",
        "IDEA",
        #"IDFC",
        "IDFCFIRSTB",
        "IEX",
        "IGL",
        "INDHOTEL",
        #"INDIACEM",
        "INDIAMART",
        "INDIGO",
        "INDUSINDBK",
        "INDUSTOWER",
        "INFY",
        "IOC",
        "IPCALAB",
        "IRCTC",
        "ITC",
        "JINDALSTEL",
        "JKCEMENT",
        "JSWSTEEL",
        "JUBLFOOD",
        "KOTAKBANK",
        "LALPATHLAB",
        "LAURUSLABS",
        "LICHSGFIN",
        "LT",
        "LTF",
        "LTIM",
        "LTTS",
        "LUPIN",
        #"M&M",
        #"M&MFIN",
        "MANAPPURAM",
        "MARICO",
        "MARUTI",
        #"MCDOWELL-N",
        "MCX",
        "METROPOLIS",
        "MFSL",
        "MGL",
        "MOTHERSON",
        "MPHASIS",
        "MRF",
        "MUTHOOTFIN",
        "NATIONALUM",
        "NAUKRI",
        "NAVINFLUOR",
        "NESTLEIND",
        "NMDC",
        "NTPC",
        "OBEROIRLTY",
        "OFSS",
        "ONGC",
        "PAGEIND",
        "PEL",
        "PERSISTENT",
        "PETRONET",
        "PFC",
        "PIDILITIND",
        "PIIND",
        "PNB",
        "POLYCAB",
        "POWERGRID",
        "PVRINOX",
        "RAMCOCEM",
        "RBLBANK",
        "RECLTD",
        "RELIANCE",
        "SAIL",
        "SBICARD",
        "SBILIFE",
        "SBIN",
        "SHREECEM",
        "SHRIRAMFIN",
        "SIEMENS",
        "SRF",
        "SUNPHARMA",
        "SUNTV",
        "SYNGENE",
        "TATACHEM",
        "TATACOMM",
        "TATACONSUM",
        "TATAMOTORS",
        "TATAPOWER",
        "TATASTEEL",
        "TCS",
        "TECHM",
        "TITAN",
        "TORNTPHARM",
        "TRENT",
        "TVSMOTOR",
        "UBL",
        "ULTRACEMCO",
        "UPL",
        "VEDL",
        "VOLTAS",
        "WIPRO",
        #"ZEEL",
        #"ZYDUSLIFE"
    ]



@login_required(login_url='/loginpage')
def option_chain(request, symbol_name):
    symbol_name_original = symbol_name
    # List of available NSE indices
    #symbol_list_new = ['VOLTAS']
    # symbol_list = symbol_list_new
    # expiry_date = '29-May-2025'
    # # Initialize the API
    
    
    if request.GET.get('expiry'):
        expiry_date = request.GET.get('expiry')
    else:
        expiry_date = settings.EXPIRY

    print("===================gajender option_chain")
    Zerodha = ZerodhaAPI()
    exchange="NFO"
    try:
        instruments_df = Zerodha.get_instruments("NFO")
        
        instruments_df['expiry'] = instruments_df['expiry'].astype('string')
        instruments_df = instruments_df[(instruments_df["expiry"] == expiry_date)]
        symbol = instruments_df['name'].unique()
        #print(symbol)

        # get strike by symbol   
    
        result = Zerodha.get_all_strikes_with_ltp_and_oi(
            symbol_name,
            exchange=exchange,
            expiry_date=expiry_date
        )
        # if result['error']:
        #     messages.error(request, result['error'])
        #     return JsonResponse({'error': result['error']}, status=400)
       
       
        strike_df = result['df']
        # print(strike_df)
        # strike_df2 = result['df']
        # print(strike_df2.columns)
        # print(strike_df2[['strike','CE_oi','CE_prev_oi','CE_change_in_oi','CE_instrument_token','CE_name']])
 
        # nifty_symbols = [
        #     "NSE:NIFTY 50",
        #     "NSE:NIFTY BANK", 
        #     "NSE:NIFTY IT"
        # ]
        symbol_name = 'NIFTY 50' if symbol_name == 'NIFTY' else symbol_name
        quote_data = Zerodha.kite.quote([f"NSE:{symbol_name}"])

        symbol_instrument = quote_data[f"NSE:{symbol_name}"].get('instrument_token')
        symbol_lastprice = quote_data[f"NSE:{symbol_name}"].get('last_price')
        print("quote_data++++++++++++++++",quote_data)

        max_volume_CE = strike_df['CE_volume'].max()
        second_largest_volume_CE = strike_df['CE_volume'].sort_values(ascending=False).iloc[1]

        max_volume_PE  = strike_df['PE_volume'].max()
        second_largest_volume_PE = strike_df['PE_volume'].sort_values(ascending=False).iloc[1]

        # for change in oi
        max_coi_CE = strike_df['CE_change_in_oi'].max()
        second_largest_coi_CE = strike_df['CE_change_in_oi'].sort_values(ascending=False).iloc[1]
        min_coi_CE = strike_df['CE_change_in_oi'].min()
       

        max_coi_PE  = strike_df['PE_change_in_oi'].max()
        second_largest_coi_PE = strike_df['PE_change_in_oi'].sort_values(ascending=False).iloc[1]
        min_coi_PE = strike_df['PE_change_in_oi'].min()


        max_CE_oi = strike_df['CE_oi'].max()
        second_largest_CE_oi = strike_df['CE_oi'].sort_values(ascending=False).iloc[1]
        min_CE_oi = strike_df['CE_oi'].min()

        max_PE_oi = strike_df['PE_oi'].max()
        second_largest_PE_oi = strike_df['PE_oi'].sort_values(ascending=False).iloc[1]
        min_PE_oi = strike_df['PE_oi'].min()
        
        
        
        #print(strike_df)
        # get current price
        exchange2 = "NSE"
        if symbol_name == 'NIFTY':
            symbol_name = "NIFTY 50"
        if symbol_name == 'BANKNIFTY':
            symbol_name = "NIFTY BANK"


        quote_data = Zerodha.get_quote(f"{exchange2}:{symbol_name}")

        #print("quote_data",quote_data)

         # Extract current price
        last_price = quote_data[f"{exchange2}:{symbol_name}"]['last_price']
        #print(last_price)
        
        
           

        strike_df['CE_color'] = strike_df.apply(CE_color,axis=1,args=(last_price,))
        strike_df['PE_color'] = strike_df.apply(PE_color,axis=1,args=(last_price,)) 

        strike_df['CE_color_volume'] = strike_df.apply(CE_color_volume,axis=1,args=(max_volume_CE, second_largest_volume_CE,last_price))
        strike_df['PE_color_volume'] = strike_df.apply(PE_color_volume,axis=1,args=(max_volume_PE, second_largest_volume_PE,last_price)) 

        strike_df['CE_color_change_in_oi'] = strike_df.apply(CE_color_change_in_oi,axis=1,args=(max_coi_CE, second_largest_coi_CE, min_coi_CE,last_price))
        strike_df['PE_color_change_in_oi'] = strike_df.apply(PE_color_change_in_oi,axis=1,args=(max_coi_PE, second_largest_coi_PE, min_coi_PE,last_price)) 

        strike_df['CE_color_total_oi'] = strike_df.apply(CE_color_total_oi, axis=1, args=(
            max_CE_oi, second_largest_CE_oi, min_CE_oi, last_price))
        strike_df['PE_color_total_oi'] = strike_df.apply(PE_color_total_oi, axis=1, args=(
            max_PE_oi, second_largest_PE_oi, min_PE_oi, last_price))
       
        
        #print(strike_df[['strike','CE_color_total_oi','PE_color_total_oi']])
        strike_df['CE_ltp_low_pecent'] = ((strike_df['CE_ltp'] - strike_df['CE_day_low']) / strike_df['CE_day_low']) * 100
        strike_df['PE_ltp_low_pecent'] = ((strike_df['PE_ltp'] - strike_df['PE_day_low']) / strike_df['PE_day_low']) * 100

        print(strike_df[['strike','CE_ltp','CE_day_low','CE_ltp_low_pecent']])
        
        #print(dict)
        expiry_list = result['unique_expiry']
        return render(request, 'zerodha_nse_option_chain.html', {
                'expiry_date':expiry_date,
                'symbol_name' : symbol_name_original,
                'symbol_instrument' : symbol_instrument,
                'symbol_lastprice' : symbol_lastprice,
                'symbol_list' : symbol,
                'current_price' : last_price,
                'df': strike_df,
                'max_volume_CE':max_volume_CE,
                'second_largest_volume_CE' : second_largest_volume_CE,
                'max_volume_PE':max_volume_PE,
                'second_largest_volume_PE' : second_largest_volume_PE,

                'max_coi_CE':max_coi_CE,
                'second_largest_coi_CE' : second_largest_coi_CE,
                'max_coi_PE':max_coi_PE,
                'second_largest_coi_PE' : second_largest_coi_PE,
                'expiry_list' : expiry_list
                
            })

        
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'Error': {str(e)}})

  
    

@login_required(login_url='/loginpage')
def zerodha_save_changein_oi(request):
    now = datetime.now()
    today = now.date()
    print("save change in oi")
    
    
    
    morning_cutoff = datetime.combine(today, time(9, 0))
    afternoon_cutoff = datetime.combine(today, time(20, 30))

    print(now,'====',morning_cutoff, "===",afternoon_cutoff)
    print(now.timestamp(),'===',morning_cutoff.timestamp(),'=====',afternoon_cutoff.timestamp())
    
    if now.timestamp() > morning_cutoff.timestamp() and now.timestamp() < afternoon_cutoff.timestamp():
        return JsonResponse({'error': 'Market is running'}, status=400)
    
    
    try:
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
        print("===1")
        for i in range(0, len(trading_symbols), batch_size):
            batch = trading_symbols[i:i + batch_size]

            # Prepare the batch request format (exchange:symbol)
            batch_request = [f"{exchange}:{symbol}" for symbol in batch]

            try:
                # Get quote data for the batch
                print("===2")
                batch_response = Zerodha.get_quote(batch_request)
                print("===")

                # Merge the batch response into the main quote_data
                quote_data.update(batch_response)

                # Optional: print progress
                print(f"Processed {min(i + batch_size, len(trading_symbols))}/{len(trading_symbols)} symbols")

            except Exception as e:
                print(f"Error processing batch {i // batch_size + 1}: {str(e)}")
                return JsonResponse({'error': str(e)}, status=400)
        filtered_df['prev_oi'] = filtered_df['tradingsymbol'].apply(
                    lambda x: quote_data.get(f"{exchange}:{x}", {}).get('oi', None))
        filtered_df['prev_oi'] = (filtered_df['prev_oi'] / filtered_df['lot_size']).astype(int)

        filtered_df.sort_values(by=['tradingsymbol','strike'], inplace=True)

        # save to csv
        #filtered_df.to_csv(f"zerodha_prev_option_chain.csv", index=False)
        print("completed")
        return JsonResponse({'success': True})
        

    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)

@login_required(login_url='/loginpage')
def zerodha_positions(request):
    Zerodha = ZerodhaAPI()
    positions = Zerodha.get_positions()
    return JsonResponse({'positions': positions})

def nse_option_2(request, stock_name):
    # List of available NSE indices
    #symbol_list_new = ['VOLTAS']
    # symbol_list = symbol_list_new
    # expiry_date = '29-May-2025'
    # # Initialize the API
    # Get list of available symbols from the database
    

    
    for stock_name in symbol_list_new:
        
        try:
            # Create NSEOptions instance
            print(stock_name)
            oc = NSEOptionChain(symbol=stock_name)
            data = oc.fetch_data()
            print("====================",stock_name)
            #print(data['records']['data'])
            
            if data and 'records' in data:
                # Get current price
                current_price = data['records']['underlyingValue']
                #print("Current price",current_price)
                
                # Process the data into a DataFrame
                # Get list of expiration dates
                expirations = []
                for item in data['records']['data']:
                    if 'expiryDate' in item:
                        if item['expiryDate'] not in expirations:
                            expirations.append(item['expiryDate'])
                # dates = [datetime.datetime.strptime(ts, "%Y-%m-%d") for ts in expirations]
                # dates.sort()
                # Convert expiration dates to datetime for proper sorting
                dates = [datetime.strptime(ts, "%d-%b-%Y") for ts in expirations]
                dates.sort()
                # Convert back to original format
                expirations = [dt.strftime("%d-%b-%Y") for dt in dates]
                
                #print(expirations)
                # Get expiry from request params or use first available
                #expiry = request.GET.get('expiry', expirations[0] if expirations else None)
                if request.GET.get('expiry'):
                    expiry = request.GET.get('expiry')
                else:
                    expiry = expirations[0]
                print(expiry)    
                options_data = []
                for item in data['records']['data']:
                    strike = item['strikePrice']
                    ce_data = item.get('CE', {})
                    pe_data = item.get('PE', {})
                    
                    # Skip if expiry date doesn't match
                    #print(ce_data.get('openInterest', 0))
                    if item['expiryDate'] != expiry:
                        continue
                    #print(item)
                    #print(ce_data)

                    
                    options_data.append({
                        'strike': strike,
                        'openInterest_x': ce_data.get('openInterest', 0),
                        'change_openInterest_x': ce_data.get('changeinOpenInterest', 0),
                        'volume_x': ce_data.get('totalTradedVolume', 0),
                        'impliedVolatility_x': ce_data.get('impliedVolatility', 0),
                        'lastPrice_x': ce_data.get('lastPrice', 0),
                        'change_x': ce_data.get('change', 0),
                        'bidqty_x': ce_data.get('bidQty', 0),
                        'bid_x': ce_data.get('bidprice', 0),
                        'ask_x': ce_data.get('askPrice', 0),
                        'askqty_x': ce_data.get('askQty', 0),

                        'bidqty_y': pe_data.get('bidQty', 0),
                        'bid_y': pe_data.get('bidprice', 0),
                        'ask_y': pe_data.get('askPrice', 0),
                        'askqty_y': pe_data.get('askQty', 0),
                        'change_y': pe_data.get('change', 0),
                        'lastPrice_y': pe_data.get('lastPrice', 0),
                        'impliedVolatility_y': pe_data.get('impliedVolatility', 0),
                        'volume_y': pe_data.get('totalTradedVolume', 0),
                        'openInterest_y': pe_data.get('openInterest', 0),
                        'change_openInterest_y': pe_data.get('changeinOpenInterest', 0)
                    })
                
                df = pd.DataFrame(options_data)

                if not df.empty:
                    # Find the strike price closest to current price
                    df['distance'] = abs(df['strike'] - current_price)
                    closest_strike_idx = df['distance'].idxmin()
                    
                    # Get 10 rows above and below the closest strike
                    start_idx = max(0, closest_strike_idx - 2)
                    end_idx = min(len(df), closest_strike_idx + 2 + 1)  # +1 to include the row itself
                    df = df.iloc[start_idx:end_idx]
                    
                    # Drop the temporary distance column
                    df = df.drop(columns=['distance'])
                #print(df)
                
                # Round current price
                current_price = round(current_price, 2)

                # Filter rows to show only 10 above and below current price
                # df = df[df['strike'].between(current_price - 10, current_price + 10)]
                # print(df)
        
                # second_largest_volume_x = df['volume_x'].sort_values(ascending=False).iloc[1]
                # second_largest_volume_y = df['volume_y'].sort_values(ascending=False).iloc[1]
                

                volume_call= df['volume_x'].sum() 
                volume_put= df['volume_y'].sum() 

                coi_call= df['change_openInterest_x'].sum() 
                coi_put= df['change_openInterest_y'].sum() 

                print("volume_call=",volume_call)
                print("volume_put=  ",volume_put)
                print("coi_call=",coi_call)
                print("coi_put=",coi_put)

                if volume_call > volume_put*3 and coi_put > coi_call*2 and coi_call < 0:
                    if ScaningStock.objects.filter(symbol=stock_name).exists():
                        ScaningStock.objects.filter(symbol=stock_name).delete()
                        print("ScaningStock deleted")
                    ScaningStock.objects.create(
                        symbol=stock_name,
                        total_volume_call=volume_call,
                        total_volume_put=volume_put,
                        total_coi_call=coi_call,
                        total_coi_put=coi_put
                    )   
                print("ScaningStock created")   

                # for item in df:
                #     NSEOptionChainData.objects.create(
                #         symbol=stock_name,
                #         expiry_date=expiry,
                #         strike_price=item['strike'],
                #         call_volume=item['volume_x'],
                #         call_openInterest=item['openInterest_x'],
                #         call_changeinOpenInterest=item['change_openInterest_x'],
                #         call_impliedVolatility=item['impliedVolatility_x'],
                #         call_lastPrice=item['lastPrice_x'],
                #         call_change=item['change_x'],
                #         call_bidqty=item['bidqty_x'],
                #         call_bid=item['bid_x'],
                #         call_ask=item['ask_x'],
                #         call_askqty=item['askqty_x'],
                #         put_volume=item['volume_y'],
                #         put_openInterest=item['openInterest_y'],
                #         put_changeinOpenInterest=item['change_openInterest_y'],
                #     )

                
            
            
        except Exception as e:
            print(f"Error: {str(e)}")
            
        
    return render(request, 'anil.html', {
                
    })

def cron_job_dashboard(request):
    """Dashboard to view and manage cron jobs"""
    jobs = CronJob.objects.all().order_by('name')
    recent_executions = CronJobExecution.objects.select_related('job').order_by('-started_at')[:10]
    
    context = {
        'jobs': jobs,
        'recent_executions': recent_executions,
    }
    return render(request, 'trading/cron_dashboard.html', context)

@csrf_exempt
def run_cron_job(request, job_id):
    """API endpoint to run a cron job"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        job = CronJob.objects.get(id=job_id)
        
        # Create execution record
        execution = CronJobExecution.objects.create(job=job)
        
        try:
            # Import and run the function
            module_path, function_name = job.function_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            function = getattr(module, function_name)
            
            # Run the function
            result = function()
            
            # Update execution record
            execution.status = 'success'
            execution.completed_at = timezone.now()
            execution.output = f"Job executed successfully at {timezone.now()}\nResult: {result}"
            execution.save()
            
            # Update job record
            job.last_run = timezone.now()
            job.status = 'active'
            job.save()
            
            return JsonResponse({
                'success': True,
                'message': f"Job '{job.name}' executed successfully",
                'execution_id': execution.id
            })
            
        except Exception as e:
            # Update execution record with error
            execution.status = 'failed'
            execution.completed_at = timezone.now()
            execution.error_message = str(e)
            execution.output = f"Error executing job: {str(e)}\n{traceback.format_exc()}"
            execution.save()
            
            # Update job record
            job.last_run = timezone.now()
            job.status = 'error'
            job.save()
            
            return JsonResponse({
                'success': False,
                'error': str(e),
                'execution_id': execution.id
            }, status=500)
            
    except CronJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def cron_job_status(request):
    """API endpoint to get cron job status"""
    jobs = CronJob.objects.all()
    data = []
    
    for job in jobs:
        data.append({
            'id': job.id,
            'name': job.name,
            'status': job.status,
            'is_enabled': job.is_enabled,
            'last_run': job.last_run.isoformat() if job.last_run else None,
            'next_run': job.next_run.isoformat() if job.next_run else None,
            'execution_count': job.executions.count(),
            'success_count': job.executions.filter(status='success').count(),
            'failed_count': job.executions.filter(status='failed').count(),
        })
    
    return JsonResponse({'jobs': data})




# from astrology.zerodha_integration import ZerodhaAPI

# # Initialize the API
# zerodha = ZerodhaAPI()

# # Example: Get user profile
# profile = zerodha.get_profile()

# # Example: Place an order
# order = zerodha.place_order(
#     variety="regular",
#     exchange="NSE",
#     tradingsymbol="RELIANCE",
#     transaction_type="BUY",
#     quantity=1,
#     product="CNC",
#     order_type="MARKET"
# )

# # Example: Get historical data
# historical_data = zerodha.get_historical_data(
#     instrument_token=256265,
#     from_date="2024-01-01",
#     to_date="2024-03-20",
#     interval="day"
# )


if __name__ == "__main__":
    # This block is for testing the functions locally
    #my_scheduled_job()
    print("Testing for view function")
    option_chain('GODREJPROP')
    print("Testing completed")
    


