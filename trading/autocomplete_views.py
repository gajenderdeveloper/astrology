from dal import autocomplete
import os
import sys
import django
from django.conf import settings
import pandas as pd 
import numpy as np 

print("====================autocomplete_views.py=====================")

# instrument_file = os.path.join(settings.PROJECT_DIR,'astrology','ZERODHA_API','instruments.csv')
# instruments_df = pd.read_csv(instrument_file)

PROJECT_PATH = os.path.dirname(settings.BASE_DIR)
instrument_file = os.path.join(PROJECT_PATH,'astrology','DATA','instruments.csv')
instruments_df = pd.read_csv(instrument_file)


#instruments_df_nse = instruments_df[(instruments_df['exchange'] == 'NSE') ]
#instruments_df_nfo = instruments_df[instruments_df['exchange'] == 'NFO']


class MyAutocomplete(autocomplete.Select2ListView):
    def get_list(self):
        # Your predefined list
        #filter_value = self.request.GET.get('exchange', None)
        exchange = self.forwarded.get('exchange', None)
        print("filter_value=========:", exchange)

        if exchange == 'NFO':
            instruments = instruments_df[(instruments_df['exchange'] == 'NFO') & (instruments_df['segment'] == 'NFO-OPT')]
            symbol_list = instruments['tradingsymbol'].unique()
            symbol = [(symbol, symbol) for symbol in symbol_list if isinstance(symbol, str) and len(symbol) > 0]
            
        else:
            instruments = instruments_df[(instruments_df['exchange'] == 'NSE') & (instruments_df['segment'] == 'NSE')]
            symbol_list = instruments['tradingsymbol'].unique()
            symbol = [(symbol, symbol) for symbol in symbol_list if isinstance(symbol, str) and len(symbol) > 0]
           


       
        
        return symbol
    

class SymbolAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = instruments_df.copy()
        
        # Get the exchange from the forwarded parameters
        exchange = self.forwarded.get('exchange', None)
        
        if exchange:
            qs = qs[(qs['exchange'] == exchange) & (qs['segment'] == exchange)]
        
        if self.q:
            qs = qs[qs['tradingsymbol'].str.contains(self.q, case=False)]
        
        return qs['tradingsymbol'].unique()
    