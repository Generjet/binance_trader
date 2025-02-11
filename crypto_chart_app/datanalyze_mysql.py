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
# ======================== NEW Technical Analysis Functions ========================
def support_resistance_range(df, price_range=5):
    # # Calculate resistance levels
    # resistance_range = abs(df['resistance'] - df['high'])
    # # Calculate support levels
    # support_range = abs(df['support'] - df['low'])
    # Add the new columns to the DataFrame
    df['near_support'] = df.apply(lambda row: row['low'] if abs(row['support'] - row['low']) <= price_range else None, axis=1)
    df['near_resistance'] = df.apply(lambda row: row['high'] if abs(row['resistance'] - row['high']) <= price_range else None, axis=1)
    return df

# ======================== OLD Technical Analysis Functions ========================
# def support_resistance_range(df, price_range=5):
#     # Calculate resistance levels
#     resistance_upper_range = df['resistance'] + price_range
#     resistance_lower_range = df['resistance'] - price_range
#     # Calculate support levels
#     support_upper_range = df['support'] + price_range
#     support_lower_range = df['support'] - price_range
#     # check if the current price is within the support range
#     is_near_support = (df['low'] >= support_lower_range) & (df['low'] <= support_upper_range)
#     # check if the current price is within the resistance range
#     is_near_resistance = (df['high'] >= resistance_lower_range) & (df['high'] <= resistance_upper_range)
#     # Add the new columns to the DataFrame
#     df['near_support'] = df.apply(lambda row: row['low'] if row['low'] >= row['support'] - price_range and row['low'] <= row['support'] + price_range else None, axis=1)
#     df['near_resistance'] = df.apply(lambda row: row['high'] if row['high'] >= row['resistance'] - price_range and row['high'] <= row['resistance'] + price_range else None, axis=1)
#     return df

def find_extremum(df, window=10):
    resistances = df[(df.high.shift(1) < df.high) & (df.high.shift(-1) < df.high)].dropna().high
    resistance_points = resistances.sort_values(ascending=False).head(2)
    
    if len(resistance_points) == 2:
        x1, x2 = resistance_points.index[0], resistance_points.index[1]
        y1, y2 = resistance_points.iloc[0], resistance_points.iloc[1]
        slope_resistance = (y2 - y1) / (x2 - x1)
        intercept_resistance = y1 - slope_resistance * x1
        df['resistance'] = slope_resistance * df.index + intercept_resistance
    else:
        df['resistance'] = np.nan

    supports = df[(df.low == df.low.rolling(window, center=True).min()) & 
                  (df.close.shift(1) < df.open.shift(1)) & 
                  (df.close > df.open)].dropna().low
    support_points = supports.sort_values(ascending=True).tail(2)
    
    if len(support_points) == 2:
        x1, x2 = support_points.index[0], support_points.index[1]
        y1, y2 = support_points.iloc[0], support_points.iloc[1]
        slope_support = (y2 - y1) / (x2 - x1)
        intercept_support = y1 - slope_support * x1
        df['support'] = slope_support * df.index + intercept_support
    else:
        df['support'] = np.nan

    return df

