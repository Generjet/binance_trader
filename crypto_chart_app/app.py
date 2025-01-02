from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import ta
import sqlite3
import plotly.graph_objects as go

app = Flask(__name__, static_folder='static')
CORS(app)

DB_NAME = 'tamir_crypto_data.db'

def find_extremum(df):
    window = 100  # Use the last 100 data points for rolling calculation
    # df['resistance'] = df['high'].rolling(window=window, min_periods=1).max()
    # df['support'] = df['low'].rolling(window=window, min_periods=1).min()
    resistances = df[df.high == df.high.rolling(10, center=True).max()].high
    resistance_mean = resistances.max()
    df['resistance'] = resistance_mean
    supports = df[df.low == df.low.rolling(window, center=True).min()].low
    support_mean = supports.min()
    df['support'] = support_mean
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

def calculate_signal(data):
    if len(data) < 20:
        return "hold"  # Not enough data for calculation

    # Calculate 20-period moving average
    ma20 = sum(d['close'] for d in data[-20:]) / 20

    current_close = data[-1]['close']

    if current_close > ma20:
        return "buy"
    elif current_close < ma20:
        return "sell"
    else:
        return "hold"

def apply_technicals(df):
    # Calculate MACD
    df['macd'] = ta.trend.macd_diff(df['close'])

    # Calculate RSI
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)

    # Calculate Stochastic Oscillator
    df['%K'] = ta.momentum.stoch(df['high'], df['low'], df['close'], window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()

    # Rename the columns
    df.rename(columns={'%K': 'stochastic-K', '%D': 'stochastic-D'}, inplace=True)

    # Calculate EMA
    df['ema'] = df['close'].ewm(span=14, adjust=False).mean()

    df.dropna(inplace=True)
    return df

def save_data(df):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crypto_data (
            time TEXT PRIMARY KEY,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            macd REAL,
            rsi REAL,
            "stochastic-K" REAL,
            "stochastic-D" REAL,
            ema REAL,
            support REAL,
            resistance REAL,
            is_doji INTEGER,
            signal TEXT
        )
    ''')
    
    # Handle schema migration if necessary (add new columns)
    existing_columns = [row[1] for row in cursor.execute('PRAGMA table_info(crypto_data)')]
    new_columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'macd', 'rsi', 'stochastic-K', 'stochastic-D', 'ema', 'support', 'resistance', 'is_doji', 'signal']
    for col in new_columns:
        if col not in existing_columns:
            print(f"Adding new column: {col}")
            cursor.execute(f'ALTER TABLE crypto_data ADD COLUMN "{col}" REAL')

    # Insert data, replacing if time already exists
    for index, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO crypto_data (time, open, high, low, close, volume, macd, rsi, "stochastic-K", "stochastic-D", ema, support, resistance, is_doji, signal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (row['time'], row['open'], row['high'], row['low'], row['close'], row['volume'], row['macd'], row['rsi'], row['stochastic-K'], row['stochastic-D'], row['ema'], row['support'], row['resistance'], 0, 'hold'))
        except sqlite3.OperationalError as e:
            print(f"Error inserting data: {e}")

    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM crypto_data ORDER BY time DESC LIMIT 100"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return "No data found", 404

    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])

    chart_html = fig.to_html(full_html=False)
    table_html = df.to_html(classes='data', index=False)

    return render_template('index.html', chart_html=chart_html, table_data=table_html)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
