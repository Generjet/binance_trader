from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import requests
import time
import threading
import statistics
import pandas as pd
import ta

app = Flask(__name__, static_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

current_data = []
data_lock = threading.Lock()


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

    # Calculate EMA
    df['ema'] = df['close'].ewm(span=14, adjust=False).mean()

    df.dropna(inplace=True)
    return df

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
            df = find_extremum(df)
            df = apply_technicals(df)
            
            # Convert time to readable format
            df['time'] = pd.to_datetime(df['time'], unit='s').dt.strftime('%Y-%m-%d %H:%M')
            formatted_data = df.to_dict('records')

            with data_lock:
                current_data = []
                for i in range(len(formatted_data)):
                    is_doji = is_bullish_doji(formatted_data[i])
                    signal = calculate_signal(formatted_data[:i+1])
                    current_data.append(formatted_data[i])
                    print(f"Emitting data: {formatted_data[i]['support']}")
                    socketio.emit('update_data', {
                        'data': formatted_data[i],
                        'is_doji': is_doji,
                        'signal': signal,
                        'support': formatted_data[i]['support'],
                        'resistance': formatted_data[i]['resistance'],
                        'macd': formatted_data[i]['macd'],
                        'rsi': formatted_data[i]['rsi'],
                        '%K': formatted_data[i]['%K'],
                        '%D': formatted_data[i]['%D'],
                        'ema': formatted_data[i]['ema']
                    })
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

@app.route('/klines')
def get_klines():
    symbol = request.args.get('symbol')
    interval = request.args.get('interval')
    limit = 100

    if not symbol or not interval:
        return jsonify({'error': 'Missing symbol or interval'}), 400

    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'

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
        } for d in data]

        return jsonify(formatted_data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error fetching data: {e}'}), 500

@app.route('/chart')
def chart():
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1h')

    # Fetch data from Binance API (using /klines route)
    try:
        response = requests.get(f'http://localhost:5000/klines?symbol={symbol}&interval={interval}')
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return f'Error fetching data: {e}', 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