# Trend reversal patterns
def detect_engulfing_pattern(df):
    if len(df) < 4:
        df['engulfing'] = 'no'
        df['reversal'] = 'no'
        df['doji'] = 'no'
        return df

    df['engulfing'] = 'no'
    df['reversal'] = 'no'
    df['doji'] = 'no'
    for i in range(3, len(df)):
        prev_candle = df.iloc[i-1]
        current_candle = df.iloc[i]
        prev_trend = df.iloc[i-2]['close'] - df.iloc[i-3]['close']
        # prev_trend negative means downtrend, positive means uptrend

        doji_type = doji_check(prev_candle)
        reversal = reversal_pattern(prev_candle)
        df.at[i-1, 'reversal'] = reversal  # Save the reversal pattern in the DataFrame
        df.at[i-1, 'doji'] = doji_type  # Save the doji type in the DataFrame
        # ======================== NEW CODE ========================
        if doji_type == "bullish_doji" or reversal == "bullish_hammer" or reversal == "bullish_inverted_hammer":
            if prev_trend < 0 and current_candle['close'] > current_candle['open'] and current_candle['close'] > prev_candle['close'] and current_candle['open'] > prev_candle['low']:
                df.at[i, 'engulfing'] = 'bullish'
        elif doji_type == "bearish_doji" or reversal == "bearish_shooting_star" or reversal == "bearish_hanging_man":
            if prev_trend > 0 and current_candle['close'] < current_candle['open'] and current_candle['close'] < prev_candle['close'] and current_candle['open'] < prev_candle['high']:
                df.at[i, 'engulfing'] = 'bearish'
        # ======================== OLD CODE ========================
        # if doji_type == "bullish_doji" or reversal == "bullish_hammer" or reversal == "bullish_inverted_hammer":
        #     if prev_trend < 0 and current_candle['close'] > current_candle['open'] and current_candle['close'] > prev_candle['high'] and current_candle['open'] < prev_candle['low']:
        #         df.at[i, 'engulfing'] = 'bullish'
        # elif doji_type == "bearish_doji" or reversal == "bearish_shooting_star" or reversal == "bearish_hanging_man":
        #     if prev_trend > 0 and current_candle['close'] < current_candle['open'] and current_candle['close'] < prev_candle['low'] and current_candle['open'] > prev_candle['high']:
        #         df.at[i, 'engulfing'] = 'bearish'

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

def boilinger_band_check(df, window=20, num_std_dev=2, price_range=5):
    df['bb_middle'] = df['close'].rolling(window=window).mean()
    df['bb_std'] = df['close'].rolling(window=window).std()
    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * num_std_dev)
    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * num_std_dev)
    df['bb_trend'] = 'wait'
    df['bb_signal'] = 'wait'
    
    for i in range(window, len(df)):
        if df['close'].iloc[i] > df['bb_upper'].iloc[i]:
            df.at[df.index[i], 'bb_trend'] = 'up'
            df.at[df.index[i], 'bb_signal'] = 'sell'
        elif df['close'].iloc[i] < df['bb_lower'].iloc[i]:
            df.at[df.index[i], 'bb_trend'] = 'down'
            df.at[df.index[i], 'bb_signal'] = 'buy'
        else:
            df.at[df.index[i], 'bb_trend'] = 'sideways'
            df.at[df.index[i], 'bb_signal'] = 'wait'
    # ==== calculate near support and resistance levels of boilinger bands ====
    # df['near_bb_support'] = df.apply(lambda row: row['low'] if abs(row['bb_lower'] - row['low']) <= price_range else None, axis=1)
    # df['near_bb_resistance'] = df.apply(lambda row: row['high'] if abs(row['bb_upper'] - row['high']) <= price_range else None, axis=1)
    # ================= new signal ===========================
    df['near_bb_support'] = df.apply(lambda row: row['low'] if (abs(row['bb_lower'] - row['low']) <= price_range or (row['rsi_trade'] == 'buy' and row['stochastic_trade'] == 'buy')) else None, axis=1)
    df['near_bb_resistance'] = df.apply(lambda row: row['high'] if (abs(row['bb_upper'] - row['high']) <= price_range or (row['rsi_trade'] == 'sell' and row['stochastic_trade'] == 'sell')) else None, axis=1)
    return df

def apply_technicals(df):
    if len(df) < 14:  # Minimum required length for calculations
        return df    
    df_tech = df.copy()
    try:
        # Calculate MACD
        # Calculate short and long EMA
        short_ema = df_tech['close'].ewm(span=12, adjust=False).mean()
        long_ema = df_tech['close'].ewm(span=32, adjust=False).mean()
        # Calculate MACD and MACD Signal
        # df_tech['macd'] = ta.trend.macd(df_tech['close'])
        # df_tech['macd_signal'] = ta.trend.macd_signal(df_tech['close'])
        # df_tech['macd_hist'] = ta.trend.macd_diff(df_tech['close'])
        # Calculate RSI
        df_tech['rsi'] = ta.momentum.rsi(df_tech['close'], window=14)
        # Calculate Stochastic Oscillator
        df_tech['stochastic-K'] = ta.momentum.stoch(df_tech['high'], df_tech['low'], df_tech['close'], window=14, smooth_window=3)
        df_tech['stochastic-D'] = df_tech['stochastic-K'].rolling(3).mean()
        # Calculate EMA
        df_tech['ema'] = df_tech['close'].ewm(span=14, adjust=False).mean()
        df_tech = boilinger_band_check(df_tech, 20, 2, 10) # boilinger_band_check(df, window=20, num_std_dev=2, price_range=5):
        # Fill NaN values with previous values
        df_tech = df_tech.ffill()
    except Exception as e:
        print(f"Error in technical analysis: {e}")
        return df
    
    return df_tech

