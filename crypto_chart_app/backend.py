from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import pandas as pd
import time
from binance.client import Client
import os
import ta

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

api_key = os.getenv('binance_key')
api_secret = os.getenv('binance_secret')
client = Client(api_key, api_secret)

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
    max_points = df['High'].nlargest(2)
    if len(max_points) < 2:
        return df
    slope = (max_points.iloc[1] - max_points.iloc[0]) / (max_points.index[1] - max_points.index[0]).days
    df['resistance'] = max_points.iloc[1] + slope * (df.index - max_points.index[1]).days
    return df

def applytechnicals(df):
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    df['K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'], window=14, smooth_window=3)
    df['D'] = df['K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df['Close'], window=14)
    return df

@socketio.on('start_analysis')
def handle_start_analysis(data):
    symbol = data.get('symbol', 'ETHUSDT')
    timePeriod = data.get('timePeriod', '1h')
    lookback = data.get('lookback', 30)
    analyzed_df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df = fetchCryptoData(symbol, timePeriod, lookback)
    for index, row in df.iterrows():
        analyzed_df = analyzed_df.append(row)
        analyzed_df = find_extremum(analyzed_df)
        analyzed_df = applytechnicals(analyzed_df)
        socketio.emit('update_data', analyzed_df.tail(1).to_dict('records'))
        time.sleep(1)

@app.route('/')
def index():
    return render_template('/templates/index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)