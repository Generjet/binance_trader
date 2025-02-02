from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import ta
import os
import time
import sys
import yfinance as yf
from binance.client import Client
import plotly.graph_objects as go
import numpy as np
from tabulate import tabulate
from save2mysql import create_database_if_not_exists, update_db, db, AnalyzedData

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Tamir4578@localhost/portalblog_dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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
    # Construct absolute path for CSV in the existing 'data' directory
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'crypto_price.csv')
    # Save DataFrame to CSV
    df.to_csv(csv_path, index=False)
    # Keep only necessary columns
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
    return df

def support_resistance_range(df, price_range=10):
    # Calculate resistance levels
    resistance_upper_range = df['resistance'] + price_range
    resistance_lower_range = df['resistance'] - price_range
    # Calculate support levels
    support_upper_range = df['support'] + price_range
    support_lower_range = df['support'] - price_range
    # check if the current price is within the support range
    is_near_support = (df['close'] >= support_lower_range) & (df['close'] <= support_upper_range)
    # check if the current price is within the resistance range
    is_near_resistance = (df['close'] >= resistance_lower_range) & (df['close'] <= resistance_upper_range)
    # Add the new columns to the DataFrame
    df['near_support'] = is_near_support
    df['near_resistance'] = is_near_resistance
    return df

def find_extremum(df, window=4):
    # print("GOT data for finding EXTREMUMS: ",df)
    # resistances = df[df.high == df.high.rolling(window, center=True).max()].dropna().high
    resistances = df[df.high == df.high.rolling(window, center=True).max()].high
    # resistance_points = resistances.sort_values(ascending=True).tail(2)
    resistance_mean = resistances.max()
    df['resistance'] = resistance_mean
    supports = df[df.low == df.low.rolling(window, center=True).min()].low
    support_mean = supports.min()
    df['support'] = support_mean
    print("AFTER EXTREMUMS: ",df)
    return df

# Trend reversal patterns
def detect_engulfing_pattern(df):
    if len(df) < 4:
        df['engulfing'] = 'no'
        df['reversal_pattern'] = 'no'
        df['doji'] = 'no'
        return df

    df['engulfing'] = 'no'
    df['reversal_pattern'] = 'no'
    df['doji'] = 'no'
    for i in range(3, len(df)):
        prev_candle = df.iloc[i-1]
        current_candle = df.iloc[i]
        prev_trend = df.iloc[i-2]['close'] - df.iloc[i-3]['close']
        # prev_trend negative means downtrend, positive means uptrend

        doji_type = doji_check(prev_candle)
        reversal = reversal_pattern(prev_candle)
        df.at[i-1, 'reversal_pattern'] = reversal  # Save the reversal pattern in the DataFrame
        df.at[i-1, 'doji'] = doji_type  # Save the doji type in the DataFrame
        if doji_type == "bullish_doji" or reversal == "bullish_hammer" or reversal == "bullish_inverted_hammer":
            if prev_trend < 0 and current_candle['close'] > current_candle['open'] and current_candle['close'] > prev_candle['high'] and current_candle['open'] < prev_candle['low']:
                df.at[i, 'engulfing'] = 'bullish'
        elif doji_type == "bearish_doji" or reversal == "bearish_shooting_star" or reversal == "bearish_hanging_man":
            if prev_trend > 0 and current_candle['close'] < current_candle['open'] and current_candle['close'] < prev_candle['low'] and current_candle['open'] > prev_candle['high']:
                df.at[i, 'engulfing'] = 'bearish'

    return df

def doji_check(candle):
    open_price = candle['open']
    close_price = candle['close']
    high_price = candle['high']
    low_price = candle['low']
    # Check if the candlestick is a Doji
    is_doji = abs(open_price - close_price) / (high_price - low_price) < 0.1 if (high_price - low_price) > 0 else False
    if not is_doji:
        return "no"
    # Check if the Doji is bullish or bearish
    if close_price > open_price:
        return "bullish_doji"
    elif open_price > close_price:
        return "bearish_doji"
    return "no"

