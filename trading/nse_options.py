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

    def fetch_data(self):
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

    
class MostActiveContracts:
    def __init__(self, index='calls-stocks-vol', timeout=5) -> None:
        # self.__url = f"https://www.nseindia.com/api/snapshot-derivatives-equity?index={index}"
        # self.__session = requests.sessions.Session()
        # self.__session.headers = {
      
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        # 'Accept': '*/*',
        # 'Accept-Language': 'en-US,en;q=0.9',
        # 'Accept-Encoding': 'gzip, deflate, br',
        # 'Connection': 'keep-alive',
        # 'Referer': 'https://www.nseindia.com/market-data/most-active-contracts',
        # 'Origin': 'https://www.nseindia.com'
        # }
        # self.__session.headers.update(self.headers)
        # self.__timeout = timeout
        # self.__session.get("https://www.nseindia.com/api/snapshot-derivatives-equity", timeout=self.__timeout)

        self.url = f"https://www.nseindia.com/api/snapshot-derivatives-equity?index={index}"
        self.base_url = f"https://www.nseindia.com/api/snapshot-derivatives-equity?index={index}"
        self.headers =  {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.nseindia.com/market-data/most-active-contracts',
        'Origin': 'https://www.nseindia.com'
        }
        self.session = requests.sessions.Session()
        self.session.headers.update(self.headers)
        self.__timeout = timeout

    def fetch_data(self):
        try:
            print(self.url)
            data = self.session.get(url=self.url, timeout=self.__timeout)
            data = data.json()
            print("Most active contracts raw data:")
            #print(data)
            data = data['OPTSTK']
            df = pd.json_normalize(data['data'])
            return df
        except Exception as ex:
            print(self.url)
            print('Error============: {}'.format(ex))
            self.session.get("https://www.nseindia.com/api/snapshot-derivatives-equity", timeout=self.__timeout) 

    def snapshotDerivativesEquity(self):
        url = "https://www.nseindia.com/api/snapshot-derivatives-equity?index=calls-stocks-vol"

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
            print("Error fetching homepage:", home_resp.status_code)
        else:
            print("Homepage cookies set successfully.")

        # Step 2: Add cookies manually if needed
        # (Optional - usually not needed since session already has them)
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
    

    def fetch_data_with_retries(self, retries=3, delay=5):
        for attempt in range(retries):
            try:
                return self.snapshotDerivativesEquity()
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(delay)
        print("All attempts to fetch data failed.")
        return None

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