from django.shortcuts import render
from .models import *
import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd
#from .options_data import get_formatted_options_chain
import yfinance as yf
from .get_options_data import get_specific_expiration
from .nse_options import NSEOptions, NSEOptionChain
from django.http import HttpResponse
symbol_list_new = [
        "NIFTY",
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

# Create your views here.
def home(request):
    horoscope_slug = 'inner'  

    HomeAbout_Content = HomeAbout.objects.get(id=1)
    HomeService = HomePageService.objects.filter(status=True)
    Testimonials_data = Testimonials.objects.filter(status=True)

    

    return render(request, 'index.html', {
        'HomeAbout_Content' : HomeAbout_Content,
        'HomeService' : HomeService,
        'Testimonials_data' : Testimonials_data
        
    });

def horoscope(request,horoscope_slug):
    print(horoscope_slug)
    horoscope_detail = Horoscope.objects.get(slug=horoscope_slug, status=True)    
    horoscope_slug = 'inner'    

    #horoscope_slug = horoscope_slug ? horoscope_slug : 'inner'
    return render(request, 'horoscope.html', {
        'horoscope_slug' : horoscope_slug,
        'horoscope_detail' : horoscope_detail
    });

def page_content(request):
    current_page = request.get_full_path()
    page_name = current_page.replace('/', '') 
    print("current page==",current_page)
    content = PageContent.objects.get(slug=page_name, status=True) 
 
    return render(request, 'page_content.html', {
        'content':content
    });



def price(request):
    return render(request, 'price.html', {

    });

def appointment(request):
    return render(request, 'appointment.html', {

    });

def basic_details(request):
    return render(request, 'basic_details.html', {

    });

def summary(request):
    return render(request, 'summary.html', {

    });

def login(request):
    print("=======login")
    return render(request, 'login.html', {

    });

def signup(request):
    return render(request, 'signup.html', {

    });




def option_chain(request,stock_name):
    print(stock_name)
    symbol_list = UsStock.objects.all()
    #symbol_list = [symbol.name for symbol in symbol_list]

    #print("symbol_list===",symbol_list)

    #symbol_list = ['MSTR','SPY','META','GOOG','DE','SPX','TSLS','COIN','AAPL']
    #print("symbol_list===",symbol_list)
    #stock_name = '%5ESPX'
    ticker = yf.Ticker(stock_name)
    expirations = ticker.options

    print(expirations)
    if request.GET.get('expiry'):
        expiry = request.GET.get('expiry')
    else:
        expiry = expirations[0]
   
    #expiry = expirations[0]
    #print(expiry)
    
   
    try:
        result = get_specific_expiration(stock_name, expiry)
        print("=================gajender========")
        #print(result)
        calls = result['calls']
        puts = result['puts']
        current_price = result['current_price']
        #expirations = result['expirations']
        #print(calls)
        df = calls.merge(puts, left_on='strike', right_on='strike')
        df = df[["openInterest_x", "volume_x", "impliedVolatility_x",'lastPrice_x',"percentChange_x","bid_x","ask_x","strike",
                 "bid_y","ask_y","percentChange_y","lastPrice_y","impliedVolatility_y","volume_y","openInterest_y"]]
       

        if not df.empty:
                # Find the strike price closest to current price
                df['distance'] = abs(df['strike'] - current_price)
                closest_strike_idx = df['distance'].idxmin()
                
                # Get 10 rows above and below the closest strike
                start_idx = max(0, closest_strike_idx - 10)
                end_idx = min(len(df), closest_strike_idx + 10 + 1)  # +1 to include the row itself
                df = df.iloc[start_idx:end_idx]
                
                # Drop the temporary distance column
                df = df.drop(columns=['distance'])
        #print(df)

        current_price = round(current_price, 2)
        
        second_largest_volume_x = df['volume_x'].sort_values(ascending=False).iloc[1]
        second_largest_volume_y = df['volume_y'].sort_values(ascending=False).iloc[1]

        return render(request, 'option_chain.html', {
            'expirations':expirations,
            'expiry':expiry,
            'symbol_list':symbol_list,
            'stock_name':stock_name,
            'current_price':current_price,
            'df':df,
            'max_volume_x':df['volume_x'].max(),
            'max_volume_y':df['volume_y'].max(),
            'second_largest_volume_x':second_largest_volume_x,
            'second_largest_volume_y':second_largest_volume_y,

            'max_oi_x':df['openInterest_x'].max(),
            'max_oi_y':df['openInterest_y'].max(),
            'second_largest_oi_x':df['openInterest_x'].sort_values(ascending=False).iloc[1],
            'second_largest_oi_y':df['openInterest_y'].sort_values(ascending=False).iloc[1]
            
        });

    except Exception as e:
        print(f"Error: {str(e)}")
        return render(request, 'option_chain.html', {
            'symbol_list':symbol_list,
            'expiry':expiry,
            'stock_name':stock_name,
            'error':f"Error: {str(e)}",
            'df': pd.DataFrame()
            
        });

   

   


def nse_option(request, stock_name):
    print(stock_name)
    
    # List of available NSE indices
    #symbol_list = ['NIFTY', 'BANKNIFTY', 'FINNIFTY','ACC']
    symbol_list = symbol_list_new
    expiry_date = '29-May-2025'
    
    try:
        # Create NSEOptions instance
        #nse = NSEOptions()
        
        # Get option chain data
        #data = nse.get_option_chain(stock_name)

        oc = NSEOptionChain(symbol=stock_name)
        data = oc.fetch_data(expiry_date=expiry_date, starting_strike_price=None)
        #print(data['records']['data'])
        
        if data and 'records' in data:
            # Get current price
            current_price = data['records']['underlyingValue']
            print("Current price",current_price)
            
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
            dates = [datetime.datetime.strptime(ts, "%d-%b-%Y") for ts in expirations]
            dates.sort()
            # Convert back to original format
            expirations = [dt.strftime("%d-%b-%Y") for dt in dates]
            
            print(expirations)
            # Get expiry from request params or use first available
            #expiry = request.GET.get('expiry', expirations[0] if expirations else None)
            if request.GET.get('expiry'):
                expiry = request.GET.get('expiry')
            else:
                expiry = expirations[0]
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
                start_idx = max(0, closest_strike_idx - 10)
                end_idx = min(len(df), closest_strike_idx + 10 + 1)  # +1 to include the row itself
                df = df.iloc[start_idx:end_idx]
                
                # Drop the temporary distance column
                df = df.drop(columns=['distance'])
            print(df)
            
            # Round current price
            current_price = round(current_price, 2)

            # Filter rows to show only 10 above and below current price
            # df = df[df['strike'].between(current_price - 10, current_price + 10)]
            # print(df)
    
            second_largest_volume_x = df['volume_x'].sort_values(ascending=False).iloc[1]
            second_largest_volume_y = df['volume_y'].sort_values(ascending=False).iloc[1]
            print("second largent y",second_largest_volume_y)
            
            
            
            return render(request, 'nse_option_chain.html', {
                'expiry':expiry,
                'symbol_list': symbol_list,
                'expirations':expirations,
                'stock_name': stock_name,
                'current_price': current_price,
                'df': df,
                'max_volume_x': df['volume_x'].max(),
                'max_volume_y': df['volume_y'].max(),
                'second_largest_volume_x':second_largest_volume_x,
                'second_largest_volume_y': second_largest_volume_y
            })
        else:
            return render(request, 'nse_option_chain.html', {
                'symbol_list': symbol_list,
                'stock_name': stock_name,
                'error': 'No data available for this symbol',
                'df': pd.DataFrame()
            })
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return render(request, 'nse_option_chain.html', {
            'symbol_list': symbol_list,
            'stock_name': stock_name,
            'error': f"Error: {str(e)}",
            'df': pd.DataFrame()
        })



def anil_page(request):
    list = ['gajender','anil']
    print(list)
    stock_name = "NSE"
    return render(request, 'anil.html', {
        'list':list,
        'name':stock_name

    });

def get_current_time(request):
    """View that returns a partial HTML with the current time."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return HttpResponse(f"Current time: {now}")


if __name__ == "__main__":
    # This block is for testing the functions locally
    #my_scheduled_job()
    get_current_time()  # Pass None for request in standalone mode