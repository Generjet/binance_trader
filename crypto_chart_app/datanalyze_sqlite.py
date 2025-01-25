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
import sqlite3
import mysql.connector

# DB_NAME = '../tamir_crypto_data.db'
DB_NAME = '../../../elixir-projects/portalblog/portalblog_dev.db'
def save_data(row):
    # Convert the 'time' column to string if it's not already
    row['time'] = str(row['time'])

    conn = sqlite3.connect('crypto_data.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analyzed_data (
        time TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        resistance REAL,
        support REAL,
        macd REAL,
        rsi REAL,
        ema REAL,
        stochastic_D REAL,
        stochastic_K REAL
    )
    ''')

    cursor.execute('''
    INSERT INTO analyzed_data (time, open, high, low, close, volume, resistance, support, macd, rsi, ema, stochastic_D, stochastic_K)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row['time'], row['open'], row['high'], row['low'], row['close'], row['volume'], row.get('resistance', np.nan), row.get('support', np.nan), row.get('macd', np.nan), row.get('rsi', np.nan), row.get('ema', np.nan), row.get('stochastic-D', np.nan), row.get('stochastic-K', np.nan)))

    conn.commit()
    conn.close()
    print("Data saved for time:", row['time'])

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
        'time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'Number_of_trades',
        'Taker_buy_base', 'Taker_buy_quote', 'Ignore'
    ])    
    # Convert string values to float
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    # Convert timestamp to datetime
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.to_csv('data/crypto_price.csv', index=False)
    # Keep only necessary columns
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]    
    return df

def find_extremum(df, window=10):
    # print("GOT data for finding EXTREMUMS: ",df)
    # resistances = df[df.high == df.high.rolling(window, center=True).max()].dropna().high
    resistances = df[df.high == df.high.rolling(window, center=True).max()].high
    # resistance_points = resistances.sort_values(ascending=True).tail(2)
    resistance_mean = resistances.max()
    df['resistance'] = resistance_mean
    supports = df[df.low == df.low.rolling(window, center=True).min()].low
    support_mean = supports.min()
    df['support'] = support_mean
    # print("AFTER EXTREMUMS: ",df)
    return df

def is_bullish_doji(candle):
    open_price = candle['open']
    close_price = candle['close']
    high_price = candle['high']
    low_price = candle['low']
    # Check if the candlestick is a Doji
    is_doji = abs(open_price - close_price) / (high_price - low_price) < 0.1 if (high_price - low_price) > 0 else False
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
        df_tech['macd'] = ta.trend.macd_diff(df_tech['close'])
        # Calculate RSI
        df_tech['rsi'] = ta.momentum.rsi(df_tech['close'], window=14)
        # Calculate Stochastic Oscillator
        df_tech['stochastic-K'] = ta.momentum.stoch(df_tech['high'], df_tech['low'], df_tech['close'], window=14, smooth_window=3)
        df_tech['stochastic-D'] = df_tech['stochastic-K'].rolling(3).mean()
        # Calculate EMA
        df_tech['ema'] = df_tech['close'].ewm(span=14, adjust=False).mean()
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
analyzed_df = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume'])
analyzed_df['resistance'] = np.nan
analyzed_df['support'] = np.nan
analyzed_df['macd'] = np.nan
analyzed_df['rsi'] = np.nan
analyzed_df['ema'] = np.nan
analyzed_df['stochastic-D'] = np.nan
analyzed_df['stochastic-K'] = np.nan

for index, row in df.iterrows():
    analyzed_df = df.iloc[0:index+1].copy()

    if len(analyzed_df) > 15:
        analyzed_df = find_extremum(analyzed_df, window=10)
        analyzed_df = apply_technicals(analyzed_df)      
    # Print the latest processed row
    # print("analyzed data INDEX =========> ",index, " row: ",row)
    # print("analyzed data =========> ",analyzed_df)
    # print(tabulate(analyzed_df.tail(), headers='keys', tablefmt='psql', showindex=True, floatfmt=".4f"))
    # print("analyzed data =========> ",row_df['resistance'],row_df['support'])
    save_data(row)
    time.sleep(1)

# Combine all processed rows into final DataFrame
# analyzed_df = pd.concat(processed_rows)
# save_data(analyzed_df)
