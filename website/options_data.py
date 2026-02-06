import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def get_options_data(stock_symbol):
    """
    Fetch options data from Yahoo Finance for a given stock symbol.
    
    Args:
        stock_symbol (str): The stock symbol (e.g., 'AAPL', 'MSFT')
        
    Returns:
        tuple: (DataFrame containing options data, current stock price)
    """
    url = f"https://finance.yahoo.com/quote/{stock_symbol}/financials/?p={stock_symbol}"
    headers1 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get current stock price
        price_element = soup.find('fin-streamer', {'data-symbol': stock_symbol, 'data-field': 'regularMarketPrice'})
        current_price = float(price_element.text) if price_element else None
        
        if not current_price:
            print(f"Could not find current price for {stock_symbol}")
            return None, None

        # Find options tables
        tables = soup.find_all("table")
        if not tables:
            print("No options data found.")
            return None, None

        # Process options data
        options_data = []
        for table in tables:
            headers = [header.text.strip() for header in table.find_all("th")]
            rows = table.find_all("tr")[1:]  # Skip header row

            for row in rows:
                cells = row.find_all("td")
                if len(cells) > 0:
                    options_data.append([cell.text.strip() for cell in cells])

        # Create DataFrame
        df = pd.DataFrame(options_data, columns=headers)
        
        return df, current_price

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, None
    except Exception as e:
        print(f"Error processing data: {e}")
        return None, None

def format_options_chain(df, current_price, strike_range=30):
    """
    Format the options chain data into a more readable format.
    
    Args:
        df (DataFrame): Raw options data
        current_price (float): Current stock price
        strike_range (int): Range of strikes to include around current price
        
    Returns:
        DataFrame: Formatted options chain
    """
    if df is None or df.empty:
        return None

    # Clean numeric columns
    numeric_cols = ['Volume', 'Implied Volatility', '% Change', 'Open Interest',
                   'Last Price', 'Bid', 'Ask', 'Change']
    
    df = df.replace('-', '0')
    df = df.replace('', '0')

    # Clean Volume column
    df['Volume'] = df['Volume'].str.replace(',', '').astype(float)
    
    # Extract contract details
    contract_parts = df['Contract Name'].str.extract(
        r'^(?P<Symbol>[A-Z]+)(?P<Expiry>\d{6})(?P<Type>[CP])(?P<Strike>\d{8})$'
    ).dropna()
    
    # Add extracted columns
    df = df.loc[contract_parts.index].copy()
    df['Symbol'] = contract_parts['Symbol']
    df['Expiry'] = pd.to_datetime(contract_parts['Expiry'], format='%y%m%d', errors='coerce')
    df['Strike'] = pd.to_numeric(contract_parts['Strike'], errors='coerce')
    df['Instrument Type'] = contract_parts['Type'].map({'C': 'CE', 'P': 'PE'})

    # Filter strikes within range
    df = df[(df['Strike'] >= current_price - strike_range) &
            (df['Strike'] <= current_price + strike_range)].copy()

    # Clean numeric columns
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace('%', '')
                .str.replace(',', '')
                .replace('nan', '0')
                .replace('-', '0')
                .astype(float)
            )

    # Split into calls and puts
    calls = df[df['Instrument Type'] == 'CE'].copy()
    puts = df[df['Instrument Type'] == 'PE'].copy()

    # Merge calls and puts
    merged = pd.merge(calls, puts, on='Strike',
                     suffixes=('_CE', '_PE'), how='outer')

    # Create final output
    result = merged[[
        'Open Interest_CE', 'Change_CE', '% Change_CE', 'Volume_CE', 'Implied Volatility_CE',
        'Last Price_CE', 'Bid_CE', 'Ask_CE',
        'Strike',
        'Last Price_PE', 'Bid_PE', 'Ask_PE', 'Implied Volatility_PE',
        'Volume_PE', '% Change_PE', 'Change_PE', 'Open Interest_PE'
    ]].copy()

    # Rename columns
    result.columns = [
        'OI', 'Chng in OI', '% Change', 'Volume', 'IV', 'LTP', 'Bid', 'Ask',
        'Strike Price',
        'LTP2', 'Bid2', 'Ask2', 'IV2', 'Volume2', '% Change2', 'Chng in OI2', 'OI2'
    ]

    # Fill NaN values with 0
    result = result.fillna(0)
    
    return result

def get_formatted_options_chain(stock_symbol, strike_range=30):
    """
    Get and format options chain data for a given stock symbol.
    
    Args:
        stock_symbol (str): The stock symbol (e.g., 'AAPL', 'MSFT')
        strike_range (int): Range of strikes to include around current price
        
    Returns:
        tuple: (Formatted DataFrame, current price)
    """
    df, current_price = get_options_data(stock_symbol)
    if df is not None and current_price is not None:
        formatted_df = format_options_chain(df, current_price, strike_range)
        return formatted_df, current_price
    return None, None 