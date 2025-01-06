import pandas as pd
import ta
import os
import time
import sys
import yfinance as yf
import sqlite3
import plotly.graph_objects as go

DB_NAME = '../tamir_crypto_data.db'


def fetchCryptoData(symbol, timePeriod, lookback, ago='days ago UTC'):
    # Convert Binance-like period to yfinance interval
    interval_map = {
        '1h': '1h',
        '1d': '1d',
        '1m': '1m',
        '5m': '5m',
        '15m': '15m'
    }
    
    # Get data from yfinance
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=f"{lookback}d", interval=interval_map.get(timePeriod, '1h'))
    
    # Reset index and rename columns to match existing code
    df = df.reset_index()
    df.rename(columns={
        'Datetime': 'Time',
        'Open': 'Open',
        'High': 'High',
        'Low': 'Low',
        'Close': 'Close',
        'Volume': 'Volume'
    }, inplace=True)
    
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
processed_rows = []

for index, row in df.iterrows():
    print(index)
    # Create a single-row DataFrame
    row_df = pd.DataFrame([row])    
    # Apply transformations
    analyzed_df = pd.concat([analyzed_df, row_df], ignore_index=True)
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