# ===================== Trade analyze functions =====================
def trade_analyze(analyzed_df):
    # Initialize the trade columns with 'wait'
    analyzed_df['macd_trade'] = 'wait'
    analyzed_df['rsi_trade'] = 'wait'
    analyzed_df['stochastic_trade'] = 'wait'
    analyzed_df['channel_trade'] = 'wait'
    analyzed_df['trade'] = 'wait'  # Add the new 'trade' column

    # Iterate over the DataFrame to determine trade signals
    for i in range(1, len(analyzed_df)):
        # # MACD trade signals
        # if analyzed_df['macd'].iloc[i] > analyzed_df['macd_signal'].iloc[i] and analyzed_df['macd'].iloc[i-1] <= analyzed_df['macd_signal'].iloc[i-1]:
        #     analyzed_df.at[analyzed_df.index[i], 'macd_trade'] = 'buy'
        # elif analyzed_df['macd'].iloc[i] < analyzed_df['macd_signal'].iloc[i] and analyzed_df['macd'].iloc[i-1] >= analyzed_df['macd_signal'].iloc[i-1]:
        #     analyzed_df.at[analyzed_df.index[i], 'macd_trade'] = 'sell'
        
        # RSI trade signals
        if analyzed_df['rsi'].iloc[i] < 30:
            analyzed_df.at[analyzed_df.index[i], 'rsi_trade'] = 'buy'
        elif analyzed_df['rsi'].iloc[i] > 70:
            analyzed_df.at[analyzed_df.index[i], 'rsi_trade'] = 'sell'
        
        # Stochastic oscillator trade signals
        if analyzed_df['stochastic-K'].iloc[i] < 20 and analyzed_df['stochastic-D'].iloc[i] < 20:
            analyzed_df.at[analyzed_df.index[i], 'stochastic_trade'] = 'buy'
        elif analyzed_df['stochastic-K'].iloc[i] > 80 and analyzed_df['stochastic-D'].iloc[i] > 80:
            analyzed_df.at[analyzed_df.index[i], 'stochastic_trade'] = 'sell'
        
        # Channel trade signals
        if not pd.isna(analyzed_df['near_support'].iloc[i]):
            analyzed_df.at[analyzed_df.index[i], 'channel_trade'] = 'buy'
        elif not pd.isna(analyzed_df['near_resistance'].iloc[i]):
            analyzed_df.at[analyzed_df.index[i], 'channel_trade'] = 'sell'
        
        # Determine overall trade signal
        if not pd.isna(analyzed_df['near_bb_support'].iloc[i]) and analyzed_df['rsi_trade'].iloc[i] == 'buy' and analyzed_df['stochastic_trade'].iloc[i] == 'buy':
            analyzed_df.at[analyzed_df.index[i], 'trade'] = 'buy'
        elif not pd.isna(analyzed_df['near_bb_resistance'].iloc[i]) and analyzed_df['rsi_trade'].iloc[i] == 'sell' and analyzed_df['stochastic_trade'].iloc[i] == 'sell':
            analyzed_df.at[analyzed_df.index[i], 'trade'] = 'sell'
    
    return analyzed_df

# ===================== EXECUTE =====================
symbol = 'ETHUSDT'
timePeriod = '1h'
lookback = 90000000
df = fetchCryptoData(symbol, timePeriod, lookback)
# ============= UNTИЛ HERE ALL WORKS =============
# Create a list to collect processed rows
analyzed_df = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume','support', 'resistance','macd','macd_signal','macd_hist','rsi','stochastic-K','stochastic-D','ema','bb_middle','bb_std','bb_upper','bb_lower','bb_trend','bb_signal','near_support','near_resistance','engulfing','reversal','doji','macd_trade','rsi_trade','stochastic_trade','channel_trade','near_bb_support','near_bb_resistance'])
# Add the necessary columns if they do not exist
if 'support' not in df.columns:
    df['support'] = np.nan
