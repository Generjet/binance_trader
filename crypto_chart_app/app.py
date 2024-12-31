from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import requests
import time
import threading
import statistics
import pandas as pd
import ta
import sqlite3

app = Flask(__name__, static_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

current_data = []
data_lock = threading.Lock()

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

def fetch_and_emit_data(symbol, interval):
    global current_data
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=500'
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            formatted_data = [{
                'time': d[0] / 1000,
                'open': float(d[1]),
                'high': float(d[2]),
                'low': float(d[3]),
                'close': float(d[4]),
                'volume': float(d[5])
            } for d in data]

            df = pd.DataFrame(formatted_data)
            # Convert time to readable format
            # df.set_index('time', inplace=True)
            # df.index = pd.to_datetime(df.index, unit='ms')
            df['time'] = pd.to_datetime(df['time'], unit='s').dt.strftime('%Y-%m-%d %H:%M')
            # print(df.tail(5))

            with data_lock:
                current_data = []
                for index, row in df.iterrows():
                    current_data.append(row)
                    if len(current_data) > 10:
                        analyzedf = find_extremum(current_data)
                        analyzedf = apply_technicals(analyzedf)
                    else:
                        analyzedf = []
                                
                    save_data(analyzedf)
                    # is_doji = is_bullish_doji(row)
                    signal = calculate_signal(analyzedf)
                    
                    # print(f"Emitting data: {row['support']} time is {row['time']}")
                    print(analyzedf)
                    # socketio.emit('update_data', {
                    #     'data': row,
                    #     # 'is_doji': is_doji,
                    #     'signal': signal,
                    #     'support': analyzedf['support'],
                    #     'resistance': analyzedf['resistance'],
                    #     'macd': analyzedf['macd'],
                    #     'rsi': analyzedf['rsi'],
                    #     'stochastic-K': analyzedf['stochastic-K'],
                    #     'stochastic-D': analyzedf['stochastic-D'],
                    #     'ema': analyzedf['ema']
                    # })
                    time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f'Error fetching data: {e}')
            time.sleep(10)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1h')
    
    thread = threading.Thread(target=fetch_and_emit_data, args=(symbol, interval))
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    with open('crypto_chart_app/index.html', 'r') as f:
        return f.read()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
