# Import packages
from dash import Dash, html, dash_table, dcc
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from binance.client import Client
import ta
import os
import sys

# GENERJET BINANCE ==>
# GENERJET API KEY and SECRET
api_key = os.getenv('binance_key')
api_secret = os.getenv('binance_secret')
client = Client(api_key, api_secret)
# ======== setting overall signal values to variables ====
currency = 'ETHUSDT'

# fetch new data
# ====== get data function ======
def fetchCryptoData(symbol, timePeriod ,lookback, ago='days ago UTC'):
    df = pd.DataFrame(client.get_historical_klines(symbol, timePeriod, lookback + ago ))
    df = df.iloc[:,:6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    # df['Time'] = pd.to_datetime(df['Time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M')
    df.Time = pd.to_datetime(df.Time, unit='ms')
    df.set_index('Time', inplace=True)
    print(df.tail(10))
    return df

# sqlite-aas data unshina
DB_NAME = '../tamir_crypto_data.db'
conn = sqlite3.connect(DB_NAME)
query = "SELECT * FROM crypto_data ORDER BY time DESC LIMIT 100"
df = pd.read_sql_query(query, conn)
conn.close()

# get new data
symbol = 'ETHUSDT'
timePeriod = '5m'
lookback = '60'
df = fetchCryptoData(symbol, timePeriod, lookback )

# =========== extremum ===============
def find_extremum(df):
    window = 100  # Use the last 100 data points for rolling calculation
    # df['resistance'] = df['high'].rolling(window=window, min_periods=1).max()
    # df['support'] = df['low'].rolling(window=window, min_periods=1).min()
    resistances = df[df.High == df.High.rolling(10, center=True).max()].High
    resistance_mean = resistances.max()
    df['resistance'] = resistance_mean
    supports = df[df.Low == df.Low.rolling(window, center=True).min()].Low
    support_mean = supports.min()
    df['support'] = support_mean
    return df
 
 # =========== TA technical analysis ===============
def applytechnicals(df):
    # window for 14 days and smooth window for 3days
    df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close, window=14)
    df['macd'] = ta.trend.macd_diff(df.Close)
    df['ema'] = df.iloc[:,0].ewm(span=14,adjust=False).mean()
    df.dropna(inplace=True)
    return df
# Initialize the app ============ VIZUALIZE ============
app = Dash()
df = find_extremum(df)
df = applytechnicals(df)
print(df.tail(10))

# Convert columns to numeric
df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].apply(pd.to_numeric)

# Create candlestick chart
fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close']
)])


# App layout
app.layout = [
    html.Div(children='Крипто арилжааны автомат бот 自動化'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    dcc.Graph(figure=fig),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0)
]

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