if 'resistance' not in df.columns:
    df['resistance'] = np.nan
if 'macd' not in df.columns:
    df['macd'] = np.nan
if 'macd_signal' not in df.columns:
    df['macd_signal'] = np.nan
if 'macd_hist' not in df.columns:
    df['macd_hist'] = np.nan
if 'rsi' not in df.columns:
    df['rsi'] = np.nan
if 'stochastic-K' not in df.columns:
    df['stochastic-K'] = np.nan
if 'stochastic-D' not in df.columns:
    df['stochastic-D'] = np.nan
if 'ema' not in df.columns:
    df['ema'] = np.nan
if 'bb_middle' not in df.columns:
    df['bb_middle'] = np.nan
if 'bb_std' not in df.columns:
    df['bb_std'] = np.nan
if 'bb_upper' not in df.columns:
    df['bb_upper'] = np.nan
if 'bb_lower' not in df.columns:
    df['bb_lower'] = np.nan
if 'bb_trend' not in df.columns:
    df['bb_trend'] = np.nan
if 'bb_signal' not in df.columns:
    df['bb_signal'] = np.nan
if 'near_support' not in df.columns:
    df['near_support'] = np.nan
if 'near_resistance' not in df.columns:
    df['near_resistance'] = np.nan
if 'engulfing' not in df.columns:
    df['engulfing'] = 'no'
if 'reversal' not in df.columns:
    df['reversal'] = 'no'
if 'doji' not in df.columns:
    df['doji'] = 'no'
if 'macd_trade' not in df.columns:
    df['macd_trade'] = 'wait'
if 'rsi_trade' not in df.columns:
    df['rsi_trade'] = 'wait'
if 'stochastic_trade' not in df.columns:
    df['stochastic_trade'] = 'wait'
if 'channel_trade' not in df.columns:
    df['channel_trade'] = 'wait'
if 'near_bb_support' not in df.columns:
    df['near_bb_support'] = np.nan
if 'near_bb_resistance' not in df.columns:
    df['near_bb_resistance'] = np.nan

for index, row in df.iterrows():
    # for index, row in df.iterrows(): нь historical data-г нэг нэгээр авч байгаа simulation
    # Эндээс эхлээд анализ хийж шалгах
    # ХАМГИЙН СҮҮЛЧИЙН 20 МЭДЭЭЛЭЛ -> analyzed_df = df.tail(20)
    analyzed_df = df.iloc[0:index+1].copy()
    analyzed_df = analyzed_df.tail(20)
    # print("analyzed data =========> ",analyzed_df)
    if len(analyzed_df) > 4:
        analyzed_df = find_extremum(analyzed_df, 20)
    if len(analyzed_df) > 4: # call support_resistance_range after find_extremum
        analyzed_df = support_resistance_range(analyzed_df, 10)
        analyzed_df = detect_engulfing_pattern(analyzed_df)
    if len(analyzed_df) > 30:
        analyzed_df = apply_technicals(analyzed_df)
        analyzed_df = trade_analyze(analyzed_df)
        print("\nAnalyzed data after technicals:")
        print("\nMACD Data:")
        print(tabulate(analyzed_df[['time', 'engulfing','macd_hist', 'macd_trade', 'rsi_trade', 'stochastic_trade', 'channel_trade', 'bb_trend', 'bb_signal']].tail(4), headers='keys', tablefmt='psql', floatfmt='.4f'))
    # print(tabulate(analyzed_df.tail(), headers='keys', tablefmt='psql', floatfmt='.4f'))

    create_database_if_not_exists()
    print("Database created")
    # update_db(row)
    latest_row = analyzed_df.iloc[-1]

    update_db(latest_row)
    time.sleep(2)
    print("Chart saved to crypto_chart_app/chart.png")

    time.sleep(2)
