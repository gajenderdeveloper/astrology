import os
import logging
from django.utils import timezone
#from .models import CronJob, CronJobExecution

import pandas as pd 
import numpy as np  
import time 
import talib

from datetime import datetime, timedelta
# Configure logging 
logger = logging.getLogger(__name__)
# import ZERODHA_API

def calculate_200ma(df:pd.DataFrame):
    # add df to 200ma column
    df['200ma'] = df['close'].rolling(window=200).mean()
    return df


def calculate_ema(df:pd.DataFrame, period=200, column='close'):
    df['ema_200'] =  df[column].ewm(span=period, adjust=False).mean()
    return df

def ema(df:pd.DataFrame, period=200, column='close'):
    """
    Calculate Exponential Moving Average (EMA) for a given DataFrame and period.
    """
    df['ema_200'] = talib.EMA(df[column], timeperiod=period)
    return df

def supertrend(df, period=7, multiplier=3):
    """
    Calculate Supertrend indicator
    :param df: DataFrame with OHLC data
    :param period: ATR period
    :param multiplier: ATR multiplier
    :return: DataFrame with Supertrend columns added
    """
    high = df['high']
    low = df['low']
    close = df['close']
    
    # Calculate ATR
    atr = talib.ATR(high, low, close, timeperiod=period)
    
    # Calculate basic upper and lower bands
    hl2 = (high + low) / 2
    df['upper_band'] = hl2 + (multiplier * atr)
    df['lower_band'] = hl2 - (multiplier * atr)
    
    # Initialize Supertrend column
    df['supertrend'] = 0.0
    df['direction'] = 1  # 1 for uptrend, -1 for downtrend
    
    for i in range(1, len(df)):
        # Current row
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        # If previous Supertrend is uptrend
        if prev['supertrend'] == prev['upper_band']:
            if current['close'] > current['upper_band']:
                df.at[df.index[i], 'supertrend'] = current['upper_band']
                df.at[df.index[i], 'direction'] = 1
            else:
                df.at[df.index[i], 'supertrend'] = current['lower_band']
                df.at[df.index[i], 'direction'] = -1
        # If previous Supertrend is downtrend
        else:
            if current['close'] < current['lower_band']:
                df.at[df.index[i], 'supertrend'] = current['lower_band']
                df.at[df.index[i], 'direction'] = -1
            else:
                df.at[df.index[i], 'supertrend'] = current['upper_band']
                df.at[df.index[i], 'direction'] = 1
    
    return df

def resample_ohlc(df:pd.DataFrame, interval='15min'):
    """
    Resample OHLC data to a different time interval.
    :param df: DataFrame with OHLC data and datetime index
    :param interval: Resampling interval (e.g., '15min', '1H', '1D')
    :return: Resampled DataFrame
    """
    #df['date'] = pd.to_datetime(df['date'])
    #df.set_index('date', inplace=True)
    df_resample = df.resample(interval).agg({
                        'open': 'first',
                        'high': 'max',
                        'low': 'min',
                        'close': 'last',
                        'volume': 'sum' 
                    }).dropna()
    df = df_resample.reset_index()
    return df


