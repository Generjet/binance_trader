import pandas as pd
import ta
import os
import time
import sys
from binance.client import Client
import sqlite3
import plotly.graph_objects as go

DB_NAME = '../tamir_crypto_data.db'

api_key = os.getenv('binance_key')
api_secret = os.getenv('binance_secret')
client = Client(api_key, api_secret)
print(client.get_account())
# sys.exit()


def fetchCryptoData(symbol, timePeriod, lookback, ago='days ago UTC'):
    lookback_str = str(lookback) + ' ' + ago
    df = pd.DataFrame(client.get_historical_klines(symbol, timePeriod, lookback_str))
    df = df.iloc[:, :6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df.set_index('Time', inplace=True)
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
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
lookback = 100
df = fetchCryptoData(symbol, timePeriod, lookback)

# Create a list to collect processed rows
processed_rows = []

for index, row in df.iterrows():
    # Create a single-row DataFrame
    row_df = pd.DataFrame([row])
    
    # Apply transformations
    row_df = find_extremum(row_df)
    row_df = apply_technicals(row_df)
    
    # Append processed row to list
    processed_rows.append(row_df)
    
    # Print the latest processed row
    print(row_df)
    time.sleep(1)

# Combine all processed rows into final DataFrame
analyzed_df = pd.concat(processed_rows)
