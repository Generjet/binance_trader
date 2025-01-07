import pandas as pd
import ta
import os
import time
import sys
import yfinance as yf
import sqlite3
from binance.client import Client
import plotly.graph_objects as go

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
    
    # Keep only necessary columns
    df = df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
    
    return df

def find_extremum(df):
    window = 100  # Use the last 100 data points for rolling calculation
    resistances = df[df.High == df.High.rolling(10, center=True).max()].High
    resistance_mean = resistances.max()
    df['resistance'] = resistance_mean
    supports = df[df.Low == df.Low.rolling(window, center=True).min()].Low
    support_mean = supports.min()
    df['support'] = support_mean
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
    # Calculate MACD
    df['macd'] = ta.trend.macd_diff(df['Close'])
    # Calculate RSI
    df['rsi'] = ta.momentum.rsi(df['Close'], window=14)
    # Calculate Stochastic Oscillator
    df['%K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'], window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    # Rename the columns
    df.rename(columns={'%K': 'stochastic-K', '%D': 'stochastic-D'}, inplace=True)
    # Calculate EMA
    df['ema'] = df['Close'].ewm(span=14, adjust=False).mean()
    df.dropna(inplace=True)
    return df
# ===================== EXECUTE =====================
symbol = 'ETHUSDT'
timePeriod = '1h'
lookback = 110
df = fetchCryptoData(symbol, timePeriod, lookback)
# ndf = find_extremum(df)
# ndf = apply_technicals(ndf)
# print(ndf)
# ============= UNTIL HERE ALL WORKS =============
# Create a list to collect processed rows
analyzed_df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

for index, row in df.iterrows():
    print(index)
    # Create a single-row DataFrame
    row_df = pd.DataFrame([row])
    # Append using concat
    # analyzed_df = pd.concat([analyzed_df, row_df], ignore_index=True)
    # Update analyzed_df with all data up to current index
    analyzed_df = df.iloc[0:index+1].copy()
    if len(analyzed_df) > 15:
        analyzed_df = find_extremum(analyzed_df)
        analyzed_df = apply_technicals(analyzed_df)    
    # # Append processed row to list
    # processed_rows.append(row_df)
    
    # Print the latest processed row
    print("analyzed data =========> ",analyzed_df)
    # print("analyzed data =========> ",analyzed_df['resistance'],analyzed_df['support'])
    # print("analyzed data =========> ",row_df['resistance'],row_df['support'])
    time.sleep(1)

# Combine all processed rows into final DataFrame
# analyzed_df = pd.concat(processed_rows)
