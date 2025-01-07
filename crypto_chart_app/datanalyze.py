import pandas as pd
import ta
import os
import time
import sys
import yfinance as yf
import sqlite3
from binance.client import Client
import plotly.graph_objects as go
import numpy as np
from tabulate import tabulate

DB_NAME = '../tamir_crypto_data.db'


def fetchCryptoData(symbol, timePeriod, lookback, ago='days ago UTC'):
    # Initialize Binance client (use your API keys if you have them)
    client = Client()    
    # Get historical klines/candlestick data
    klines = client.get_historical_klines(
        symbol=symbol,
        interval=timePeriod,
        limit=lookback
    )    
    # Create DataFrame
    df = pd.DataFrame(klines, columns=[
        'Time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close_time', 'Quote_asset_volume', 'Number_of_trades',
        'Taker_buy_base', 'Taker_buy_quote', 'Ignore'
    ])    
    # Convert string values to float
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    # Convert timestamp to datetime
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    df.to_csv('data/crypto_price.csv', index=False)
    # Keep only necessary columns
    df = df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume']]


    
    return df

def find_extremum(df, window=10):
    # print("GOT data for finding EXTREMUMS: ",df)
    # resistances = df[df.High == df.High.rolling(window, center=True).max()].dropna().High
    resistances = df[df.High == df.High.rolling(window, center=True).max()].High
    # resistance_points = resistances.sort_values(ascending=True).tail(2)
    resistance_mean = resistances.max()
    df['resistance'] = resistance_mean
    supports = df[df.Low == df.Low.rolling(window, center=True).min()].Low
    support_mean = supports.min()
    df['support'] = support_mean
    # print("AFTER EXTREMUMS: ",df)
    return df

def is_bullish_doji(candle):
    open_price = candle['Open']
    close_price = candle['Close']
    High_price = candle['High']
    Low_price = candle['Low']
    # Check if the candlestick is a Doji
    is_doji = abs(open_price - close_price) / (High_price - Low_price) < 0.1 if (High_price - Low_price) > 0 else False
    # Check if the Doji is bullish (appears in a downtrend)
    # This is a simplified check; in a real scenario, you might want to analyze the preceding trend
    is_bullish = is_doji and close_price > open_price
    return is_bullish

def apply_technicals(df):
    if len(df) < 14:  # Minimum required length for calculations
        return df
    
    df_tech = df.copy()
    try:
        # Calculate MACD
        df_tech['macd'] = ta.trend.macd_diff(df_tech['Close'])
        # Calculate RSI
        df_tech['rsi'] = ta.momentum.rsi(df_tech['Close'], window=14)
        # Calculate Stochastic Oscillator
        df_tech['stochastic-K'] = ta.momentum.stoch(df_tech['High'], df_tech['Low'], df_tech['Close'], window=14, smooth_window=3)
        df_tech['stochastic-D'] = df_tech['stochastic-K'].rolling(3).mean()
        # Calculate EMA
        df_tech['ema'] = df_tech['Close'].ewm(span=14, adjust=False).mean()
        # Fill NaN values with previous values
        df_tech.fillna(method='bfill', inplace=True)
    except Exception as e:
        print(f"Error in technical analysis: {e}")
        return df
    
    return df_tech
# ===================== EXECUTE =====================
symbol = 'ETHUSDT'
timePeriod = '1h'
lookback = 60
df = fetchCryptoData(symbol, timePeriod, lookback)
# ============= UNTIL HERE ALL WORKS =============
# Create a list to collect processed rows
analyzed_df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

for index, row in df.iterrows():
    # Create a single-row DataFrame
    # row_df = pd.DataFrame([row])
    # Append using concat
    # Update analyzed_df with all data up to current index
    analyzed_df = df.iloc[0:index+1].copy()
    analyzed_df['resistance'] = np.nan
    analyzed_df['support'] = np.nan
    analyzed_df['macd'] = np.nan
    analyzed_df['rsi'] = np.nan
    analyzed_df['stochastic-D'] = np.nan
    analyzed_df['stochastic-K'] = np.nan
    if len(analyzed_df) > 15:
        analyzed_df = find_extremum(analyzed_df, window=10)
        analyzed_df = apply_technicals(analyzed_df)      
    # Print the latest processed row
    print("analyzed data INDEX =========> ",index, " row: ",row)
    print("analyzed data =========> ",analyzed_df)
    print(tabulate(analyzed_df.tail(), headers='keys', tablefmt='psql', showindex=True, floatfmt=".4f"))
    # print("analyzed data =========> ",row_df['resistance'],row_df['support'])
    time.sleep(1)

# Combine all processed rows into final DataFrame
# analyzed_df = pd.concat(processed_rows)
