import requests
import json
from datetime import datetime
import time
import pandas as pd

class NSEOptions:
    def __init__(self,timeout=5):
        self.base_url = "https://www.nseindia.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5"}
        self.session = requests.sessions.Session()
        self.session.headers.update(self.headers)
        self.__timeout = timeout

    def get_option_chain(self, symbol="NIFTY"):
        try:
            # First visit the main page to get cookies
            self.session.get(self.base_url)
            time.sleep(2)  # Small delay to avoid rate limiting

            # Get the option chain data
            if symbol == 'NIFTY':
                url = f"{self.base_url}/api/option-chain-indices?symbol={symbol}"
            else:
                url = f"{self.base_url}/api/option-chain-equities?symbol={symbol}"
            response = self.session.get(url,timeout=self.__timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Error fetching data. Status code: {response.status_code}")
                return None

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def save_to_file(self, data, filename=None):
        if filename is None:
            filename = f"nse_options_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {filename}")

class NSEOptionChain():
    def __init__(self, symbol='NIFTY', timeout=5) -> None:
        if symbol == 'NIFTY':
            self.__url = "https://www.nseindia.com/api/option-chain-indices?symbol={}".format(symbol)
        else:
            self.__url = "https://www.nseindia.com/api/option-chain-equities?symbol={}".format(symbol)
        self.__session = requests.sessions.Session()
        self.__session.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5"}
        self.__timeout = timeout
        self.__session.get("https://www.nseindia.com/option-chain", timeout=self.__timeout)

    def fetch_data(self, expiry_date=None, starting_strike_price=None, number_of_rows=2):
        try:
            data = self.__session.get(url=self.__url, timeout=self.__timeout)
            data = data.json()
            # df = pd.json_normalize(data['records']['data'])

            # if expiry_date != None:
            #     df = df[(df.expiryDate == expiry_date)]
            # df.reset_index(drop=True, inplace=True)

            # starting_strike_price = df['CE.underlyingValue'][7]
            # if starting_strike_price == None:
            #     starting_strike_price = df['CE.underlyingValue'][8]
            # if starting_strike_price == None:
            #     starting_strike_price = df['CE.underlyingValue'][9]
            return data
        except Exception as ex:
            print(self.__url)
            #print(df)
            print('Error: {}'.format(ex))
            self.__session.get("https://www.nseindia.com/option-chain", timeout=self.__timeout)

def main():
    nse = NSEOptions()
    
    # Get option chain data for NIFTY
    data = nse.get_option_chain("ACC")
    
    if data:
        # Save the data to a file
        nse.save_to_file(data)
        
        # Print some basic information
        if 'records' in data:
            print("\nOption Chain Summary:")
            print(f"Underlying Value: {data['records']['underlyingValue']}")
            print(f"Timestamp: {data['records']['timestamp']}")
            
            # Print first few strike prices
            if 'data' in data['records']:
                print("\nFirst few strike prices:")
                for item in data['records']['data'][:5]:
                    print(f"Strike Price: {item['strikePrice']}")
                    if 'CE' in item:
                        print(f"CE OI: {item['CE']['openInterest']}")
                    if 'PE' in item:
                        print(f"PE OI: {item['PE']['openInterest']}")
                    print("---")

if __name__ == "__main__":
    #main() 
    oc = NSEOptionChain(symbol='ACC')
    data = oc.fetch_data(expiry_date='29-May-2025', starting_strike_price=None)