def reversal_pattern(candle):
    open_price = candle['open']
    close_price = candle['close']
    high_price = candle['high']
    low_price = candle['low']
    body_length = abs(close_price - open_price)
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price

    # Bullish patterns
    if body_length <= (high_price - low_price) * 0.3:
        if lower_shadow >= 2 * body_length and upper_shadow <= body_length:
            if close_price > open_price:
                return "bullish_hammer"
            elif open_price > close_price:
                return "bullish_inverted_hammer"

    # Bearish patterns
    if body_length <= (high_price - low_price) * 0.3:
        if upper_shadow >= 2 * body_length and lower_shadow <= body_length:
            if open_price > close_price:
                return "bearish_shooting_star"
            elif close_price > open_price:
                return "bearish_hanging_man"

    return "no"
git 
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
        df_tech = df_tech.ffill()
    except Exception as e:
        print(f"Error in technical analysis: {e}")
        return df
    
    return df_tech
# ===================== EXECUTE =====================
symbol = 'ETHUSDT'
timePeriod = '1h'
lookback = 100
df = fetchCryptoData(symbol, timePeriod, lookback)
# ============= UNTIL HERE ALL WORKS =============
# Create a list to collect processed rows
analyzed_df = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume','support', 'resistance'])
# Add the necessary columns if they do not exist
if 'support' not in df.columns:
    df['support'] = np.nan
if 'resistance' not in df.columns:
    df['resistance'] = np.nan

for index, row in df.iterrows():
    # for index, row in df.iterrows(): нь historical data-г нэг нэгээр авч байгаа simulation
    # Эндээс эхлээд анализ хийж шалгах
    # ХАМГИЙН СҮҮЛЧИЙН 20 МЭДЭЭЛЭЛ -> analyzed_df = df.tail(20)
    analyzed_df = df.iloc[0:index+1].copy()
    analyzed_df = analyzed_df.tail(20)
    # print("analyzed data =========> ",analyzed_df)
    if len(analyzed_df) > 4:
        analyzed_df = find_extremum(analyzed_df, 4)
    if len(analyzed_df) > 4: # call support_resistance_range after find_extremum
        analyzed_df = support_resistance_range(analyzed_df, 10)
    if len(analyzed_df) > 15:
        analyzed_df = apply_technicals(analyzed_df)
        print("\nAnalyzed data after technicals:")
    print(tabulate(analyzed_df.tail(), headers='keys', tablefmt='psql', floatfmt='.4f'))
    create_database_if_not_exists()
    print("Database created")
    # update_db(row)
    latest_row = analyzed_df.iloc[-1]

    # Calculate near support/resistance flags
    pip_value = 0.20  # 20 pips for ETH/USDT - adjust as needed
    latest_row['near_support'] = abs(latest_row['close'] - latest_row['support']) <= pip_value
    latest_row['near_resistance'] = abs(latest_row['close'] - latest_row['resistance']) <= pip_value

    update_db(latest_row)
    time.sleep(2)
    
    # Plotting logic
    if len(analyzed_df) > 5:
        fig = go.Figure(data=[go.Candlestick(
            x=analyzed_df['time'],
            open=analyzed_df['open'],
            high=analyzed_df['high'],
            low=analyzed_df['low'],
            close=analyzed_df['close']
        )])

        # pip_value = 0.20  # 20 pips for ETH/USDT - adjust as needed
        # near_support = abs(analyzed_df['close'] - analyzed_df['support']) <= pip_value
        # near_resistance = abs(analyzed_df['close'] - analyzed_df['resistance']) <= pip_value

        fig.add_trace(go.Scatter(
            x=analyzed_df[analyzed_df['near_support'] == True].index, # Filter near_support == True
            y=analyzed_df.loc[analyzed_df['near_support'] == True, 'close'],
            mode='markers',
            marker=dict(color='red', size=8),
            name='Near Support (20 pips)'
        ))

        fig.add_trace(go.Scatter(
            x=analyzed_df[analyzed_df['near_resistance'] == True].index, # Filter near_resistance == True
            y=analyzed_df.loc[analyzed_df['near_resistance'] == True, 'close'],
            mode='markers',
            marker=dict(color='yellow', size=8),
            name='Near Resistance (20 pips)'
        ))

        fig.write_image("chart.png")
        print("Chart saved to crypto_chart_app/chart.png")

    time.sleep(2)
