import yfinance as yf
import json
from datetime import datetime
import pandas as pd

# def get_options_data(ticker_symbol):
#     """
#     Fetch call and put options data for a given ticker symbol
#     """
#     try:
#         # Create a Ticker object
#         ticker = yf.Ticker(ticker_symbol)
        
#         # Get options expiration dates
#         expiration_dates = ticker.options
        
#         if not expiration_dates:
#             return {"error": "No options data available for this ticker"}
        
#         # Get the nearest expiration date
#         nearest_expiry = expiration_dates[0]
        
#         # Get options data for the nearest expiration date
#         options = ticker.option_chain(nearest_expiry)
        
#         # Convert to dictionary format
#         # calls_data = options.calls.to_dict('records')
#         # puts_data = options.puts.to_dict('records')
        
#         # Create the final data structure
#         # options_data = {
#         #     "ticker": ticker_symbol,
#         #     "expiration_date": nearest_expiry,
#         #     "calls": calls_data,
#         #     "puts": puts_data
#         # }
#          # Convert to dataframe
#         calls_df = options.calls
#         puts_df = options.puts
#         # print(calls_df)
#         # print(puts_df)
        
#         # Add option type column
#         calls_df['Option Type'] = 'Call'
#         puts_df['Option Type'] = 'Put'
        
#         # Combine calls and puts into one dataframe
#         # Merge calls and puts dataframes on contractSymbol
#         combined_df = pd.merge(calls_df, puts_df, how ='inner', on ='contractSymbol') 
#         #combined_df = combined_df.sort_values('strike')
        
#         return combined_df
        
#         # return options_data
    
#     except Exception as e:
#         return {"error": str(e)}

# def save_to_json(data, filename):
#     """
#     Save the options data to a JSON file
#     """
#     with open(filename, 'w') as f:
#         json.dump(data, f, indent=4)

# def get_options_data_v2(ticker_symbol):
#     """
#     Fetch call and put options data for a given ticker symbol
#     """
#     try:
#         # Create a Ticker object
#         ticker = yf.Ticker(ticker_symbol)
        
#         # Get options expiration dates
#         expiration_dates = ticker.options
        
#         if not expiration_dates:
#             return {"error": "No options data available for this ticker"}
        
#         # Get the nearest expiration date
#         nearest_expiry = expiration_dates[0]
        
#         # Get options data for the nearest expiration date
#         options = ticker.option_chain(nearest_expiry)
        
#         # Convert to dictionary format
#         calls_data = options.calls.to_dict('records')
#         puts_data = options.puts.to_dict('records')
        
#         # Create the final data structure
#         options_data = {
#             "ticker": ticker_symbol,
#             "expiration_date": nearest_expiry,
#             "calls": calls_data,
#             "puts": puts_data
#         }
        
#         return options_data
    
#     except Exception as e:
#         return {"error": str(e)}


def get_specific_expiration(ticker_symbol, target_date):
    ticker = yf.Ticker(ticker_symbol)
    expirations = ticker.options
    current_price = ticker.history(period="1d")['Close'].iloc[-1]
    
    if target_date not in expirations:
        available = "\n".join(expirations)
        raise ValueError(f"{target_date} not available. Available dates:\n{available}")

    # Get the specific option chain
    opt_chain = ticker.option_chain(target_date)

    # Convert to DataFrames and add expiration date
    calls = opt_chain.calls.assign(expiration=target_date)
    puts = opt_chain.puts.assign(expiration=target_date)

    return {
        'calls':calls, 
        'puts' : puts,
        'current_price': current_price,
        'expirations': expirations
        }



