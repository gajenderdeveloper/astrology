import os
import logging
from django.utils import timezone
#from .models import CronJob, CronJobExecution

import pandas as pd 
import numpy as np  

from datetime import datetime, time, timedelta
import time as time_module
import plotly.graph_objects as go
from trading.color_coi import *
# Configure logging 


from trading.models import *
def addColorStrike(df):
    last_price = df['current_price'].values[0]
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
    return df

def generate_stock_chart(request):
    symbol = request['symbol']
    print("=========Generating chart for symbol:", symbol)


    current_time = datetime.now().time()
    print("Current time-------------------:generate_stock_chart", current_time)

    today = datetime.now().date()
    if time(1, 7) <= current_time <= time(9, 14):
        print("==============Today's date for chart data:", today)
        today = datetime.now().date()-timedelta(days=1)
    else:
        today = datetime.now().date()

    holiday_list = ['2025-11-05','2025-12-25']
    if today.strftime('%Y-%m-%d') in holiday_list:
            today = today - timedelta(days=1)

    #today = datetime.now().date()-timedelta(days=2)
   
    if 'date' in request:
        date_str = request['date']
        created_date = pd.to_datetime(date_str).date()
    else:
        created_date = today
    #print("====Using created_date for chart:", created_date)
    result = COI.objects.filter(created_at__date=created_date,symbol=symbol).order_by('-id')
    df_chart = pd.DataFrame.from_records(result.values())
    df_chart = df_chart.sort_values(by='id', ascending=True)
    # dataframe date format
    df_chart['created_at'] = pd.to_datetime(df_chart['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    #add column date and time
    df_chart['date'] = pd.to_datetime(df_chart['created_at']).dt.date
    df_chart['time'] = pd.to_datetime(df_chart['created_at']).dt.strftime('%H:%M')

    #print(df_chart.columns)
    #print(df_chart[['symbol','strike','call_trading_symbol','put_trading_symbol','created_at','date','time','current_price']].head(10))
    df_oi = df_chart.copy()
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

        time_unique = df_oi['time'].unique()
        time_unique = time_unique.tolist()
        time_unique.sort( reverse=True)
        if 'time' in request:
            time_selected = request['time']
        else:
            time_selected = time_unique[0]
        df_oi = df_oi[df_oi['time'] == time_selected]
        df_oi = addColorStrike(df_oi)

        data = {
            'time_grouped': time_grouped,
            'df_oi': df_oi,
            'today': today,
            'created_date': created_date,
        }
        return data
        
        
    except Exception as e:
        print(f"Error in plotting chart: {e}")
        chart_html = f"Error in plotting chart: {e}"

    return chart_html